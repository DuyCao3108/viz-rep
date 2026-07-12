# Learning Progress: Matplotlib

## Topic: learn_waterfall_chart

Last updated: 2026-07-12

### Covered
- Figure vs Axes (`fig, ax = plt.subplots()`) — fig is the whole canvas, ax is one plot area; everything gets drawn onto ax.
- Resolution basics — `figsize` (inches, controls physical size / relative font & line scale) vs `dpi` (pixels per inch, controls pixel density); total output pixels = figsize * dpi. Tried `dpi=300` on `savefig()` first as the smallest change.

- Ticks — `ax.tick_params()` for cosmetic control (length/width/color, `which='major'|'minor'|'both'`); `minorticks_on()` to auto-enable minor ticks.
- Explicit locators — `MultipleLocator(step)` for fixed-interval ticks, `AutoMinorLocator(n)` for n auto-spaced minor ticks between majors; applied to both `ax.xaxis` and `ax.yaxis`.

### Next
- Optional: finish the dpi-on-subplots vs dpi-on-savefig distinction (parked, not blocking).
- Then move to `figsize` hands-on (currently only explained, not yet tried by user).
- After that: styling the basic bar() into an actual waterfall (running totals / floating bars via `bottom=`).

## Topic: china_stacked_bar (horizontal bar chart) — script: learn-scripts/china_mili_bars.py

Last updated: 2026-07-12

### Covered
- Y-axis label clipping fix options — `fig.tight_layout()` (auto-remeasures margins from rendered text, easiest default), `constrained_layout=True` on `plt.subplots()` (same idea, recalculates continuously, better for resizing/notebooks), `fig.subplots_adjust(left=...)` (manual exact control), `savefig(bbox_inches='tight')` (crops saved file only, doesn't affect `plt.show()`).
- 100% stacked horizontal bar — normalize each row to sum to 100 (`value / row_total * 100`), then stack with repeated `barh()` calls using `left=` as the running cumulative offset; stacking mechanism itself is unchanged from regular stacked bars.
- Ordering category axis by value — `barh()` draws bottom-to-top in input order, so sort ascending (`np.argsort`) to get largest-at-top, or reverse (`[::-1]`) for largest-at-bottom; must reindex categories and all value arrays by the same permutation to keep them aligned.
- `np.argsort` mechanics — returns indices that would sort ascending, not the sorted values themselves; combined with `[::-1]` (Python reverse-slice, walks any sequence backwards) to flip ascending → descending.
- Hiding y-axis ticks vs labels independently — `tick_params(left=False)` removes just the tick mark and keeps value labels; `labelleft=False` removes just the labels; `set_yticks([])` or `yaxis.set_visible(False)` remove more (ticks+labels, or the whole axis) at once.
- Comprehensive `tick_params()` reference — scope (`axis=`, `which=`), mark visibility (`bottom/top/left/right`), label visibility (`labelbottom/labeltop/labelleft/labelright`), direction (`in/out/inout`), size (`length/width/color`), label styling (`labelsize/labelcolor/labelrotation/pad`), and grid tie-in (`grid_color` etc., only active if `ax.grid()` also called).
- `bar_label()` positioning — `label_type='edge'` anchors at the bar tip; `padding` (pixels) pushes the label along the direction it's pointing, and a **negative** value pulls an edge label back inside the bar instead of past its tip.
- `bar_label(labels=...)` override — by default the label text is auto-pulled from each bar's own size (so it reflects whatever value drew the bar, e.g. a %); passing `labels=[...]` explicitly replaces the displayed text while leaving the bar's geometry/anchor position untouched — used to show absolute counts on bars whose length represents a percentage.
- Color cycle / theme — matplotlib auto-assigns colors from `rcParams['axes.prop_cycle']` (a `plt.cycler(color=[...])`) to each plot call in sequence, in the order they're drawn; setting this before `plt.subplots()` re-themes all default-colored series at once. `plt.style.use('name')` is the broader version (colors + background + gridlines + fonts together; see `plt.style.available`). Background is *not* part of the cycle — set separately via `fig.set_facecolor()` / `ax.set_facecolor()`.
- Bar thickness vs. category spacing (`barh`) — categories are always spaced 1 unit apart on the axis (not directly changeable); `height=` (default 0.8) controls how thick each bar is *within* its slot, so shrinking it opens up visual whitespace between rows without touching category spacing itself.
- Figure/axes height — `figsize=(w, h)` on `plt.subplots()` sets physical inches and is the main lever for "make the whole plot taller"; `fig.set_size_inches(w, h)` is the same effect settable after creation; `fig.subplots_adjust(top=, bottom=)` instead reapportions how much of an *already-sized* figure the axes occupies (margins vs. axes box), no resize.
- `ylim` vs `figsize` vs `tick_params` — `ax.set_ylim()` changes the *data range* mapped onto the existing axes box (e.g. extending past the first/last category on a categorical `barh` axis adds padding/whitespace cheaply, without resizing the figure); `tick_params()` is purely cosmetic (tick marks/label styling) and affects neither size nor spacing; `set_yticks()` only controls tick/label positions. `set_ylim(top=...)` (or `bottom=...`) can be passed alone to shift just one bound while leaving the other at its current default — confirmed via `ax.get_ylim()` (default here was `(-0.475, 4.475)` for 5 categories); useful for opening room on just one side (e.g. top) for extra annotations without disturbing the rest of the layout.
- Custom "label above bar" (KPI-card style, not a tick label) — every `Rectangle` returned by `barh()`/`bar()` exposes `.get_x()/.get_y()/.get_width()/.get_height()`; loop over the bars and place text with `ax.text(bar.get_x(), bar.get_y() + bar.get_height() + offset, label, ha='left', va='bottom')`. This replaces the y-axis tick label entirely rather than styling it, so it's paired with hiding the real tick labels (see below).
- All 4 ways to remove y-axis tick labels, in order of surgical → blunt: (1) `ax.tick_params(left=False, labelleft=False)` — toggles marks/text independently, most reversible; (2) `ax.set_yticks([])` — removes tick positions entirely, no marks or labels; (3) `ax.set_yticklabels([])` — keeps tick positions/marks, empties label strings; (4) `ax.yaxis.set_visible(False)` — hides the whole axis including its spine attachment, most blunt one-liner.
- Matplotlib API mental model (why `ax.set_X()` vs `ax.something.set_X()`) — everything is a tree of Artists (`Figure → Axes → {xaxis, yaxis, spines[...], title, patches[...], texts[...]}`), and every Artist has its own `get_/set_` pairs for its own properties. `ax.set_X()` shortcuts exist only for the ~20 most common whole-Axes properties (limits, title, labels, scale) and are literally wrappers — e.g. `ax.set_xlabel()` calls `ax.xaxis.set_label_text()` internally. For anything more specific (locators, minor ticks, whole-axis visibility, spine styling), there's no Axes-level shortcut — go to the owning child object directly (`ax.xaxis.*`, `ax.spines['top'].*`) or call the method on an object you already have a reference to (a bar, a text, a line). Rule of thumb: try `ax.set_<thing>()` first; an `AttributeError` is the signal to ask "which child object owns this?" and go one level deeper.

### Next
- Apply `set_ylim(top=5.2)` (or similar) to the real script and place the intended top-of-chart elements (title/annotation/legend) into the new headroom — was explained, not yet applied/confirmed in the actual file.
- Revisit locators/formatters (`set_major_formatter`) once real data needs custom label text (e.g. `%` suffix for the 100% stacked bar's x-axis).
- `labels=` override for `bars_us` (absolute `us` counts) was explained but not yet confirmed applied/run against the live script.
- Apply the "label above bar" + y-tick-removal pattern to the live `china_mili_bars.py` script (currently only tried conceptually, not yet run by user) — including the gray "track" bar behind the value bar seen in the reference image, not yet explained.
- User hasn't yet run the `dir(ax.xaxis)` vs `dir(ax)` comparison suggested to make the Artist-tree mental model concrete.
