# Project Log: viz

Last updated: 2026-07-16

## Purpose
A Python wrapper around matplotlib/numpy that automates repeatable, professional-looking BI charts with minimal per-chart boilerplate — plus a Power BI-style dimension/measure data layer, so charts bind to declared data semantics instead of hand-shaped arrays.

## Current structure
- `src/dataset.py` — `Dataset`/`Dimension`/`Measure` semantic data layer (Polars-backed)
- `src/vizzy.py` — `Vizzy` (chart dispatcher) + `Artist` (post-hoc styling facade)
- `src/styles.py` — `DefaultStyle`, the shared visual-vocabulary layer charts apply
- `src/charts/` — chart shape classes, one module per family (`bar.py`, `line.py`)
- `src/colors.py`, `src/fonts.py` — Economist Design System color/typography tokens
- `story/pcb_card/` — worked example wiring `Dataset` → `Vizzy` → rendered chart (`plot/bar_1.py`)
- `archive/` — old learning scripts and prototype analyses, not part of the library proper
- `design.txt` — chart taxonomy brainstorm (bar done in detail, line in progress)

## Decisions
- Chart taxonomy is organized as `chart type / shapes (variants) / config (common styling)`, e.g. `bar/shapes/{vertical,horizontal}/...` + `bar/config/common/{dim_axis,mes_axis,data_label,bars,spines,colors,legends}`. Line chart shapes will follow the same nesting.
- For `line`, stacking should not be implemented as bare stacked lines (visually unreadable) — `stack_line`/`stack_100_line` are aliases that render as filled `area`/`stack_100_area` under the hood. Line's shape list: `simple_line`, `multi_line`, `step_line`, plus `area`, `stack_area`, `stack_100_area` as the stacking-capable siblings. Lower-priority additions: `dual_axis_line`, `line_with_markers`, `range_band_line`, `spark_line`.
- Chart classes (e.g. `Bar`, `StackBar`) take a matplotlib `ax` (Axes), not `plt`, as their draw target. Reason: `plt` is global pyplot state — breaks composition of multiple charts in one figure (subplot grids/dashboards) and complicates testing. Each chart class should own drawing onto one `Axes` it's given.
- `fig` is not owned by individual chart classes. It belongs to a separate layout/canvas layer responsible for: figure-level legend (`fig.legend()`), suptitle/footnotes, sizing (`tight_layout`, `subplots_adjust`), export (`fig.savefig()`), and shared colorbars across multiple axes. This maps onto the taxonomy: legends/spines are chart-local (`config/common/legends`), but a legend shared across multiple charts would live one level up in the layout layer.
- Added `src/dataset.py`: a Power BI-style semantic data layer — `Dimension`/`Measure` are declared once against a `Dataset` (wrapping a long-format Polars `DataFrame`), then queried by name via `Dataset.query(dim=, measure=, legend=, filters=)`, returning a `QueryResult` whose `.to_tuple()` matches the `(categories, values)` / `(categories, legend_categories, values)` shape chart code already expects (see `story/pcb_card/plot/bar_1.py`). Backend is Polars (chosen over pandas for performance/modern API). Scope is a single flat table only — no cross-table relationships/joins (PBI star-schema modeling), no multiple measures per query, no calculated/derived measures. These are plausible future extensions but weren't needed to unblock chart binding.
- Added the `Vizzy` chart layer on top of `Dataset`, resolving both open questions below:
  - **fig/ax ownership**: `Vizzy(fig, ax, dataset)` always takes a caller-supplied `fig`/`ax` — it never creates its own. This means there is no separate layout/canvas layer/module: composing multiple charts into one dashboard is just constructing more than one `Vizzy` against the same `fig` with different `ax` (e.g. `fig, axes = plt.subplots(nrows, ncols)`), and the caller calls `fig.savefig(...)` themselves once done. `Vizzy`/`ChartShape` have no `.save()` method.
  - **Construction vs. render**: `ChartShape(fig, ax, theme=)` sets up styling only (`DefaultStyle`, in `src/styles.py`, applying spines/font/color conventions lifted from `sandbox/build_report.py`); `.plot(categories, values, legend_categories=None)` draws data. `Vizzy.line(dim=, measure=, legend=, filters=)`/`.bar(...)` query the `Dataset` and call both steps. Param names deliberately match `Dataset.query()`'s vocabulary (`dim`/`measure`/`legend`), not `xaxis`/`yaxis` — orientation (vertical vs. horizontal bar) is a shape concern, not a call-site concern.
  - **Customization is not kwargs on `.line()`/`.bar()`.** A separate `Artist` object, reached via `viz.artist` (a property on `Vizzy`), provides fluent post-hoc mutators (`set_theme`, `set_series_color`, `show_data_label`, `show_legend`, `set_title`) that apply to whichever chart is currently active. `Artist` itself has zero chart-type branching — every `ChartShape` subclass implements the same mutator interface polymorphically (geometry-specific parts via `_draw_data_labels`/`_clear_data_labels`/`_set_artist_color` hooks), so adding a new chart shape never requires touching `Artist` or `Vizzy`'s dispatch body, only a new class in `src/charts/*.py` decorated with `@register_shape(name)` plus one import line in `src/charts/__init__.py`.
  - Shape classes live in `src/charts/` (one module per family — `bar.py`, `line.py`, future `special.py`) rather than one flat file, since `design.txt`'s bar taxonomy alone is 14 shape classes.
  - This pass implements two shapes only (`Line` in `charts/line.py`, handling both `simple_line`/`multi_line`; `SimpleBar` in `charts/bar.py`) — enough to prove the registry/mutator-interface mechanism isn't hardcoded to one shape. Full plan: `.claude/plans/context-i-use-pbi-memoized-abelson.md`.

## Not yet built (chart layer extension points)
- **Bar**: `StackBar`, `Stack100Bar`, `GroupBar`, `GroupStackBar`, `DiverseBar`, and horizontal (`h_*`) siblings — subclass `Bar` in `charts/bar.py`. Horizontal variants: leaning toward an `orientation` constructor flag on `Bar` rather than a parallel class tree, not decided definitively.
- **Line**: `stack_line`/`stack_100_line` (must render as filled area, never bare stacked lines — see decision above), `step_line`, `dual_axis_line`, `line_with_markers`, `range_band_line`, `spark_line`.
- **Special charts**: `Waterfall`, `Rank`, `Sankey`, `DecompositionTree`, `Lollipop`.
- Combining two chart types on one `ax` (e.g. dual-axis bar+line) — `Vizzy` holds exactly one active chart at a time by design.
- `Dimension(dtype="date")` exists in `dataset.py` but nothing in `styles.py`/`charts/` does date-aware axis formatting yet.
- `data_label.show_threshold`/`show_exact` and `legends_on_line` config knobs from `design.txt`.
- Power BI-style hand-drawn horizontal token legend (`build_report.py`'s `hlegend`) as an upgrade over the plain `ax.legend()` `DefaultStyle._set_legends()` uses now.
- Per-category (not just per-series) color overrides on `SimpleBar` (today one series = every bar recolors uniformly).

## Open questions
- Bar chart taxonomy is fleshed out in `design.txt`; line chart taxonomy just brainstormed here, not yet written into `design.txt`. Other chart types (area as standalone vs. line sibling, scatter, pie, combo charts) not yet brainstormed.

## Next
- Write the line chart shape/config taxonomy into `design.txt` (matching bar's nesting) once confirmed.
- Continue chart type brainstorm (area, scatter/point, combo) before moving further into program design.
- Pick the next chart shape to build from the extension-point list above (probably a second `Bar` variant, to further stress-test the registry before tackling the bigger special-chart types).
