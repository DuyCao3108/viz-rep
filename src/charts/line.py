"""Line chart shape. A single Line object can render multiple lines from
either of two sources: multiple measures (looped, no legend) or one measure
split by a legend dimension. Per-series state lives in self._mes_maps, keyed
by measure name (multi-measure mode) or "{measure_name}_{legend_label}"
(legend mode) — see plot()/_build_mes_maps().

Standalone class now (no shared ChartShape/Bar parent — see project-log.md's
"no shared base class across families" decision). Per project-log.md:
stacking variants (stack_line, stack_100_line) are NOT built here — they
are a documented future alias that must render as filled area under the
hood, never as bare stacked lines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from matplotlib.ticker import FuncFormatter
from scipy.interpolate import make_interp_spline

from src.charts.base import register_shape
from src.custom.colors import Pal, get_theme_colors
from src.custom.formatting import (
    DataLabelFormat,
    _format_dimension,
    render_value,
    scale_factor,
    unit_word,
)
from src.dataset import ResultDimension, ResultLegend, ResultMeasure

Tone = Literal["minimal", "science"]


@dataclass
class AdjustPos:
    """Manual data-label nudge for show_data_label(adjust_pos=[...]).
    at_dimension_val matches against the dimension's *display* value (post-
    Dimension.fmt, e.g. "26-Q2" for a "yy-qq"-formatted quarter). of_measure/
    of_legend optionally scope the match to one series — the declared
    measure name (multi-measure mode) or legend label (legend-split mode);
    leave unset to match that dimension value across every series. pad_v/
    pad_h are added to the default (0, 8) offset-points annotation offset."""

    at_dimension_val: str
    of_measure: str | None = None
    of_legend: str | None = None
    pad_v: int = 0
    pad_h: int = 0


@dataclass
class LegendLabelAdjustPos:
    """Manual on-line legend-label nudge for adjust_legend_label_pos(...).
    Matches a _mes_maps entry by of_measure (multi-measure mode) or
    of_legend (legend-split mode) — no at_dimension_val, since legend
    labels are per-series, not per-dimension-value. pad_h/pad_v additively
    shift that entry's placed legend_annotation offset."""

    of_measure: str | None = None
    of_legend: str | None = None
    pad_h: int = 0
    pad_v: int = 0


@register_shape("line")
class Line:
    def __init__(self, fig, ax) -> None:
        self.fig = fig
        self.ax = ax

        self._dim_name = None
        self._dim_rf_obj = None
        self._dim_result_vals = None
        self._dim_display_vals = None

        self._mes_maps: dict[str, dict] = {}
        self._legend_mode: bool = False
        self._show_legend: bool = False

        self._mes_fmt: DataLabelFormat | None = None
        self._mes_dedup_fmt: bool = False

        self._line_style: str = "default"
        self._smooth: bool = False

    def plot(
        self,
        dimension: ResultDimension,
        measures: list[ResultMeasure],
        legends: ResultLegend | None = None,
    ) -> "Line":
        self._validate_inputs(measures, legends)

        self._dim_name = dimension.name
        self._dim_rf_obj = dimension.result_from
        self._dim_result_vals = dimension.value
        self._dim_display_vals = dimension.value

        self._legend_mode = legends is not None
        self._mes_maps = self._build_mes_maps(measures, legends)

        self._before_plot()
        self._chart_plot()
        self._after_plot()
        return self

    @staticmethod
    def _validate_inputs(measures: list[ResultMeasure], legends: ResultLegend | None) -> None:
        if legends is not None:
            if len(measures) != 1:
                raise ValueError(
                    "Line with a legend requires exactly one measure, got "
                    f"{len(measures)}. Use multi-measure mode (no legend) instead."
                )
        elif len(measures) < 1:
            raise ValueError("Line requires at least one measure.")

    @staticmethod
    def _build_mes_maps(
        measures: list[ResultMeasure], legends: ResultLegend | None
    ) -> dict[str, dict]:
        if legends is None:
            mes_maps = {}
            for m in measures:
                if m.value.ndim != 1:
                    raise ValueError(
                        f"Line measure {m.name!r} expects one value per category "
                        "(no legend). Pass a legend to split a single measure instead."
                    )
                mes_maps[m.name] = {
                    "result_from": m.result_from,
                    "result_vals": m.value,
                    "display_vals": m.value,
                    "legend_label": None,
                    "line": None,
                    "legend_annotation": None,
                }
            return mes_maps

        m = measures[0]
        if m.value.ndim != 2 or m.value.shape[1] != len(legends.value):
            raise ValueError(
                f"Line measure {m.name!r} expects one value per category per legend "
                "category when a legend is given."
            )
        mes_maps = {}
        for j, label in enumerate(legends.value):
            mes_maps[f"{m.name}_{label}"] = {
                "result_from": m.result_from,
                "result_vals": m.value[:, j],
                "display_vals": m.value[:, j],
                "legend_label": label,
                "line": None,
                "legend_annotation": None,
            }
        return mes_maps

    def _entry_pct_fmt(self, entry: dict) -> DataLabelFormat | None:
        """The entry's declared Measure.fmt, if it's a "%" token — an
        override point for a future stack_100_line to inject a default
        percent fmt when none is declared, mirroring
        StackBar100._resolve_pct_fmt() in src/charts/bar.py. Per-entry (not
        chart-wide) since multi-measure mode can mix series with different
        declared fmts."""
        mes_fmt = entry["result_from"].fmt
        return mes_fmt if mes_fmt is not None and mes_fmt.startswith("%") else None

    def _pct_display_scale(self) -> float:
        """Divisor applied before render_value() so its "%" branch (which
        expects a 0-1 fraction) sees the right scale. Plain Line values are
        assumed already 0-1 when %-formatted. Overridable the same way
        StackBar100._pct_display_scale() is, for a future stack_100_line."""
        return 1.0

    def _render_entry_display_vals(
        self, entry: dict, fmt: DataLabelFormat | None, dedup_fmt: bool = False
    ) -> None:
        """The one place an entry's raw result_vals get rendered to a
        display-ready string array — reused by both the auto _before_plot()
        pass and the explicit format_measure() call, so the two can never
        drift apart (mirrors Bar._format_mes_display_vals())."""
        scale = (
            self._pct_display_scale()
            if fmt is not None and fmt.startswith("%")
            else scale_factor(fmt)
        )
        entry["display_vals"] = np.vectorize(
            lambda v: render_value(v / scale, fmt, dedup_unit=dedup_fmt)
        )(entry["result_vals"])

    def _format_mes_ticks(self, fmt: DataLabelFormat | None) -> None:
        factor = scale_factor(fmt)

        def _tick_formatter(x, pos):
            return render_value(x / factor, fmt, dedup_unit=self._mes_dedup_fmt)

        self.ax.yaxis.set_major_formatter(FuncFormatter(_tick_formatter))

    def _auto_bind_ticks(self) -> None:
        """Binds the y-axis tick formatter automatically only when there's
        one unambiguous fmt for the whole chart: a single entry, or every
        entry sharing the same declared fmt (always true in legend-split
        mode, since every entry there shares one underlying measure). Left
        unbound (default matplotlib ticks) for genuine multi-measure mode
        with differing declared fmts across series — no single fmt to guess,
        a documented limitation rather than an arbitrary pick."""
        fmts = {entry["result_from"].fmt for entry in self._mes_maps.values()}
        if len(fmts) != 1:
            return
        self._format_mes_ticks(next(iter(fmts)))

    def _before_plot(self) -> None:
        if self._dim_rf_obj.fmt is not None:
            self._dim_display_vals = [
                _format_dimension(v, self._dim_rf_obj.fmt) for v in self._dim_result_vals
            ]

        for entry in self._mes_maps.values():
            fmt = self._entry_pct_fmt(entry) or entry["result_from"].fmt
            self._render_entry_display_vals(entry, fmt, dedup_fmt=False)

        self._auto_bind_ticks()

    def _after_plot(self) -> None:
        self._set_theme()
        self._set_line_style()

    def _series_label(self, entry: dict) -> str | None:
        if self._legend_mode:
            return str(entry["legend_label"])
        if len(self._mes_maps) > 1:
            return entry["result_from"].name
        return None

    def _chart_plot(self) -> "Line":
        x = np.arange(len(self._dim_display_vals))
        for entry in self._mes_maps.values():
            (line,) = self.ax.plot(
                x, entry["result_vals"], linewidth=2.2, marker="o", markersize=4.5,
                zorder=3, clip_on=False, label=self._series_label(entry),
            )
            entry["line"] = line

        self._show_legend = self._legend_mode or len(self._mes_maps) > 1
        if self._show_legend:
            self.ax.legend()

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self._dim_display_vals)
        self.ax.set_xlim(-0.6, len(self._dim_display_vals) - 0.4)

        self._set_mes_scale()
        return self

    def _find_smart_scale(self) -> tuple[float, float]:
        """Min/max raw value across every currently-plotted series (all
        entries in self._mes_maps) — the "whole ax" range set_mes_scale()
        zooms to by default."""
        all_vals = np.concatenate(
            [entry["result_vals"] for entry in self._mes_maps.values()]
        )
        return float(all_vals.min()), float(all_vals.max())

    def _set_mes_scale(
        self,
        ylim: tuple[float, float] | None = None,
        n_step: int = 5,
        std: float = 0.05,
    ) -> None:
        """Zooms the y-axis to (ylim or _find_smart_scale()'s detected
        min/max), padded by std as a fraction of the value span on each
        side, with n_step major tick intervals. Guards the degenerate
        all-equal-value case (span == 0) so set_ylim never gets a
        zero-width range."""
        vmin, vmax = ylim if ylim is not None else self._find_smart_scale()
        span = vmax - vmin
        pad = span * std if span else (abs(vmax) * std if vmax else 0.5)
        actual_min, actual_max = vmin - pad, vmax + pad
        self.ax.set_ylim(actual_min, actual_max)
        self.ax.set_yticks(np.linspace(actual_min, actual_max, n_step + 1))

    def set_mes_scale(
        self,
        ylim: tuple[float, float] | None = None,
        n_step: int = 5,
        std: float = 0.05,
    ) -> "Line":
        """Public, chainable override of the y-axis zoom plot() already
        applied by default. All args optional — ylim=None re-detects the
        smart min/max, n_step/std keep their defaults unless given."""
        self._set_mes_scale(ylim=ylim, n_step=n_step, std=std)
        return self

    def _subtitle_measure_label(self) -> str:
        names = {entry["result_from"].name for entry in self._mes_maps.values()}
        return next(iter(names)) if len(names) == 1 else "Values"

    def _dedup_fmt(self, fmt: DataLabelFormat | None) -> None:
        unit = unit_word(fmt)
        self._set_subtitle(f"{self._subtitle_measure_label()} (in {unit})")

    def _format_measure(
        self, fmt: DataLabelFormat | None = None, dedup_fmt: bool = True
    ) -> "Line":
        self._mes_fmt = fmt
        self._mes_dedup_fmt = dedup_fmt and unit_word(fmt) is not None

        for entry in self._mes_maps.values():
            self._render_entry_display_vals(entry, fmt, dedup_fmt=self._mes_dedup_fmt)

        self._format_mes_ticks(fmt)

        if self._mes_dedup_fmt:
            self._dedup_fmt(fmt)

        return self

    def format_measure(self, fmt: DataLabelFormat | None = None, dedup_fmt: bool = True) -> "Line":
        """Public entry point: sets the shared measure fmt used by
        show_data_label() and installs a matching FuncFormatter on the
        measure (y) axis — one fmt/scale for the whole chart, since every
        series shares one measure axis. Post-hoc / render-only: lines are
        always drawn from raw values (see plot()), this only rewrites
        _mes_maps[...]["display_vals"] and the tick text. Chainable — safe
        to call again anytime after plot()."""
        return self._format_measure(fmt=fmt, dedup_fmt=dedup_fmt)

    @staticmethod
    def _matches_adjust(ap: AdjustPos, entry: dict, dim_val) -> bool:
        if ap.at_dimension_val != dim_val:
            return False
        if ap.of_measure is not None and ap.of_measure != entry["result_from"].name:
            return False
        if ap.of_legend is not None and ap.of_legend != entry["legend_label"]:
            return False
        return True

    def _validate_adjust_pos(self, adjust_pos: list[AdjustPos]) -> None:
        unmatched = [
            ap for ap in adjust_pos
            if not any(
                self._matches_adjust(ap, entry, dim_val)
                for entry in self._mes_maps.values()
                for dim_val in self._dim_display_vals
            )
        ]
        if unmatched:
            raise ValueError(
                "show_data_label(adjust_pos=...): no label matched for: "
                + "; ".join(repr(ap) for ap in unmatched)
            )

    def show_data_label(self, adjust_pos: list[AdjustPos] | None = None) -> None:
        if adjust_pos:
            self._validate_adjust_pos(adjust_pos)
        x = np.arange(len(self._dim_display_vals))
        for entry in self._mes_maps.values():
            color = entry["line"].get_color()
            for xi, rv, dv, dim_val in zip(
                x, entry["result_vals"], entry["display_vals"], self._dim_display_vals
            ):
                pad_v, pad_h = 0, 0
                if adjust_pos:
                    match = next(
                        (ap for ap in adjust_pos if self._matches_adjust(ap, entry, dim_val)),
                        None,
                    )
                    if match is not None:
                        pad_v, pad_h = match.pad_v, match.pad_h
                self.ax.annotate(
                    dv, xy=(xi, rv), xytext=(pad_h, 8 + pad_v), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, color='black',
                )

    def _hide_spines(self) -> None:
        for spine in self.ax.spines.values():
            spine.set_visible(False)

    def _show_dim_spine(self) -> None:
        self.ax.spines["bottom"].set_visible(True)

    def _show_mes_spine(self) -> None:
        self.ax.spines["left"].set_visible(True)

    def _show_mes_grid(self, style: str = "default") -> None:
        linestyle = "-" if style == "default" else style
        self.ax.yaxis.grid(True, color="gray", linewidth=0.8, linestyle=linestyle, zorder=0)
        self.ax.set_axisbelow(True)

    def _apply_tone(self, tone: Tone | None) -> None:
        if tone == "minimal":
            self._hide_spines()
            self._show_dim_spine()
            self._show_mes_spine()
            # self._show_mes_grid()
        elif tone == "science":
            pass  # explicitly skipped for now, per spec — not an error
        elif tone is not None:
            raise ValueError(f"Unknown tone {tone!r}. Expected one of: {Tone}")

    def _set_theme(self, pal: Pal = "cate-30", tone: Tone | None = "minimal") -> "Line":
        colors = get_theme_colors(pal)
        for j, entry in enumerate(self._mes_maps.values()):
            color = colors[j % len(colors)]
            entry["line"].set_color(color)
            entry["line"].set_markerfacecolor(color)
            entry["line"].set_markeredgecolor(color)

        # legend() snapshots handle colors at call time, so it must be redone
        # here or the legend keeps showing plot()'s pre-theme colors (same
        # fix as StackBar.set_theme()).
        if self._show_legend:
            self.ax.legend()

        self._apply_tone(tone)
        return self

    def set_theme(self, pal: Pal = "cate-30", tone: Tone | None = "minimal") -> "Line":
        """Public, chainable override of the default theme _after_plot()
        already applied automatically. Calling this again anytime after
        plot() overwrites the prior theme (same auto-default + explicit-
        override pattern as format_measure()/set_mes_scale())."""
        return self._set_theme(pal=pal, tone=tone)

    def set_legend(
        self, line_pos: Literal["end", "begin"] | None = None, style: str = "default"
    ) -> "Line":
        """Works per-ax (this Line's own ax only). line_pos places each
        series' label directly on its line instead of drawing the standard
        ax.legend() box; omit it (style default "default") for the standard
        legend."""
        if line_pos is not None:
            self._set_legend_on_line(line_pos)
        else:
            self._set_legend_style(style)
        return self

    def _set_legend_style(self, style: str = "default") -> None:
        if style == "default":
            self.ax.legend(loc="upper left")
        else:
            raise ValueError(f"Unknown legend style {style!r}. Expected one of: ['default']")

    def _set_legend_on_line(self, line_pos: Literal["end", "begin"]) -> None:
        if line_pos not in ("end", "begin"):
            raise ValueError(f"Unknown line_pos {line_pos!r}. Expected 'end' or 'begin'.")

        legend = self.ax.get_legend()
        if legend is not None:
            legend.remove()

        x = np.arange(len(self._dim_display_vals))
        for entry in self._mes_maps.values():
            label = self._series_label(entry) or entry["result_from"].name
            color = entry["line"].get_color()
            if line_pos == "end":
                xi, yi = x[-1], entry["result_vals"][-1]
                xytext, ha, va = (8, 0), "left", "center"
            else:
                xi, yi = x[0], entry["result_vals"][0]
                xytext, ha, va = (0, 8), "center", "bottom"

            entry["legend_annotation"] = self.ax.annotate(
                label, xy=(xi, yi), xytext=xytext, textcoords="offset points",
                ha=ha, va=va, fontsize=9, color=color, fontweight="bold",
                annotation_clip=False,
            )

    @staticmethod
    def _matches_legend_adjust(lap: LegendLabelAdjustPos, entry: dict) -> bool:
        if lap.of_measure is not None and lap.of_measure != entry["result_from"].name:
            return False
        if lap.of_legend is not None and lap.of_legend != entry["legend_label"]:
            return False
        return True

    def _validate_legend_label_adjust_pos(self, adjustments: list[LegendLabelAdjustPos]) -> None:
        unmatched = [
            lap for lap in adjustments
            if not any(self._matches_legend_adjust(lap, entry) for entry in self._mes_maps.values())
        ]
        if unmatched:
            raise ValueError(
                "adjust_legend_label_pos(): no series matched for: "
                + "; ".join(repr(lap) for lap in unmatched)
            )

    def adjust_legend_label_pos(self, adjustments: list[LegendLabelAdjustPos]) -> "Line":
        if not adjustments:
            return self
        self._validate_legend_label_adjust_pos(adjustments)

        for entry in self._mes_maps.values():
            ann = entry.get("legend_annotation")
            if ann is None:
                continue
            for lap in adjustments:
                if self._matches_legend_adjust(lap, entry):
                    dx, dy = ann.xyann
                    ann.xyann = (dx + lap.pad_h, dy + lap.pad_v)
        return self

    def _smoothen_line(self) -> None:
        """Replaces each series' straight-segment line with a spline-smoothed
        curve plus markers at the real points — ax.plot only connects
        whatever points it's given, so smoothing means feeding it denser
        interpolated points instead of the raw ones."""
        x = np.arange(len(self._dim_display_vals))
        for entry in self._mes_maps.values():
            y = entry["result_vals"]
            color = entry["line"].get_color()
            entry["line"].remove()

            k = min(3, len(x) - 1)
            x_smooth = np.linspace(x.min(), x.max(), 300)
            y_smooth = make_interp_spline(x, y, k=k)(x_smooth)

            (line,) = self.ax.plot(
                x_smooth, y_smooth, linewidth=2.2, zorder=3, clip_on=False, color=color,
            )
            self.ax.plot(x, y, "o", markersize=4.5, zorder=3, clip_on=False, color=color)
            entry["line"] = line

    def set_line_style(self, style: str = "default", smooth: bool = False) -> "Line":
        self._set_line_style(style=style,smooth=smooth)

    def _set_line_style(self, style: str = "default", smooth: bool = False) -> "Line":
        self._smooth = smooth
        self._line_style = style

        if style == "default":
            for entry in self._mes_maps.values():
                entry["line"].set_marker("o")
                entry["line"].set_markersize(4.5)
                entry["line"].set_linewidth(2.6)

        if smooth:
            self._smoothen_line()

        return self

    def _set_subtitle(self, text: str, color: str = "#888888") -> None:
        self.ax.text(
            0.0, 1.02, text,
            transform=self.ax.transAxes,
            fontsize=9, color=color, ha="left", va="bottom",
        )
