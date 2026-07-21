"""Vizzy: the public entry point. Always constructed against a caller-owned
fig/ax (matplotlib never created internally). One method per chart family
(.bar()/.barh()/.line()), each querying the Dataset and returning the
concrete chart object it built — no wrapping, no shared post-hoc styling
facade. Customization is whatever methods that returned object implements
directly."""

from __future__ import annotations

from src.dataset import Dataset
from src.charts.base import get_shape_class
from src.charts.bar import (
    SimpleBarH,
    SimpleBarV,
    StackBar100H,
    StackBar100V,
    StackBarH,
    StackBarV,
)
from src.charts.line import Line
from src import charts  # noqa: F401 — runs @register_shape decorators

from icecream import ic


class Vizzy:
    def __init__(self, fig, ax, dataset: Dataset) -> None:
        self.fig = fig
        self.ax = ax
        self.dataset = dataset

    def bar(self, dim: str, measure: str, legend: str | None = None,
             filters: str | None = None, sort_by: dict | None = None,
             shape: str = "simple_bar")-> SimpleBarV:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def barh(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "h_simple_bar")-> SimpleBarH:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def stack_bar(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "stack_bar")-> StackBarV:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def h_stack_bar(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "h_stack_bar") -> StackBarH:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def stack_bar_100(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "stack_100_bar")-> StackBar100V:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def h_stack_bar_100(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "h_stack_100_bar") -> StackBar100H:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def line(self, dim: str, measure: str | list[str], legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "line") -> Line:
        measure_names = [measure] if isinstance(measure, str) else list(measure)
        if len(measure_names) > 1 and legend is not None:
            raise ValueError(
                "Vizzy.line(): multi-measure mode (measure=list[str]) can't be "
                "combined with a legend. Query one measure per line, or drop legend."
            )
        results = [
            self.dataset.query(dim=dim, measure=name, legend=legend,
                                filters=filters, sort_by=sort_by)
            for name in measure_names
        ]
        chart = get_shape_class(shape)(fig=self.fig, ax=self.ax)
        chart.plot(results[0].categories, [r.values for r in results], results[0].legend_categories)
        return chart

    def _build(self, shape_name: str, dim: str, measure: str, legend, filters, sort_by=None):
        result = self.dataset.query(dim=dim, measure=measure, legend=legend,
                                     filters=filters, sort_by=sort_by)
        chart = get_shape_class(shape_name)(fig=self.fig, ax=self.ax)
        chart.plot(result.categories, result.values, result.legend_categories)
        return chart
