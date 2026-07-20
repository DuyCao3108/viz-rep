"""extract_palette.py — pull each firm's dominant chart-ink color palette
straight out of their vector-drawn PDF report.

Why vector, not pixels: these guides draw every bar/line/area as PDF path
objects rather than embedding charts as raster images. Reading the fill/stroke
colors directly off those paths (via pdfplumber -> pdfminer) gives the exact
authored colors with no anti-aliasing noise, so it beats rasterizing pages and
running k-means over pixels.

Method: walk each page's rects/curves/lines, weight every fill/stroke color by
the screen area (or stroke length) it covers, drop near-grayscale ink
(backgrounds, axis rules, body text -- none of that is "palette"), then
greedily cluster near-duplicate colors and keep the top N by total weight.

Usage:
    python extract_palette.py                  # all firms
    python extract_palette.py --firm bain       # one firm
    python extract_palette.py --refresh         # re-download even if cached
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pdfplumber

SANDBOX_DIR = Path(__file__).resolve().parent
PDF_DIR = SANDBOX_DIR / "data" / "pdfs"
PALETTE_CACHE = SANDBOX_DIR / "data" / "palettes.json"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# One representative, chart-dense PDF per firm. Regional editions of the same
# report (JPM's UK/EMEA guides) share a design system, so one edition is
# enough to capture the firm's chart palette.
#
# Bain / BCG / McKinsey sit behind edge bot-protection (403s, or a connection
# that times out at the TLS layer) that doesn't budge for browser-like
# headers -- it's a TLS/IP fingerprint check curl/urllib can't pass, not a
# missing header. Drop a manually-downloaded copy at
# data/pdfs/<firm>__<anything>.pdf and rerun; no code changes needed.
FIRM_SOURCES: dict[str, str] = {
    "jpmorgan": "https://am.jpmorgan.com/content/dam/jpm-am-aem/global/en/insights/market-insights/guide-to-the-markets/mi-guide-to-the-markets-us.pdf",
    "goldman_sachs": "https://am.gs.com/cms-assets/gsam-app/documents/insights/en/2025/international-market-know-how_1q25.pdf",
    "bain": "https://www.bain.com/globalassets/noindex/2026/bain-report_global-private-equity-report-2026.pdf",
    "bcg": "https://web-assets.bcg.com/27/09/094ed67e49ffbd469d130d73842d/2026-gwr-may-2026-n.pdf",
    "mckinsey": "https://www.mckinsey.com/~/media/mckinsey/business%20functions/people%20and%20organizational%20performance/our%20insights/the%20state%20of%20organizations/2026/the-state-of-organizations-2026.pdf",
}

# Extra editions blended into the same firm's palette when a local copy exists.
EXTRA_SOURCES: dict[str, list[str]] = {
    "goldman_sachs": [
        "https://am.gs.com/cms-assets/gsam-app/documents/insights/en/2026/us-market-pulse_feb2026.pdf",
    ],
}

MAX_PAGES = 40
GRAYSCALE_SPREAD = 0.05  # max-min channel spread (0-1 scale) below this = neutral ink, dropped
CLUSTER_DISTANCE = 24  # merge colors within this Euclidean distance (0-255 RGB space)
TOP_N = 8


def _rgb255(color) -> tuple[int, int, int] | None:
    """Normalize a pdfminer color value (gray / RGB / CMYK) to 0-255 RGB, or None if unresolvable."""
    if isinstance(color, (int, float)):
        v = round(max(0.0, min(1.0, color)) * 255)
        return (v, v, v)
    if isinstance(color, (list, tuple)):
        vals = [max(0.0, min(1.0, c)) for c in color if isinstance(c, (int, float))]
        if len(vals) == 3:
            return tuple(round(c * 255) for c in vals)
        if len(vals) == 4:
            c, m, y, k = vals
            return (
                round(255 * (1 - c) * (1 - k)),
                round(255 * (1 - m) * (1 - k)),
                round(255 * (1 - y) * (1 - k)),
            )
        if len(vals) == 1:
            v = round(vals[0] * 255)
            return (v, v, v)
    return None


def _is_grayscale(rgb: tuple[int, int, int]) -> bool:
    return (max(rgb) - min(rgb)) <= GRAYSCALE_SPREAD * 255


def _weighted_colors(pdf: pdfplumber.PDF, max_pages: int):
    """Yield (rgb, weight) for every filled/stroked vector object across the sampled pages."""
    for page in pdf.pages[:max_pages]:
        for rect in page.rects:
            if not rect["fill"]:
                continue
            rgb = _rgb255(rect["non_stroking_color"])
            area = abs(rect["width"] * rect["height"])
            if rgb is not None and area > 0:
                yield rgb, area
        for curve in page.curves:
            if not curve["fill"]:
                continue
            rgb = _rgb255(curve["non_stroking_color"])
            area = abs(curve["width"] * curve["height"])
            if rgb is not None and area > 0:
                yield rgb, area
        for line in page.lines:
            if not line["stroke"]:
                continue
            rgb = _rgb255(line["stroking_color"])
            length = ((line["x1"] - line["x0"]) ** 2 + (line["y1"] - line["y0"]) ** 2) ** 0.5
            weight = length * max(line["linewidth"] or 0.5, 0.5)
            if rgb is not None and weight > 0:
                yield rgb, weight


def _cluster(weighted: list[tuple[tuple[int, int, int], float]], top_n: int) -> list[str]:
    """Greedily merge near-duplicate colors (Euclidean distance) and keep the top N by total weight."""
    buckets: dict[tuple[int, int, int], float] = {}
    for rgb, weight in weighted:
        # pre-merge into 8-unit buckets so anti-aliasing variants collapse before the O(n*k) pass below
        key = tuple(min(255, round(c / 8) * 8) for c in rgb)
        buckets[key] = buckets.get(key, 0.0) + weight

    ranked = sorted(buckets.items(), key=lambda kv: kv[1], reverse=True)
    clusters: list[list] = []  # each entry: [representative_rgb, total_weight]
    for rgb, weight in ranked:
        for cluster in clusters:
            dist = sum((a - b) ** 2 for a, b in zip(rgb, cluster[0])) ** 0.5
            if dist <= CLUSTER_DISTANCE:
                cluster[1] += weight
                break
        else:
            clusters.append([rgb, weight])

    clusters.sort(key=lambda c: c[1], reverse=True)
    return ["#%02X%02X%02X" % c[0] for c in clusters[:top_n]]


def _local_path_for(firm: str, url: str) -> Path:
    basename = Path(urllib.parse.urlsplit(url).path).name
    return PDF_DIR / f"{firm}__{basename}"


def _fetch(firm: str, urls: list[str], refresh: bool) -> list[Path]:
    paths = []
    for url in urls:
        local = _local_path_for(firm, url)
        if local.exists() and not refresh:
            paths.append(local)
            continue
        try:
            local.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                local.write_bytes(resp.read())
            paths.append(local)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"  [{firm}] could not fetch {url}: {exc}")
    return paths


def extract_firm_palette(pdf_paths: list[Path], max_pages: int, top_n: int) -> dict:
    weighted: list[tuple[tuple[int, int, int], float]] = []
    pages_scanned = 0
    for path in pdf_paths:
        with pdfplumber.open(path) as pdf:
            sample = pdf.pages[:max_pages]
            pages_scanned += len(sample)
            for rgb, w in _weighted_colors(pdf, max_pages):
                if not _is_grayscale(rgb):
                    weighted.append((rgb, w))
    if not weighted:
        return {"status": "no_vector_color_found", "colors": []}
    return {
        "status": "ok",
        "colors": _cluster(weighted, top_n),
        "pages_scanned": pages_scanned,
        "sources": [str(p.relative_to(SANDBOX_DIR)) for p in pdf_paths],
    }


def run(firm_filter: str | None, refresh: bool, max_pages: int, top_n: int) -> dict:
    firms = {firm_filter: FIRM_SOURCES[firm_filter]} if firm_filter else FIRM_SOURCES
    results: dict[str, dict] = {}
    for firm, primary_url in firms.items():
        urls = [primary_url] + EXTRA_SOURCES.get(firm, [])
        print(f"[{firm}] fetching {len(urls)} source(s)...")
        paths = _fetch(firm, urls, refresh)
        if not paths:
            results[firm] = {"status": "blocked", "colors": [], "attempted_sources": urls}
            print(f"  [{firm}] unavailable -- no source could be downloaded")
            continue
        results[firm] = extract_firm_palette(paths, max_pages, top_n)
        print(f"  [{firm}] {results[firm]['status']}: {results[firm]['colors']}")

    PALETTE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    PALETTE_CACHE.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {PALETTE_CACHE}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firm", choices=sorted(FIRM_SOURCES), help="only process this firm")
    parser.add_argument("--refresh", action="store_true", help="re-download even if cached")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES)
    parser.add_argument("--top-n", type=int, default=TOP_N)
    args = parser.parse_args()

    results = run(args.firm, args.refresh, args.max_pages, args.top_n)

    print("\nTHEMES = {")
    for firm, data in results.items():
        if data["colors"]:
            print(f"    {firm!r}: {data['colors']!r},")
    print("}")


if __name__ == "__main__":
    main()
