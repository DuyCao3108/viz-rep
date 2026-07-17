"""Bar chart shape(s). SimpleBar (vertical) and HSimpleBar (horizontal) are
independent concrete classes, not one class with an orientation flag —
each implements only the methods that make sense for its own geometry."""

from __future__ import annotations

from typing import Literal

import numpy as np

from src.charts.base import register_shape
from src.custom.colors import Pal, get_theme_colors
from src.custom.formatting import DataLabelFormat, format_value

Tone = Literal["minimal", "science"]


class Bar:
    """Bar-family plumbing plus the shared, zero-customization behavior every
    bar shape needs identically: show_data_label() and set_theme(). Both rely
    on matplotlib's BarContainer exposing a real .orientation attribute
    (vertical for ax.bar(), horizontal for ax.barh()), set as self.bars by
    each concrete class's own plot() — so "measure axis" (y for vertical, x
    for horizontal) is derived here with no per-child code beyond what plot()
    already has to do for its own geometry."""

    BAR_WIDTH = 0.6

    def __init__(self, fig, ax) -> None:
        self.fig = fig
        self.ax = ax
        self._series_artists: dict = {}

    def show_data_label(self, fmt: DataLabelFormat | None = None, thresh_hold: float | None = None) -> None:
        labels = [
            format_value(v, fmt) if thresh_hold is None or v >= thresh_hold else ""
            for v in self._values
        ]
        self.ax.bar_label(self.bars, labels=labels, label_type='edge', padding=3)

    def _measure_axis(self) -> str:
        return "y" if self.bars.orientation == "vertical" else "x"

    def _hide_spines(self) -> None:
        for spine in self.ax.spines.values():
            spine.set_visible(False)

    def _hide_measure_axis(self) -> None:
        getattr(self.ax, f"set_{self._measure_axis()}ticks")([])

    def _hide_ticks(self) -> None:
        category_axis = "x" if self._measure_axis() == "y" else "y"
        self.ax.tick_params(axis=category_axis, length=0)

    def _show_measure_axis_grid(self) -> None:
        axis = self._measure_axis()
        getattr(self.ax, f"{axis}axis").grid(True, color="#dddddd", linewidth=0.8, linestyle="-", zorder=0)
        self.ax.set_axisbelow(True)

    def set_theme(self, pal: Pal = "cate-55", tone: Tone | None = "minimal") -> "Bar":
        hex_color = get_theme_colors(pal)[0]
        for patch in self.bars.patches:
            patch.set_facecolor(hex_color)

        if tone == "minimal":
            self._hide_spines()
            self._hide_measure_axis()
            self._hide_ticks()
        elif tone == "science":
            self._show_measure_axis_grid()
        elif tone is not None:
            raise ValueError(f"Unknown tone {tone!r}. Expected one of: {Tone}")

        return self


@register_shape("simple_bar")
class SimpleBar(Bar):
    """One bar per category, no legend split. design.txt's vertical/simple_bar."""

    def plot(self, categories: list, values: np.ndarray, legend_categories: list | None = None):
        if values.ndim != 1:
            raise ValueError(
                "SimpleBar expects one value per category (no legend). "
                "Use a future GroupBar/StackBar shape for legend-split data."
            )
        self._categories, self._values = categories, values
        x = np.arange(len(categories))
        self.bars = self.ax.bar(x, values, self.BAR_WIDTH)
        self._series_artists[0] = self.bars.patches

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(categories)
        self.ax.set_xlim(-0.6, len(categories) - 0.4)
        ymax = values.max() if len(values) else 0
        self.ax.set_ylim(0, ymax * 1.18 if ymax else 1)
        return self


@register_shape("h_simple_bar")
class HSimpleBar(Bar):
    """One bar per category, no legend split. design.txt's horizontal/h_simple_bar."""

    def plot(self, categories: list, values: np.ndarray, legend_categories: list | None = None):
        ...  # mirror SimpleBar.plot but ax.barh(); categories go on y, ticks/limits swap axes

    def set_horizontal_gap(self, gap: float) -> "HSimpleBar":
        ...  # bar thickness/spacing within each category slot (barh's height=)
