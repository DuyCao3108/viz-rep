# Project Log: viz

Last updated: 2026-07-12

## Purpose
A Python wrapper around matplotlib/numpy that automates repeatable, professional-looking BI charts with minimal per-chart boilerplate.

## Current structure
- `main.py` — entry point (not yet fleshed out with chart classes)
- `src/` — empty so far, intended home for the chart wrapper library
- `story/sample/chart1.py` — early one-off sample script
- `archive/learning/` — matplotlib learning scripts, not part of the library proper
- `design.txt` — chart taxonomy brainstorm (bar done in detail, line in progress)

## Decisions
- Chart taxonomy is organized as `chart type / shapes (variants) / config (common styling)`, e.g. `bar/shapes/{vertical,horizontal}/...` + `bar/config/common/{dim_axis,mes_axis,data_label,bars,spines,colors,legends}`. Line chart shapes will follow the same nesting.
- For `line`, stacking should not be implemented as bare stacked lines (visually unreadable) — `stack_line`/`stack_100_line` are aliases that render as filled `area`/`stack_100_area` under the hood. Line's shape list: `simple_line`, `multi_line`, `step_line`, plus `area`, `stack_area`, `stack_100_area` as the stacking-capable siblings. Lower-priority additions: `dual_axis_line`, `line_with_markers`, `range_band_line`, `spark_line`.
- Chart classes (e.g. `Bar`, `StackBar`) take a matplotlib `ax` (Axes), not `plt`, as their draw target. Reason: `plt` is global pyplot state — breaks composition of multiple charts in one figure (subplot grids/dashboards) and complicates testing. Each chart class should own drawing onto one `Axes` it's given.
- `fig` is not owned by individual chart classes. It belongs to a separate layout/canvas layer responsible for: figure-level legend (`fig.legend()`), suptitle/footnotes, sizing (`tight_layout`, `subplots_adjust`), export (`fig.savefig()`), and shared colorbars across multiple axes. This maps onto the taxonomy: legends/spines are chart-local (`config/common/legends`), but a legend shared across multiple charts would live one level up in the layout layer.

## Open questions
- Where exactly does the layout/canvas layer live in the module structure (`src/` subpackage name, relationship to `story/`)?
- Whether chart class construction is `Bar(ax)` + `.render(data)`, or some other interface shape (constructor vs. method args) — not yet decided.
- Bar chart taxonomy is fleshed out in `design.txt`; line chart taxonomy just brainstormed here, not yet written into `design.txt`. Other chart types (area as standalone vs. line sibling, scatter, pie, combo charts) not yet brainstormed.

## Next
- Write the line chart shape/config taxonomy into `design.txt` (matching bar's nesting) once confirmed.
- Continue chart type brainstorm (area, scatter/point, combo) before moving further into program design.
- Decide the concrete interface for chart classes (constructor signature, `.render()`/`.plot()` method) and where the layout/canvas layer lives in `src/`.
