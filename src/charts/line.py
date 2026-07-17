"""Line chart shape. Handles both simple_line (no legend) and multi_line
(legend) in one class — they only differ in how many times the per-series
loop runs, not in geometry.

Standalone class now (no shared ChartShape parent). Per project-log.md:
stacking variants (stack_line, stack_100_line) are NOT built here — they
are a documented future alias that must render as filled area under the
hood, never as bare stacked lines."""

from __future__ import annotations

import numpy as np

from src.charts.base import register_shape


@register_shape("line")
class Line:
    def __init__(self, fig, ax) -> None:
        self.fig = fig
        self.ax = ax
        self._series_artists: dict = {}

    def plot(self, categories: list, values: np.ndarray, legend_categories: list | None = None):
        self._categories = categories
        x = np.arange(len(categories))
        series_list, keys = self._normalize_series(values, legend_categories)

        for i, (series, key) in enumerate(zip(series_list, keys)):
            line, = self.ax.plot(
                x, series, linewidth=2.2, marker="o", markersize=4.5,
                zorder=3, clip_on=False, label=str(key) if legend_categories else None,
            )
            self._series_artists[key] = line

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(categories)
        self.ax.set_xlim(-0.6, len(categories) - 0.4)
        if legend_categories:
            self.ax.legend()
        return self

    @staticmethod
    def _normalize_series(values: np.ndarray, legend_categories: list | None):
        if values.ndim == 1:
            return [values], [0]
        return [values[:, j] for j in range(values.shape[1])], list(legend_categories)

    def show_data_label(self) -> None:
        ...  # redo the old local-min/max-aware placement directly via ax.text()/ax.annotate()

    def set_smooth(self, *args, **kwargs) -> "Line":
        ...  # design.txt line/config/line/smooth

    def set_line_style(self, *args, **kwargs) -> "Line":
        ...  # design.txt line/config/line/shape (solid/dashed/dotted)

    def set_theme(self, theme: str = "cate-55") -> "Line":
        ...
