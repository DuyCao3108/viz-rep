"""Vizzy: the public entry point. Always constructed against a caller-owned
fig/ax (matplotlib never created internally). One method per chart family
(.bar()/.barh()/.line()), each querying the Dataset and returning the
concrete chart object it built — no wrapping, no shared post-hoc styling
facade. Customization is whatever methods that returned object implements
directly."""

from __future__ import annotations

from src.dataset import Dataset
from src.charts.base import get_shape_class
from src import charts  # noqa: F401 — runs @register_shape decorators


class Vizzy:
    def __init__(self, fig, ax, dataset: Dataset) -> None:
        self.fig = fig
        self.ax = ax
        self.dataset = dataset

    def bar(self, dim: str, measure: str, legend: str | None = None,
             filters: dict | None = None, shape: str = "simple_bar"):
        return self._build(shape, dim, measure, legend, filters)

    def barh(self, dim: str, measure: str, legend: str | None = None,
              filters: dict | None = None, shape: str = "h_simple_bar"):
        return self._build(shape, dim, measure, legend, filters)

    def line(self, dim: str, measure: str, legend: str | None = None,
              filters: dict | None = None, shape: str = "line"):
        return self._build(shape, dim, measure, legend, filters)

    def _build(self, shape_name: str, dim: str, measure: str, legend, filters):
        result = self.dataset.query(dim=dim, measure=measure, legend=legend, filters=filters)
        chart = get_shape_class(shape_name)(fig=self.fig, ax=self.ax)
        chart.plot(result.categories, result.values, result.legend_categories)
        return chart
