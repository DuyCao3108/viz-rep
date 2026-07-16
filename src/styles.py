"""Default styling applied to every chart, encapsulating the Power BI-style
visual vocabulary validated in sandbox/build_report.py (bare axes, muted
title/axis colors, saturated-at-40%-alpha bar fills)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import matplotlib
import matplotlib.pyplot as plt

from src.fonts import FONT_FALLBACK_POWERBI, resolve_installed_font

DEFAULT_COLOR_ROLES: dict[str, str] = {
    "title": "#605E5C",
    "data_label": "#252423",
    "axis_label": "#3B3B3B",
}

DEFAULT_FONT_SIZES: dict[str, float] = {
    "title": 12,
    "legend": 10,
    "data_label": 10.5,
    "axis_label": 9.5,
}


@dataclass
class DefaultStyle:
    """Applies default spines/font/color/data-label/legend conventions to one Axes.

    One instance is owned per ChartShape instance. Holds the *resolved* style
    state for that chart, mutated in place by ChartShape's mutator methods
    (set_theme, show_data_label, etc.) rather than re-created per call.
    """

    ax: plt.Axes
    theme_colors: list[str]
    color_roles: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_COLOR_ROLES))
    font_sizes: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_FONT_SIZES))
    font_family: str = resolve_installed_font(
        FONT_FALLBACK_POWERBI["sans"], "Helvetica Neue", "Arial", "sans-serif"
    )
    data_label_fmt: Callable[[float], str] = lambda v: f"{v:.0f}"
    show_legend: bool = True

    def __post_init__(self) -> None:
        self._set_font()
        self._set_spines()
        self._set_color()

    def _set_font(self) -> None:
        # tick_params (not mutating existing Text objects) so this survives
        # shapes later calling set_xticks()/set_xticklabels() with real data —
        # those can recreate tick label artists, which would silently drop
        # any font set directly on the old Text objects.
        self.ax.tick_params(labelfontfamily=self.font_family)

    def _set_spines(self) -> None:
        # build_report.py's bare(ax): no spines, no y ticks, x ticks with zero length
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.ax.set_yticks([])
        self.ax.tick_params(axis="x", length=0, labelsize=self.font_sizes["axis_label"],
                             labelcolor=self.color_roles["axis_label"])

    def _set_color(self) -> None:
        from cycler import cycler
        self.ax.set_prop_cycle(cycler(color=self.theme_colors))

    def _set_mes_axis_title(self, text: str) -> None:
        # build_report.py's title(): axes-fraction text above the plot area
        self.ax.text(0.0, 1.16, text, transform=self.ax.transAxes, ha="left", va="baseline",
                     fontsize=self.font_sizes["title"], color=self.color_roles["title"],
                     fontfamily=self.font_family, clip_on=False)

    def _set_data_label(self, x, y, value, **text_kwargs):
        # returns the Text artist so callers (Line/SimpleBar's _draw_data_labels)
        # can keep a handle to it and .remove() it later when toggled off
        kwargs = dict(fontsize=self.font_sizes["data_label"], color=self.color_roles["data_label"],
                      fontfamily=self.font_family)
        kwargs.update(text_kwargs)
        return self.ax.text(x, y, self.data_label_fmt(value), **kwargs)

    def _set_legends(self) -> None:
        # Plain styled ax.legend() — no pixel-math/renderer dependency.
        # build_report.py's hand-drawn horizontal token legend (hlegend()) is a
        # documented drop-in replacement later: callers only depend on
        # _set_legends() being called after all series are drawn with label=,
        # never on how it renders internally.
        if not self.show_legend:
            return
        handles, labels = self.ax.get_legend_handles_labels()
        if not handles:
            return
        self.ax.legend(handles, labels, loc="upper left", bbox_to_anchor=(0, 1.12),
                       ncol=len(labels), frameon=False, fontsize=self.font_sizes["legend"],
                       labelcolor=self.color_roles["data_label"])


def _light(color, alpha: float = 0.40):
    """Power BI bar fill = saturated color drawn at ~40% alpha over white."""
    r, g, b = matplotlib.colors.to_rgb(color)
    return (r * alpha + (1 - alpha), g * alpha + (1 - alpha), b * alpha + (1 - alpha))
