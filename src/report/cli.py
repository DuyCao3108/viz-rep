"""Shared CLI entry point for building an insight xlsx from an outline file.
One generic command covers every story — no per-story driver script needed.

    python -m src.report.cli --outline story/pcb_bank/insight_outline.txt \\
        --out story/pcb_bank/output/InsightResult_pcb_bank.xlsx
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.report.build import BASE_WIDTH_PX, build_insight_xlsx
from src.report.outline import parse_outline_file

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outline", required=True, type=Path, help="Path to the insight_outline.txt file")
    parser.add_argument("--out", required=True, type=Path, help="Path to write the InsightResult xlsx to")
    parser.add_argument("--base-width-px", type=int, default=BASE_WIDTH_PX, help="Full-width image target width in px")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root image paths resolve against")
    parser.add_argument("--no-validate-exists", action="store_true", help="Skip checking that image paths exist")
    args = parser.parse_args(argv)

    sections = parse_outline_file(
        args.outline,
        repo_root=args.repo_root,
        validate_exists=not args.no_validate_exists,
    )
    out_path = build_insight_xlsx(sections, args.out, base_width_px=args.base_width_px)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
