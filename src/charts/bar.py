"""Bar chart shapes, organized as a three-level tree:

    Bar                 # plumbing + shared behavior for every bar shape
    ├── SimpleBar       # shared single-series plot(), parametrized by axis
    │   ├── SimpleBarV   # vertical   (@register_shape "simple_bar")
    │   └── SimpleBarH   # horizontal (@register_shape "h_simple_bar")
    └── StackBar        # shared legend-stacked plot(), parametrized by axis
        ├── StackBarV    # vertical   (@register_shape "stack_bar")
        └── StackBarH    # horizontal (@register_shape "h_stack_bar")

Vertical and horizontal bars within one family differ only in which axis
carries the dimension vs. the measure. Each leaf declares that as a class
attribute (DIM_AXIS), so each family's plot() is written once and both
orientations share it instead of being independent copies."""

from __future__ import annotations

from typing import Literal

from matplotlib.backend_bases import NonGuiException
import numpy as np

from src.charts.base import register_shape
from src.custom.colors import Pal, get_theme_colors
from src.custom.formatting import DataLabelFormat, format_value

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

        self._dimensions=None
        self._measures=None
        self._legends=None

    def _dim_axis(self) -> str:
        return self.DIM_AXIS

    def _mes_axis(self) -> str:
        return "y" if self.DIM_AXIS == "x" else "x"

    def _hide_spines(self) -> None:
        for spine in self.ax.spines.values():
            spine.set_visible(False)

    def _show_dim_spine(self):
        dim_spine_position='bottom' if self._dim_axis()=='x' else 'left'
        self.ax.spines[dim_spine_position].set_visible(True)

    def _hide_mes_axis(self) -> None:
        getattr(self.ax, f"set_{self._mes_axis()}ticks")([])

    def _hide_ticks(self) -> None:
        self.ax.tick_params(axis=self._dim_axis(), length=0)
        self.ax.tick_params(axis=self._mes_axis(), length=0)

    def _show_mes_axis_grid(self) -> None:
        axis = self._mes_axis()
        getattr(self.ax, f"{axis}axis").grid(True, color="#dddddd", linewidth=0.8, linestyle="-", zorder=0)
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

    def set_theme(self, pal: Pal = "cate-55", tone: Tone | None = "minimal") -> "Bar":
        hex_color = get_theme_colors(pal)[0]
        for patch in self.bars.patches:
            patch.set_facecolor(hex_color)

        self._apply_tone(tone)
        return self


class SimpleBar(Bar):
    """One bar per category, no legend split. Shared vertical/horizontal
    plot(): the dimension axis carries the categories, the measure axis carries
    the values — which is which comes from the leaf's DIM_AXIS. Not registered;
    only its SimpleBarV/SimpleBarH leaves are concrete shapes."""

    def show_data_label(self, fmt: DataLabelFormat | None = None, thresh_hold: float | None = None) -> None:
        labels = [
            format_value(v, fmt) if thresh_hold is None or v >= thresh_hold else ""
            for v in self._measures
        ]
        self.ax.bar_label(self.bars, labels=labels, label_type='edge', padding=3)

    def plot(self, dimension: list, measures: np.ndarray, legends=None):
        if measures.ndim != 1:
            raise ValueError(
                "SimpleBar expects one value per category (no legend). "
                "Use a future GroupBar/StackBar shape for legend-split data."
            )
        self._dimensions, self._measures = dimension, measures

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

    def plot(self, dimension: list, measures: np.ndarray, legends: list | None = None):
        if measures.ndim != 2:
            raise ValueError(
                "StackBar expects one value per category per legend category. "
                "Use SimpleBar/SimpleBarH for single-series (no legend) data."
            )
        if not legends:
            raise ValueError("StackBar requires a legend dimension.")
        self._dimensions, self._measures, self._legends = dimension, measures, legends

        dim, mes = self._dim_axis(), self._mes_axis()
        pos = np.arange(len(dimension))
        plot_fn = self.ax.bar if dim == "x" else self.ax.barh
        offset_kw = "bottom" if dim == "x" else "left"

        cumulative = np.zeros(len(dimension))
        self.bars = []
        for j, leg in enumerate(legends):
            segment = measures[:, j]
            container = plot_fn(pos, segment, self.BAR_WIDTH, label=str(leg), **{offset_kw: cumulative})
            self.bars.append(container)
            cumulative = cumulative + segment

        getattr(self.ax, f"set_{dim}ticks")(pos)
        getattr(self.ax, f"set_{dim}ticklabels")(dimension)
        getattr(self.ax, f"set_{dim}lim")(-0.6, len(dimension) - 0.4)
        cmax = cumulative.max() if len(cumulative) else 0
        getattr(self.ax, f"set_{mes}lim")(0, cmax * 1.18 if cmax else 1)

        self.ax.legend()
        return self

    def show_data_label(self, fmt: DataLabelFormat | None = None, thresh_hold: float | None = None) -> None:
        for j, container in enumerate(self.bars):
            segment = self._measures[:, j]
            labels = [
                format_value(v, fmt) if thresh_hold is None or v >= thresh_hold else ""
                for v in segment
            ]
            self.ax.bar_label(container, labels=labels, label_type="center")

    def set_theme(self, pal: Pal = "cate-55", tone: Tone | None = "minimal") -> "StackBar":
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
