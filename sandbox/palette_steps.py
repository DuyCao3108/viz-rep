"""Sandbox: densify each accent family's published tones into a step-5 lightness ladder.

The design system only publishes a handful of tones per family (e.g. hong-kong
ships just 45/55/90/95). This fills in every multiple of 5 from 5 to 95 using
src.themes.generate_steps (hue/saturation held fixed, lightness stepped), then
renders all families as one swatch grid and dumps the raw hex values to JSON.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

from src.themes import COLOR_COLLECTIONS, generate_steps

SANDBOX_DIR = Path(__file__).resolve().parent

FAMILIES = (
    list(COLOR_COLLECTIONS["accent_primary"])
    + list(COLOR_COLLECTIONS["accent_secondary"])
    + list(COLOR_COLLECTIONS["accent_tertiary"])
)
STEPS = range(5, 96, 5)


def main() -> None:
    ladder = {family: generate_steps(family) for family in FAMILIES}

    fig, ax = plt.subplots(figsize=(1.1 * len(STEPS), 1.3 * len(FAMILIES)))
    for row, family in enumerate(FAMILIES):
        y = len(FAMILIES) - 1 - row
        for col, lightness in enumerate(STEPS):
            hex_code = ladder[family][lightness]
            ax.add_patch(plt.Rectangle((col, y), 1, 1, facecolor=hex_code, edgecolor="white", linewidth=0.5))
            text_color = "white" if lightness < 50 else "black"
            ax.text(col + 0.5, y + 0.5, str(lightness), ha="center", va="center", fontsize=6, color=text_color)
        ax.text(-0.3, y + 0.5, family, ha="right", va="center", fontsize=9)

    ax.set_xlim(-2.2, len(STEPS))
    ax.set_ylim(0, len(FAMILIES))
    ax.axis("off")
    ax.set_title("Lightness ladder — step 5", fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(SANDBOX_DIR / "output" / "palette_steps.png", dpi=500)

    (SANDBOX_DIR / "data" / "palette_steps.json").write_text(json.dumps(ladder, indent=2))


if __name__ == "__main__":
    main()
