---
name: insight-draft
description: >
  Drafts a finished analysis into an InsightResult_*.xlsx workbook matching Duy's established
  insight-report template (section bands, indent ladder, hypothesis tables, chart pastes),
  driven by a plain-text outline file that names which chart PNG goes under which finding.
  Trigger when the user says "draft the insight", "write up this analysis", "create the
  InsightResult file", "build the insight_outline", or asks to turn analysis results/charts
  into the xlsx deliverable for a story.
---

# Insight Draft

Turns a finished analysis (goal, method, findings, chart exports already rendered under a
story's `output/` tree) into an `InsightResult_*.xlsx` file styled exactly like the reference
workbook `CDDA/DEV/PCB CARD/InsightResult_CVM_PCB_Card_Analysis.xlsx`.

Read `references/style-spec.md` once per session before drafting — it documents every styling
rule (fills, borders, indent columns, spacing, chart layouts, the outline-driven split/BLANK
convention) that `src/report/xlsx_insight_lib.py` + `src/report/build.py` encode. Don't hand-roll
openpyxl styling; call the library functions. `references/module-map.md` points at the real
module files — there is no second copy of the library inside this skill directory, unlike the
original `libs/`-level version of this skill (which had no real package to live in and so kept
its own reference copy).

**What's fixed vs. what isn't.** Only the *visual system* is fixed: fonts, fills, borders, the
indent ladder (columns B–E), spacing rules, and chart layouts, all from `style-spec.md`/
`xlsx_insight_lib.py`. The *content skeleton* — which top-level sections exist, what order they
come in, and how a section is subdivided — is NOT fixed. The outline-driven flow this skill now
uses (see STEP 1) produces a flat list of bold-headline findings, each with its own chart
row(s) — that's one valid skeleton, not the only one. If the user hands you a draft with the
PCB Card reference's fuller structure (Goal / Info for analysts / Results / Other observation),
build section bands to match that instead — `xlsx_insight_lib.py`'s `section_header()`/
`subheader()`/`hypothesis_table()` primitives are still there for that case, `build.py` just
doesn't call them for the flat outline-driven flow.

---

## STEP 0 — Gather content

Ask for whatever isn't already clear from the conversation. Don't guess on these — wrong
structure means a redo:

1. **Section structure** — if the user's draft already has its own top-level sections (Goal,
   Result, Detail, Info for analyst, or any other grouping), that structure and order is
   authoritative. Otherwise, the outline-driven flat-findings flow (STEP 1) is the default.
2. **Findings** — each one a headline (what the finding is / the answer to a goal question) plus
   the chart(s) that support it. If a question is hypothesis-driven, get the hypothesis list (id,
   hypothesis statement, "true if" condition) — `hypothesis_table()` is available for this, though
   the outline DSL itself doesn't encode hypothesis tables (write those cases as a manual
   `build_insight_xlsx`-adjacent call, or a plain bullet, per what the user actually needs).
3. **Chart images** — these must already exist as PNG files under the story's `output/<topic>/`
   tree (rendered by `story/<name>/main.py` — this skill never generates charts, only places
   them). If a chart isn't ready yet, use `BLANK` at that slot in the outline (see STEP 1) — the
   builder renders an italic `[Chart to insert: ...]` placeholder there automatically.
4. **Output location** — defaults to repo-local: `story/<name>/output/InsightResult_<name>.xlsx`
   (created automatically). Only ask for an absolute override path (e.g. a OneDrive/CDDA folder)
   if the user explicitly wants the deliverable saved somewhere else for stakeholder handoff —
   pass it as `override_abs_dir` to `resolve_insight_output_path()`, or directly as `--out` to
   the CLI.

---

## STEP 1 — Write the outline file, then run the builder

Instead of a one-off per-session driver script, write (or update) a plain-text outline file at
`story/<name>/insight_outline.txt`. Format:

```
- <finding headline>
    ○ <repo-relative/path/to/chart.png>
    ○ <path/to/left.png> | <path/to/right.png>
    ○ BLANK
```

- A line starting with `- ` begins a new finding.
- An indented `    ○ ` line under a finding is one row of chart image(s) for it.
- `|` splits a row into side-by-side columns — any number of images can share one row this way.
- A cell containing `BLANK` (case-insensitive) means no image there yet — the builder renders an
  italic `[Chart to insert: <headline> — slot i/n]` placeholder instead.
- Image paths are plain repo-relative paths (e.g. `story/pcb_bank/output/quest_1/quest1_multi_ax.png`),
  resolved against the repo root.

Example (from a real `story/pcb_bank/insight_outline.txt`):

```
- Overview of active PCB client
    ○ story/pcb_bank/output/quest_1/quest1_multi_ax.png
    ○ story/pcb_bank/output/quest_1_xsel/quest_1_xsel.png
- Multi-lenders, especially with BANK, are significantly more Digital
    ○ story/pcb_bank/output/quest_2_1/quest2_1.png | BLANK
    ○ story/pcb_bank/output/quest_2_2/quest2_2_1.png | story/pcb_bank/output/quest_2_2/quest2_2_2.png
    ○ story/pcb_bank/output/quest_2_3/quest2_3_1.png | story/pcb_bank/output/quest_2_3/quest2_3_2.png
- This behavior can be explained by two hypotheses:
    ○ BLANK
```

Then run the shared CLI (one command covers every story — no per-story driver script needed):

```bash
python -m src.report.cli \
    --outline story/pcb_bank/insight_outline.txt \
    --out story/pcb_bank/output/InsightResult_pcb_bank.xlsx
```

`build_insight_xlsx()` (in `src/report/build.py`) lays each finding out as a bold headline
bullet followed by its image row(s) — a single (unsplit) row's image gets the full
`--base-width-px` (default 1100px) width; an n-way `|`-split row gives each image
`base_width_px / n` so the combined row stays visually consistent with a full-width chart. This
is why chart-authoring `FIG_SIZE` should follow the matching convention (full width 16 for a
standalone chart, `16/n` for one going into an n-way split row — see
`story/pcb_bank/plot/base.py`'s `register_plot` docstring) — the builder computes the *display*
width regardless, but a source PNG authored at the wrong native proportions will still look
disproportionate (tiny fonts, or an overly cramped/loose chart) once scaled to that width.

`resolve_insight_output_path(story_name, filename=None, *, override_abs_dir=None)` (in
`src/report/xlsx_insight_lib.py`) is available if you need to compute the save path
programmatically rather than passing `--out` directly — it defaults to
`story/<story_name>/output/InsightResult_<story_name>.xlsx`, or `override_abs_dir` if given.

`save()` itself checks for a pre-existing file at the target path and, if found, renames it in
place with a `_backup_<timestamp>` suffix before writing the new version — so re-running the
builder after outline edits never silently clobbers a prior draft.

If a finding needs the fuller fixed-skeleton layout (section bands, hypothesis tables,
chart-beside-callout) instead of the flat outline-driven flow, fall back to calling
`xlsx_insight_lib.py`'s primitives directly in a short ad-hoc script, the same way the original
`libs/`-level skill's driver scripts did — `new_workbook()`, `section_header()`, `subheader()`,
`bullet()`, `hypothesis_table()`, `insert_image()`, `save()` are all still there for that case.

---

## STEP 2 — Run and verify

Confirm:
- The command exits 0 and the file exists at the intended path.
- Re-open it with openpyxl (`data_only=True`) and spot-check that the finding headlines, image
  count, and placeholder text roughly match what was intended — this catches path typos and
  outline-formatting mistakes before handing it to the user. `len(ws._images)` should equal the
  count of non-`BLANK` cells in the outline.

Report the saved path to the user. Don't claim done without having actually re-opened and
checked it once.
