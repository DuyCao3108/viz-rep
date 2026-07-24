"""Stitches already-rendered chart PNGs into one image for quick visual review
— story-agnostic, no knowledge of Vizzy/Dataset/plot registration."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


def vstack_images(
    paths: list[Path],
    out_path: str | Path,
    *,
    gap_px: int = 12,
    bg: tuple[int, int, int] = (255, 255, 255),
) -> Path:
    """Vertically concatenate PNGs in the given order, centering narrower ones,
    into one PNG at out_path."""
    images = [Image.open(p) for p in paths]
    width = max(im.width for im in images)
    height = sum(im.height for im in images) + gap_px * (len(images) - 1)

    canvas = Image.new("RGB", (width, height), bg)
    y = 0
    for im in images:
        x = (width - im.width) // 2
        mask = im if im.mode in ("RGBA", "LA") else None
        canvas.paste(im, (x, y), mask)
        y += im.height + gap_px

    for im in images:
        im.close()

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path
