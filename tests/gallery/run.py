"""Render every gallery scenario to its own PNG under tests/gallery/output/,
plus one combined contact sheet with every scenario labeled by name, for
fast visual review.

Not pytest-collected (named run.py, not test_*.py) and never asserts
anything — scenarios are reviewed by eye. Run directly:

    python tests/gallery/run.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

# Script dir (tests/gallery) is auto-added to sys.path by Python, so
# `scenarios` (this dir's package) is importable already. Scenario build_fns
# import from `src`, so the repo root needs to be on sys.path too.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt

from scenarios import ALL_SCENARIOS

OUTPUT_DIR = Path(__file__).parent / "output"


def _render_individual(name: str, build_fn) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    build_fn(fig, ax)
    safe_name = name.replace("/", "_")
    fig.savefig(OUTPUT_DIR / f"{safe_name}.png", dpi=500)
    plt.close(fig)


def _render_contact_sheet(scenarios: list[tuple[str, object]]) -> None:
    n = len(scenarios)
    ncols = 1
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(12 * ncols, 6 * nrows), squeeze=False)

    for i, (name, build_fn) in enumerate(scenarios):
        ax = axes[i // ncols][i % ncols]
        build_fn(fig, ax)

    for i in range(n, nrows * ncols):
        axes[i // ncols][i % ncols].axis("off")

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "_contact_sheet.png", dpi=500)
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not ALL_SCENARIOS:
        print("No scenarios registered yet — add entries to tests/gallery/scenarios/*.py")
        return

    for name, build_fn in ALL_SCENARIOS:
        _render_individual(name, build_fn)

    _render_contact_sheet(ALL_SCENARIOS)
    print(f"Rendered {len(ALL_SCENARIOS)} scenario(s) to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
