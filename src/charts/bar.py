"""Bar chart shapes, organized as a three-level tree:

    Bar                 # plumbing + shared behavior for every bar shape
    ├── SimpleBar       # shared single-series plot(), parametrized by axis
    │   ├── SimpleBarV   # vertical   (@register_shape "simple_bar")
    │   └── SimpleBarH   # horizontal (@register_shape "h_simple_bar")
    └── StackBar        # shared legend-stacked plot(), parametrized by axis
        ├── StackBarV    # vertical   (@register_shape "stack_bar")
        ├── StackBarH    # horizontal (@register_shape "h_stack_bar")
        └── StackBar100  # segments normalized to % of category total, no total label
            ├── StackBar100V  # vertical   (@register_shape "stack_100_bar")
            └── StackBar100H  # horizontal (@register_shape "h_stack_100_bar")

Vertical and horizontal bars within one family differ only in which axis
carries the dimension vs. the measure. Each leaf declares that as a class
attribute (DIM_AXIS), so each family's plot() is written once and both
orientations share it instead of being independent copies."""

from __future__ import annotations

from typing import Literal

import numpy as np
from matplotlib.backend_bases import NonGuiException
from matplotlib.ticker import FuncFormatter

from src.charts.base import register_shape
from src.custom.colors import Pal, get_theme_colors
from src.custom.formatting import (
    DataLabelFormat,
    _format_dimension,
    format_value,
    render_value,
    scale_factor,
    unit_word,
)
from src.dataset import ResultDimension, ResultLegend, ResultMeasure

Tone = Literal["minimal", "science"]


class Bar:
    """Bar-family plumbing plus the shared, zero-customization behavior every
    bar shape needs identically: show_data_label() and set_theme().

    Orientation is a declared DIM_AXIS class attribute ("x" for vertical, "y"
    for horizontal) set by each concrete leaf, so "dimension axis" and "measure
    axis" are known before anything is drawn — no reliance on the BarContainer's
    runtime .orientation, which only exists after plot()."""

    BAR_WIDTH = 0.6
    DIM_AXIS: str  # "x" (vertical) or "y" (horizontal), set by concrete leaf

    def __init__(self, fig, ax) -> None:
        self.fig = fig
        self.ax = ax
        self._series_artists: dict = {}

        self._dim_name = None
        self._mes_name = None
        self._lgd_name = None
        self._mes_fmt: DataLabelFormat | None = None
        self._mes_dedup_fmt: bool = False
        self._mes_pct_formatted: bool = False

    def _dim_axis(self) -> str:
        return self.DIM_AXIS

    def _mes_axis(self) -> str:
        return "y" if self.DIM_AXIS == "x" else "x"

    def _hide_spines(self) -> None:
        for spine in self.ax.spines.values():
            spine.set_visible(False)

    def _show_dim_spine(self):
        dim_spine_position = "bottom" if self._dim_axis() == "x" else "left"
        self.ax.spines[dim_spine_position].set_visible(True)

    def _hide_mes_axis(self) -> None:
        getattr(self.ax, f"set_{self._mes_axis()}ticks")([])

    def _hide_ticks(self) -> None:
        self.ax.tick_params(axis=self._dim_axis(), length=0)
        self.ax.tick_params(axis=self._mes_axis(), length=0)

    def _show_mes_axis_grid(self) -> None:
        axis = self._mes_axis()
        getattr(self.ax, f"{axis}axis").grid(
            True, color="#dddddd", linewidth=0.8, linestyle="-", zorder=0
        )
        self.ax.set_axisbelow(True)

    def _apply_tone(self, tone: Tone | None) -> None:
        if tone == "minimal":
            self._hide_spines()
            self._show_dim_spine()
            self._hide_mes_axis()
            self._hide_ticks()
        elif tone == "science":
            self._show_mes_axis_grid()
        elif tone is not None:
            raise ValueError(f"Unknown tone {tone!r}. Expected one of: {Tone}")

    def set_theme(self, pal: Pal = "cate-30", tone: Tone | None = "minimal") -> "Bar":
        hex_color = get_theme_colors(pal)[0]
        for patch in self.bars.patches:
            patch.set_facecolor(hex_color)

        self._apply_tone(tone)
        return self

    def _set_subtitle(self, text: str, color: str = "#888888") -> None:
        """Draws once per chart: a small note above the axes stating the unit
        data labels are shown in, e.g. "Sales (in Millions)"."""
        self.ax.text(
            0.0,
            1.02,
            text,
            transform=self.ax.transAxes,
            fontsize=9,
            color=color,
            ha="left",
            va="bottom",
        )

    def _before_plot(self):
        if self._dim_rf_obj.fmt is not None:
            self._dim_display_vals = [
                _format_dimension(v, self._dim_rf_obj.fmt)
                for v in self._dim_result_vals
            ]
        pct_fmt = self._resolve_pct_fmt()
        if pct_fmt is not None:
            self._apply_pct_format(pct_fmt)
        else:
            # Always render _mes_display_vals to display-ready strings, even
            # with no declared Measure.fmt (fmt=None still renders via
            # render_value's plain-whole-number branch) — show_data_label()
            # always uses _mes_display_vals as-is, never re-renders it.
            self._format_measure(fmt=self._mes_rf_obj.fmt)

    def _resolve_pct_fmt(self) -> DataLabelFormat | None:
        """Percent fmt to auto-render into _mes_display_vals in _before_plot(),
        or None to leave display vals as plain numbers. Driven by the
        declared Measure.fmt (dataset-side), not self._mes_fmt (the separate,
        explicit format_measure() call state)."""
        mes_fmt = self._mes_rf_obj.fmt
        return mes_fmt if mes_fmt is not None and mes_fmt.startswith("%") else None

    def _pct_display_scale(self) -> float:
        """Divisor applied before render_value() so its "%" branch (which
        expects a 0-1 fraction) sees the right scale. Plain StackBar values
        are assumed already 0-1 when %-formatted."""
        return 1.0

    def _apply_pct_format(self, fmt: DataLabelFormat) -> None:
        """The _before_plot()-time percent auto-formatter: renders every raw
        _mes_result_vals entry (of whatever shape) straight to a "NN.N%"
        string via _pct_display_scale(), independent of _format_measure()'s
        generic scale/render path. Kept separate from _format_measure() so
        that an explicit, later format_measure() call always wins outright
        (it resets _mes_pct_formatted itself) instead of this auto-detected
        default silently re-asserting itself."""
        scale = self._pct_display_scale()
        self._mes_fmt = fmt
        self._mes_dedup_fmt = False
        self._mes_display_vals = np.vectorize(
            lambda v: render_value(v / scale, fmt)
        )(self._mes_result_vals)
        self._mes_pct_formatted = True

    def _after_plot(self):
        pass

    def plot(
        self,
        dimension: ResultDimension,
        measures: ResultMeasure,
        legends: ResultLegend | None = None,
    ):
        self._dim_name = dimension.name
        self._mes_name = measures.name
        self._lgd_name = legends.name if legends is not None else None

        self._dim_rf_obj = dimension.result_from
        self._mes_rf_obj = measures.result_from
        self._lgd_rf_obj = legends.result_from if legends is not None else None

        self._dim_result_vals = dimension.value
        self._mes_result_vals = measures.value
        self._lgd_result_vals = legends.value if legends is not None else None

        self._dim_display_vals = dimension.value
        self._mes_display_vals = measures.value
        self._lgd_display_vals = legends.value if legends is not None else None

        self._before_plot()

        self._chart_plot(
            dimension=self._dim_display_vals,
            measures=self._mes_result_vals,
            legends=self._lgd_result_vals if legends is not None else None,
        )

        self._after_plot()

        return self

    def format_measure(
        self, fmt: DataLabelFormat | None = None, dedup_fmt: bool = True
    ) -> "Bar":
        """Public entry point: scales/renders _mes_display_vals from raw
        _mes_result_vals and installs a matching tick formatter, so labels
        and ticks always render in sync. Chainable — safe to call again
        anytime after plot() (e.g. Vizzy(...).bar(...).format_measure(...)
        .show_data_label())."""
        return self._format_measure(fmt=fmt, dedup_fmt=dedup_fmt)

    def _format_mes_display_vals(self, fmt: DataLabelFormat | None = None):
        """Renders every _mes_result_vals entry to its display string,
        element-wise and shape-preserving — works the same for SimpleBar's
        1D array and StackBar's 2D (category x legend) array."""
        factor = scale_factor(fmt)
        self._mes_display_vals = np.vectorize(
            lambda v: render_value(v, fmt=fmt, dedup_unit=self._mes_dedup_fmt)
        )(self._mes_result_vals / factor)

    def _format_mes_ticks(self, fmt: DataLabelFormat | None = None):
        factor = scale_factor(fmt)

        def _tick_formatter(x, pos):
            return render_value(x / factor, fmt, dedup_unit=self._mes_dedup_fmt)

        getattr(self.ax, f"{self._mes_axis()}axis").set_major_formatter(
            FuncFormatter(_tick_formatter)
        )

    def _format_val_and_ticks(self, fmt: DataLabelFormat | None = None):
        """Data-label values and measure-axis ticks are formatted together
        so they can never drift out of sync with each other."""
        self._format_mes_display_vals(fmt=fmt)
        self._format_mes_ticks(fmt=fmt)

    def _dedup_fmt(self, fmt: DataLabelFormat | None = None):
        unit = unit_word(fmt)
        self._set_subtitle(
            f"{self._mes_name} (in {unit})" if self._mes_name else f"(in {unit})"
        )

    def _format_measure(
        self, fmt: DataLabelFormat | None = None, dedup_fmt: bool = True
    ) -> "Bar":
        """Sets the measure fmt used by show_data_label() and installs a
        matching FuncFormatter on the measure axis, so labels and ticks
        always render in sync. Post-hoc / render-only: bars are always drawn
        from raw values (see plot()), so this never triggers a redraw —
        _mes_display_vals is scaled for label text, the axis formatter
        re-derives the same text per raw tick position on every draw.

        dedup_fmt only means something for scaling fmts (#,K/#,M/#,B); it's
        a no-op (not an error) otherwise, since it defaults to True."""
        self._mes_fmt = fmt
        self._mes_dedup_fmt = dedup_fmt and unit_word(fmt) is not None
        self._mes_pct_formatted = False

        self._format_val_and_ticks(fmt=fmt)

        if self._mes_dedup_fmt:
            self._dedup_fmt(fmt=fmt)

        return self

    def _chart_plot(self, dimension: list, measures: np.ndarray, legends=None) -> "Bar":
        return self


class SimpleBar(Bar):
    """One bar per category, no legend split. Shared vertical/horizontal
    plot(): the dimension axis carries the categories, the measure axis carries
    the values — which is which comes from the leaf's DIM_AXIS. Not registered;
    only its SimpleBarV/SimpleBarH leaves are concrete shapes."""

    def show_data_label(self, thresh_hold: float | None = None) -> None:
        labels = [
            dv if thresh_hold is None or rv >= thresh_hold else ""
            for rv, dv in zip(self._mes_result_vals, self._mes_display_vals)
        ]
        self.ax.bar_label(self.bars, labels=labels, label_type="edge", padding=3)

    def _chart_plot(self, dimension: list, measures: np.ndarray, legends=None):
        if measures.ndim != 1:
            raise ValueError(
                "SimpleBar expects one value per category (no legend). "
                "Use a future GroupBar/StackBar shape for legend-split data."
            )

        dim, mes = self._dim_axis(), self._mes_axis()
        pos = np.arange(len(dimension))
        self.bars = (self.ax.bar if dim == "x" else self.ax.barh)(
            pos, measures, self.BAR_WIDTH
        )

        getattr(self.ax, f"set_{dim}ticks")(pos)
        getattr(self.ax, f"set_{dim}ticklabels")(dimension)
        getattr(self.ax, f"set_{dim}lim")(-0.6, len(dimension) - 0.4)
        mmax = measures.max() if len(measures) else 0
        getattr(self.ax, f"set_{mes}lim")(0, mmax * 1.18 if mmax else 1)
        return self


@register_shape("simple_bar")
class SimpleBarV(SimpleBar):
    """Vertical single-series bar. design.txt's vertical/simple_bar."""

    DIM_AXIS = "x"


@register_shape("h_simple_bar")
class SimpleBarH(SimpleBar):
    """Horizontal single-series bar. design.txt's horizontal/h_simple_bar."""

    DIM_AXIS = "y"


class StackBar(Bar):
    """One bar per category, split into segments by a legend dimension and
    stacked along the measure axis. Shared vertical/horizontal plot(): each
    legend category gets its own BarContainer, offset by the running total of
    the segments plotted before it (bottom= for vertical, left= for
    horizontal). Not registered; only its StackBarV/StackBarH leaves are
    concrete shapes."""

    DEFAULT_THRESHOLD_PCT: float = 5

    def _chart_plot(
        self, dimension: list, measures: np.ndarray, legends: list | None = None
    ):
        if measures.ndim != 2:
            raise ValueError(
                "StackBar expects one value per category per legend category. "
                "Use SimpleBar/SimpleBarH for single-series (no legend) data."
            )
        if not legends:
            raise ValueError("StackBar requires a legend dimension.")

        dim, mes = self._dim_axis(), self._mes_axis()
        pos = np.arange(len(dimension))
        plot_fn = self.ax.bar if dim == "x" else self.ax.barh
        offset_kw = "bottom" if dim == "x" else "left"

        cumulative = np.zeros(len(dimension))
        self.bars = []
        for j, leg in enumerate(legends):
            segment = measures[:, j]
            container = plot_fn(
                pos, segment, self.BAR_WIDTH, label=str(leg), **{offset_kw: cumulative}
            )
            self.bars.append(container)
            cumulative = cumulative + segment

        getattr(self.ax, f"set_{dim}ticks")(pos)
        getattr(self.ax, f"set_{dim}ticklabels")(dimension)
        getattr(self.ax, f"set_{dim}lim")(-0.6, len(dimension) - 0.4)
        cmax = cumulative.max() if len(cumulative) else 0
        getattr(self.ax, f"set_{mes}lim")(0, cmax * 1.18 if cmax else 1)

        self.ax.legend()
        return self

    def show_data_label(
        self,
        thresh_hold: float | None = None,
        thresh_hold_pct: float | None = DEFAULT_THRESHOLD_PCT,
        show_total: bool = True,
    ) -> None:
        """thresh_hold: hide a segment whose raw value is below this absolute
        cutoff. thresh_hold_pct: hide a segment below this percent of its
        bar's total (raw_segment / row_total * 100). Both are independent
        AND-to-show checks — a segment is hidden if it fails either active
        one (None disables that check)."""
        row_totals = self._mes_result_vals.sum(axis=1)
        for j, container in enumerate(self.bars):
            raw_segment = self._mes_result_vals[:, j]
            display_segment = self._mes_display_vals[:, j]
            pct_segment = np.divide(
                raw_segment * 100,
                row_totals,
                out=np.zeros_like(raw_segment, dtype=float),
                where=row_totals != 0,
            )
            labels = [
                dv
                if (thresh_hold is None or rv >= thresh_hold)
                and (thresh_hold_pct is None or pct >= thresh_hold_pct)
                else ""
                for rv, dv, pct in zip(raw_segment, display_segment, pct_segment)
            ]
            self.ax.bar_label(
                container, labels=labels, label_type="center", color="white"
            )

        if show_total:
            self._show_total_label(thresh_hold=thresh_hold)

    def _show_total_label(self, thresh_hold: float | None = None) -> None:
        raw_totals = self._mes_result_vals.sum(axis=1)
        total_labels = [
            format_value(rv, self._mes_fmt, dedup_unit=self._mes_dedup_fmt)
            if thresh_hold is None or rv >= thresh_hold
            else ""
            for rv in raw_totals
        ]
        self.ax.bar_label(
            self.bars[-1], labels=total_labels, label_type="edge", padding=3
        )

    def set_theme(
        self, pal: Pal = "cate-30", tone: Tone | None = "minimal"
    ) -> "StackBar":
        colors = get_theme_colors(pal)
        for j, container in enumerate(self.bars):
            color = colors[j % len(colors)]
            for patch in container.patches:
                patch.set_facecolor(color)

        # legend() snapshots swatch colors at call time, so it must be redone
        # here or the legend keeps showing plot()'s pre-theme colors.
        self.ax.legend()
        self._apply_tone(tone)
        return self


@register_shape("stack_bar")
class StackBarV(StackBar):
    """Vertical stacked bar. design.txt's vertical/stack_bar."""

    DIM_AXIS = "x"


@register_shape("h_stack_bar")
class StackBarH(StackBar):
    """Horizontal stacked bar. design.txt's horizontal/h_stack_bar."""

    DIM_AXIS = "y"


class StackBar100(StackBar):
    """100%-stacked bar: same as StackBar, but each category's segments are
    normalized to percent-of-category-total before StackBar._chart_plot()
    draws them, so every bar reaches the same full length/height. Dataset's
    Dimension/Measure never know about this — normalization happens purely
    in _before_plot(), reassigning _mes_result_vals/_mes_display_vals to the
    normalized array. Everything downstream (segment drawing, axis limits,
    format_measure(), show_data_label()) is inherited from StackBar unchanged,
    since none of it assumes anything about the values' scale. Not registered;
    only its StackBar100V/StackBar100H leaves are concrete shapes.

    The percent-label formatter (StackBar._before_plot()) always fires here
    (see _resolve_pct_fmt() below), since every StackBar100 value already IS
    a percent of its bar's total — DEFAULT_PCT_FMT is the fallback precision
    when no Measure.fmt="%.x" was declared."""

    DEFAULT_PCT_FMT: DataLabelFormat = "%.1"

    def _resolve_pct_fmt(self) -> DataLabelFormat | None:
        return super()._resolve_pct_fmt() or self.DEFAULT_PCT_FMT

    def _pct_display_scale(self) -> float:
        return 100.0

    def _before_plot(self):
        row_totals = self._mes_result_vals.sum(axis=1, keepdims=True)
        normalized = np.divide(
            self._mes_result_vals * 100,
            row_totals,
            out=np.zeros_like(self._mes_result_vals),
            where=row_totals != 0,
        )
        self._mes_result_vals = normalized
        # _mes_display_vals is set below, by Bar._before_plot()'s percent
        # formatter (via super()), which always fires for StackBar100 (see
        # _resolve_pct_fmt() above) and must run against the now-normalized
        # 0-100 result vals.
        super()._before_plot()

    def show_data_label(
        self,
        thresh_hold: float | None = None,
        thresh_hold_pct: float | None = StackBar.DEFAULT_THRESHOLD_PCT,
        show_total: bool = False,
    ) -> None:
        """Same as StackBar.show_data_label(), but the 100%/total label is
        off by default — a stack that always sums to 100 doesn't need it
        called out. Still available via show_total=True."""
        super().show_data_label(
            thresh_hold=thresh_hold,
            thresh_hold_pct=thresh_hold_pct,
            show_total=show_total,
        )


@register_shape("stack_100_bar")
class StackBar100V(StackBar100):
    """Vertical 100%-stacked bar. design.txt's vertical/stack_100_bar."""

    DIM_AXIS = "x"


@register_shape("h_stack_100_bar")
class StackBar100H(StackBar100):
    """Horizontal 100%-stacked bar. design.txt's horizontal/h_stack_100_bar."""

    DIM_AXIS = "y"
