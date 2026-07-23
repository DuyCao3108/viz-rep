"""Render every font stack declared in `src/custom/fonts.py` (FONT_STACKS)
into one contact-sheet PNG: left column is the stack's name + declared CSS
family chain + what matplotlib actually resolved it to on this machine;
right column is a sample sentence set in that resolved font.

Not pytest-collected (not named test_*.py) and asserts nothing — reviewed
by eye, same convention as tests/gallery/run.py. Run directly:

    python tests/gallery/font_preview.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Script dir is auto-added to sys.path by Python; repo root needs to be on
# sys.path too so `src.custom.fonts` is importable.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt

from src.custom.fonts import FONT_STACKS, resolve_installed_font

OUTPUT_DIR = Path(__file__).parent / "output"

SAMPLE_TEXT = (
    "    50% of Primes having active CL/CC with competitor - 62% of them are "
    "borrowing from Bank.\n"
)


def _parse_stack(css: str) -> list[str]:
    """'EconomistSerifOsF', ui-serif, Georgia, serif -> [names...], quotes stripped."""
    return [name.strip().strip("'\"") for name in css.split(",")]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stacks = sorted(FONT_STACKS.items())
    n = len(stacks)
    row_h = 1.1
    fig, ax = plt.subplots(figsize=(18, row_h * n))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n)
    ax.axis("off")

    for i, (stack_name, css) in enumerate(stacks):
        y = n - i - 0.5
        names = _parse_stack(css)
        resolved = resolve_installed_font(*names)

        info_text = f"{stack_name}\nstack: {css}\nresolved: {resolved}"
        ax.text(0.0, y, info_text, fontsize=7, va="center", ha="left", family="monospace")
        ax.text(0.42, y, SAMPLE_TEXT, fontsize=10, va="center", ha="left", family=resolved)
        ax.axhline(i, color="#dddddd", linewidth=0.5)

    fig.tight_layout()
    out_path = OUTPUT_DIR / "font_preview.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Rendered {n} font stack(s) to {out_path}")


if __name__ == "__main__":
    main()
