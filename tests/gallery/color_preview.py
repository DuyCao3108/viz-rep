"""Render every color declared in `src/custom/colors.py` for visual review:
one swatch band per COLOR_THEMES entry (`plot_theme_palette`), and one full
lightness ladder per COLOR_DICTS entry (`plot_step_palette`) — both functions
already exist in colors.py, this script just calls them for every name/theme.

Not pytest-collected (not named test_*.py) and asserts nothing — reviewed
by eye, same convention as tests/gallery/run.py and font_preview.py. Run
directly:

    python tests/gallery/color_preview.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Script dir is auto-added to sys.path by Python; repo root needs to be on
# sys.path too so `src.custom.colors` is importable.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt

from src.custom.colors import COLOR_DICTS, COLOR_THEMES, plot_step_palette, plot_theme_palette

OUTPUT_DIR = Path(__file__).parent / "output" / "colors"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for theme_name in COLOR_THEMES:
        fig = plot_theme_palette(theme_name, save_path=OUTPUT_DIR / f"theme_{theme_name}.png")
        plt.close(fig)

    for color_name in COLOR_DICTS:
        fig = plot_step_palette(color_name, save_path=OUTPUT_DIR / f"steps_{color_name}.png")
        plt.close(fig)

    print(
        f"Rendered {len(COLOR_THEMES)} theme(s) + {len(COLOR_DICTS)} step ladder(s) "
        f"to {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
