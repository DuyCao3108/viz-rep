"""Bar chart shape(s). This pass implements SimpleBar only (design.txt's
vertical/simple_bar), proving the architecture isn't hardcoded to Line.
StackBar/GroupBar/... are documented extension points, not built here."""

from __future__ import annotations

import numpy as np

from src.charts.base import ChartShape, register_shape
from src.styles import _light


class Bar(ChartShape):
    """Shared bar-family behavior (width, Power BI-style fill/edge convention)
    that every bar shape variant subclasses."""

    bar_width = 0.6

    def _bar_style(self, color) -> dict:
        return dict(facecolor=_light(color), edgecolor=color, linewidth=1.1)

    def _set_artist_color(self, patches, color) -> None:
        for p in patches:
            p.set_facecolor(_light(color))
            p.set_edgecolor(color)


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
        color = self._resolve_positional_color(0)
        bars = self.ax.bar(x, values, self.bar_width, **self._bar_style(color))
        self._series_artists[0] = bars.patches

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(categories)
        self.ax.set_xlim(-0.6, len(categories) - 0.4)
        ymax = values.max() if len(values) else 0
        self.ax.set_ylim(0, ymax * 1.18 if ymax else 1)
        return self

    def _draw_data_labels(self) -> None:
        self._clear_data_labels()
        ymax = self._values.max() if len(self._values) else 0
        self._data_label_texts = [
            self.style._set_data_label(i, v + ymax * 0.02, v, ha="center", va="bottom")
            for i, v in enumerate(self._values)
        ]

    def _clear_data_labels(self) -> None:
        for t in getattr(self, "_data_label_texts", []):
            t.remove()
        self._data_label_texts = []
