"""Line chart shape. Handles both simple_line (no legend) and multi_line
(legend) in one class — they only differ in how many times the per-series
loop runs, not in geometry.

Per project-log.md: stacking variants (stack_line, stack_100_line) are NOT
built here — they are a documented future alias that must render as filled
area under the hood, never as bare stacked lines."""

from __future__ import annotations

import numpy as np

from src.charts.base import ChartShape, register_shape


@register_shape("line")
class Line(ChartShape):
    def plot(self, categories: list, values: np.ndarray, legend_categories: list | None = None):
        self._categories = categories
        x = np.arange(len(categories))
        series_list, keys = self._normalize_series(values, legend_categories)

        for i, (series, key) in enumerate(zip(series_list, keys)):
            color = self._resolve_positional_color(i)
            line, = self.ax.plot(
                x, series, color=color, linewidth=2.2, marker="o", markersize=4.5,
                markerfacecolor=color, markeredgecolor=color, zorder=3,
                clip_on=False, label=str(key) if legend_categories else None,
            )
            self._series_artists[key] = line

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(categories)
        self.ax.set_xlim(-0.6, len(categories) - 0.4)
        self.style._set_legends()
        return self

    @staticmethod
    def _normalize_series(values: np.ndarray, legend_categories: list | None):
        if values.ndim == 1:
            return [values], [0]
        return [values[:, j] for j in range(values.shape[1])], list(legend_categories)

    def _set_artist_color(self, line, color) -> None:
        line.set_color(color)
        line.set_markerfacecolor(color)
        line.set_markeredgecolor(color)

    def _draw_data_labels(self) -> None:
        self._clear_data_labels()
        x = np.arange(len(self._categories))
        self._data_label_texts = []
        for key, line in self._series_artists.items():
            y = line.get_ydata()
            span = (y.max() - y.min()) or 1.0
            off = span * 0.10
            for i, v in enumerate(y):
                local_min = 0 < i < len(y) - 1 and y[i] <= y[i - 1] and y[i] <= y[i + 1]
                dy = -off if local_min else off
                t = self.style._set_data_label(x[i], v + dy, v, ha="center",
                                               va="top" if local_min else "bottom")
                self._data_label_texts.append(t)

    def _clear_data_labels(self) -> None:
        for t in getattr(self, "_data_label_texts", []):
            t.remove()
        self._data_label_texts = []
