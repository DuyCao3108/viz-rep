# Module map

This skill's code lives in the real, imported, tested `src/report/` package — not in a copy
under this skill directory (unlike the original `libs/`-level version of this skill, which kept
`references/xlsx_insight_lib.py` because it had no real package to live in; here it does, so a
second copy would just drift out of sync).

| File | Responsibility |
|---|---|
| `src/report/xlsx_insight_lib.py` | openpyxl styling primitives: `new_workbook`, `section_header`, `subheader`, `bullet`, `footnote`, `hypothesis_table`, `estimate_image_rows`, `insert_image`, `_add_picture_borders`, `resolve_insight_output_path`, `save`. |
| `src/report/outline.py` | Parses the `- ` / `    ○ ` / `\|` / `BLANK` outline DSL into `Section` objects (`parse_outline`, `parse_outline_file`). Pure stdlib, no openpyxl/PIL dependency. |
| `src/report/build.py` | Drives `Section` objects into a workbook via `xlsx_insight_lib.py`. Owns the n-way split-row column-anchor math (`_split_row_columns`, `_place_image_row`) and the top-level `build_insight_xlsx()` entry point. |
| `src/report/combine.py` | `vstack_images()` — vertically stitches already-rendered chart PNGs into one review image. Unrelated to xlsx-building; used by `story/*/main.py`'s `combine_output` flag. |
| `src/report/cli.py` | `python -m src.report.cli --outline ... --out ...` — the one shared entry point every story uses, so no per-story driver script is needed. |

See `style-spec.md` for the visual rules these modules encode, and `SKILL.md` for the workflow.
