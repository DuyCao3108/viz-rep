# Insight Report — Style Spec

Extracted from `InsightResult_CVM_PCB_Card_Analysis.xlsx` (CDDA/DEV/PCB CARD). This is the
ground truth for how an insight-result workbook looks. `src/report/xlsx_insight_lib.py` and
`src/report/build.py` implement all of this — read this file to understand *why* the code writes
what it writes, not to re-derive it.

## Workbook shell
- One sheet, named `Analysis`.
- Gridlines OFF (`sheet_view.showGridLines = False`).
- No freeze panes, no cell merges anywhere in the file — indentation and section banding are
  done entirely with column offset and per-cell fill, never `merge_cells`.
- Font throughout: **Calibri 11**. Footnotes drop to size 10.
- Default row height (14.4pt) everywhere — section headers are NOT taller than body rows.

## Column plan (the indent ladder)
| Col | Width | Role |
|---|---|---|
| A | ~3.1 | dead margin, never written to |
| B | ~4.7 | section-band label (bold titles like "1 Goal is to answer") |
| C | ~3.9 | level-0 indent: sub-headers, restated questions, top-line takeaways, and — in the outline-driven flow — every finding's bold headline |
| D | ~4.0 | level-1 indent: detail bullets |
| E | ~3.4 | level-2 indent: sub-bullets |
| F… | default (~8.43) | free text continuation / chart callouts — no wrap_text; text is left to overflow visually into blank neighboring cells, exactly like Excel does by default |

Content columns past E get custom widths only when a specific chart callout needs the room
(e.g. a wide column set to ~13 to fit a paragraph next to an image) — not a fixed rule, just
size to fit when you place a callout.

## Section header band
Each top-level section (e.g. "1 Goal is to answer", "2-Info for analysts", "3-Results",
"4-Other observation") is one row styled as a full-width band:
- Fill: solid, **`F2F2F2`** (Excel's "Background 1, Darker 5%") across the *entire* row from
  column B through column AE — fixed right edge at AE regardless of how much content exists.
- Font: bold, 11pt, on the title cell (column B) only; the rest of the filled cells carry no
  text, just the fill.
- Border: thin box around the whole band — top edge and bottom edge run the full B:AE width,
  left edge on B only, right edge on AE only. Not a per-cell box; one rectangle.
- No blank row before a section-header band — the fill/border is itself the visual separator
  from whatever content preceded it.
- No blank row after a section-header band either — first content line starts immediately on
  the next row.

**The outline-driven flow (see below) doesn't use section-header bands at all** — it's a flat
list of findings, each starting directly with its bold headline bullet in column C.

## Sub-headers (topic labels inside a section)
Column C, italic + underline, not bold, 11pt. E.g. "Data sources", "Analysis's approach",
"1-How many card users we acquired from rivals every month?" (a results section restates the
goal question here).
- Exactly one blank row separates a sub-header from whatever came before it, UNLESS it's the
  very first sub-header right after a section band (then zero blank rows).

## Body bullets
Plain 11pt text, no bold/italic, no border, no wrap. Placed at the column matching its indent
depth (C/D/E per the ladder above). No blank row between consecutive bullets at the same or
increasing depth. Multi-line "paragraphs" are just consecutive bullet rows at the same column,
not one wrapped cell.

## Bold takeaway lines
A finding that should read as a headline (not a bullet) is bold, not italic, same 11pt, placed
in whatever column the surrounding block uses (C for text-only findings, or the callout column
next to a chart — see below). This is the "TL;DR" line a reader skims for. In the outline-driven
flow, every finding's headline (the `- ` line) is written this way, always at column C.

## Footnotes
Italic, 10pt (a point smaller than body), prefixed with a literal `(*)` marker in its own
leading cell when it annotates a specific claim above. Placed directly under the line it
annotates, no blank row.

## Small reference tables (e.g. a hypothesis table)
Used when a section runs multiple named hypotheses. Header row: italic (not bold), thin
bottom border across all header cells, thin left border marking each column boundary. Data
rows: thin left border only (column separators), no bottom border, no fill. Index column is
right-aligned; text columns are left-aligned default. No wrap_text — columns are just wide
enough (the source file widened column L to ~12.8 to fit hypothesis text).

## Charts
Every chart in the workbook is a **pasted PNG screenshot** (not a native Excel chart) — for
`story/*` outputs, one rendered by that story's `main.py` under `output/<topic>/*.png`. Two
layout patterns, chosen per finding:

1. **Chart-below** — a bold headline + optional detail bullet in column C, then the image
   placed on the next row spanning nearly the full content width (roughly columns B/C through
   S/T). Used for single, self-explanatory charts (the "Other observation" section uses this
   throughout; also the outline-driven flow's default for an unsplit `○` row).
2. **Chart-beside** — a narrower image (roughly half width, columns C/D through L/M) with a
   callout — bold headline line + plain detail line(s) — placed in a column just past the
   image's right edge (e.g. column N when the image ends at L). Used when a chart needs an
   explicit conclusion pinned next to it (the hypothesis-testing sub-section uses this: chart
   left, "H1 is false, ..." callout to its right).

After a chart, leave 2–3 blank rows before the next sub-header or section band — images float
over the grid and don't respect row boundaries precisely, so the gap keeps headers from
crowding the image visually.

Every pasted chart PNG gets a thin **light-grey** (`D9D9D9`) native Picture Border — the same
outline you'd set by hand via Excel's Picture Format > Picture Border color picker, not a
border on the underlying cells. Chart exports have no border of their own, so without one the
image edge blends into the sheet's white background. openpyxl's Image API has no property for
this, so `save()` patches it into each picture's drawing XML after `wb.save()` runs (see
`_add_picture_borders` in `xlsx_insight_lib.py`) — no extra step needed beyond calling
`insert_image()`/`build_insight_xlsx()` and `save()` as usual.

## Outline-driven flow: n-way split rows and BLANK (viz-rep addition)

The outline DSL's `|`-split `○` rows generalize "chart-below" to an n-way row: instead of one
full-width image, `n` images share one row side by side. `src/report/build.py`'s
`_split_row_columns()` computes each slot's anchor column by walking the sheet's real column
pixel widths (`xlsx_insight_lib.py`'s `MDW`/`COL_PAD_PX`/`DEFAULT_COL_WIDTH` — the standard
Excel column-width-units-to-pixels formula) starting from column C, spaced by each slot's target
width plus a small gap. Each image's `target_width_px` is `base_width_px / n` (default
`base_width_px = 1100`, matching the widest "chart-below" pattern above) — so a 2-way split row
totals the same visual width as one full-width chart-below image, not double it.

A source chart PNG's own `FIG_SIZE` should follow the matching convention when it's *authored*
(see `story/<name>/plot/base.py`'s `register_plot` docstring): full width (16) for a chart
that'll occupy an unsplit row, `16/n` for one going into an n-way split row. The builder scales
to `target_width_px` regardless of a PNG's native size, but a chart authored at the wrong
proportions for its eventual display width will still look off (fonts too small/large relative
to the chart) once placed — this is guidance for chart authors, not something the builder can
fix after the fact.

A `BLANK` cell (case-insensitive) in a split (or unsplit) `○` row renders as an italic
`[Chart to insert: <finding headline> — slot i/n]` placeholder in that slot's column instead of
an image — the same convention the original skill used for "chart not exported yet," just
computed automatically from the outline text instead of a driver script's ad-hoc call.

## Content skeleton — example only, not a fixed schema
The section list below is what the PCB Card reference file happens to use — one example
skeleton (full section bands + sub-headers + hypothesis tables), alongside the flatter
outline-driven skeleton this skill now defaults to (a plain list of bold-headline findings, no
section bands). Neither is a mandatory schema; only the banding/indent/spacing mechanics above
carry over to whatever structure a given draft actually needs. See `SKILL.md` STEP 0/1 for how
to decide.

1. **1 Goal is to answer** — plain numbered list of the specific questions the analysis
   answers, one per row, column C, no sub-header needed.
2. **2-Info for analysts** — sub-headers for: Data sources, Data pool (population + exclusion
   criteria), Analysis's approach (methodology, TG/CG split logic, comparison logic), and any
   caveat notes (e.g. a data-quality/logic note) — each with 1-3 levels of bullets underneath.
3. **3-Results** — one sub-header per goal question (restated), each followed by a bold or
   plain summary line, then supporting chart(s) in whichever layout fits. Hypothesis-driven
   questions get a hypothesis table + per-hypothesis chart-beside-callout blocks.
4. **4-Other observation** — extra findings not tied to a specific goal question: bold
   headline + detail bullet + chart-below, repeated per observation.
