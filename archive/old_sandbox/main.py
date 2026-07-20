"""Sandbox: apply financial-firm chart palettes to a mock BI dataset.

Palettes were pulled from each firm's real chart-dense report PDF via
extract_palette.py (dominant vector-fill colors, weighted by area, grayscale
ink dropped). See sandbox/data/palettes.json for full extraction metadata
(sources, pages scanned, status per firm) and sandbox/output/palette_swatches.png
for a visual preview.
"""
import numpy as np

THEMES: dict[str, list[str]] = {
    "jpmorgan": ["#B0E0FF", "#0090F8", "#80A030", "#004888", "#70C0FF", "#7040B8", "#005030", "#E87000"],
    "goldman_sachs": ["#083060", "#7098C8", "#5090E0", "#A0C058", "#A84090", "#C0D0F0", "#60D0C8", "#E07018"],
    "bain": [],  # blocked: bain.com returns 403 to non-browser clients (see extract_palette.py)
    "bcg": [],  # blocked: web-assets.bcg.com returns 403 to non-browser clients
    "mckinsey": [],  # blocked: mckinsey.com connection times out for non-browser clients
}


def generate_mock_data(seed: int = 0):
    """1 main dimension (quarter), 1 legend dimension (sector, 7 values), 1 measure (allocation %)."""
    rng = np.random.default_rng(seed)

    periods = [f"Q{q} {y}" for y in (2024, 2025) for q in (1, 2, 3, 4)]  # main dimension, 8 values
    sectors = [
        "Technology", "Healthcare", "Financials", "Energy",
        "Consumer", "Industrials", "Utilities", 'Education', 'Hospitality'
    ]  # legend dimension, 7 values

    base = rng.uniform(5, 20, size=len(sectors))
    walk = rng.normal(0, 1.2, size=(len(periods), len(sectors))).cumsum(axis=0)
    values = np.clip(base + walk, 1, None)  # rows=periods, cols=sectors

    return periods, sectors, values


if __name__ == "__main__":
    periods, sectors, values = generate_mock_data()
    print("periods:", periods)
    print("sectors:", sectors)
    print("values shape:", values.shape)
    print("themes available:", {k: len(v) for k, v in THEMES.items()})
