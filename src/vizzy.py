"""Vizzy: the public entry point. Always constructed against a caller-owned
fig/ax (matplotlib never created internally). One public method per chart
family (.line(), .bar()), each querying the Dataset and delegating to the
registered shape class. Styling/customization happens post-hoc via `.artist`,
a fluent facade that delegates to whichever chart is currently active."""

from __future__ import annotations

from src.dataset import Dataset
from src.charts.base import ChartShape, get_shape_class
from src import charts  # noqa: F401 — runs @register_shape decorators


class Artist:
    """Fluent post-hoc styling, reached via `viz.artist`. Delegates every call
    straight to whichever chart is currently active on its parent Vizzy —
    "recognizing" the chart type is plain polymorphism (each ChartShape
    subclass implements these same methods appropriately for its own
    geometry), so Artist itself has zero chart-type branching and needs no
    changes when a new shape is registered later."""

    def __init__(self, vizzy: "Vizzy") -> None:
        self._vizzy = vizzy

    @property
    def _chart(self) -> ChartShape:
        if self._vizzy._chart is None:
            raise RuntimeError("No chart yet — call viz.line(...)/viz.bar(...) before viz.artist.")
        return self._vizzy._chart

    def set_theme(self, theme: str) -> "Artist":
        self._chart.set_theme(theme)
        return self

    def set_series_color(self, key, color) -> "Artist":
        self._chart.set_series_color(key, color)
        return self

    def show_data_label(self, fmt=None, show: bool = True) -> "Artist":
        self._chart.show_data_label(fmt=fmt, show=show)
        return self

    def show_legend(self, show: bool = True) -> "Artist":
        self._chart.show_legend(show)
        return self

    def set_title(self, text: str) -> "Artist":
        self._chart.set_title(text)
        return self


class Vizzy:
    def __init__(self, fig, ax, dataset: Dataset) -> None:
        self.fig = fig
        self.ax = ax
        self.dataset = dataset
        self._chart: ChartShape | None = None
        self._artist: Artist | None = None

    @property
    def artist(self) -> Artist:
        if self._artist is None:
            self._artist = Artist(self)
        return self._artist

    def line(self, dim: str, measure: str, legend: str | None = None,
              filters: dict | None = None, shape: str = "line") -> "Vizzy":
        return self._plot(shape, dim, measure, legend, filters)

    def bar(self, dim: str, measure: str, legend: str | None = None,
             filters: dict | None = None, shape: str = "simple_bar") -> "Vizzy":
        return self._plot(shape, dim, measure, legend, filters)

    def _plot(self, shape_name: str, dim: str, measure: str, legend, filters) -> "Vizzy":
        result = self.dataset.query(dim=dim, measure=measure, legend=legend, filters=filters)
        self._chart = get_shape_class(shape_name)(fig=self.fig, ax=self.ax)
        self._chart.plot(result.categories, result.values, result.legend_categories)
        return self
