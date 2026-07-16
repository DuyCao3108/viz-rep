"""
Dimension/Measure data layer — a Power BI-style semantic layer over a single
flat (long-format) Polars table.

Declare Dimension/Measure once against a Dataset, then query them by name
for as many charts as needed instead of hand-shaping numpy arrays per script.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import polars as pl

AggFn = Literal["sum", "mean", "count", "min", "max", "median"]

_AGG_EXPRS = {
    "sum": pl.Expr.sum,
    "mean": pl.Expr.mean,
    "count": pl.Expr.count,
    "min": pl.Expr.min,
    "max": pl.Expr.max,
    "median": pl.Expr.median,
}


@dataclass
class Dimension:
    name: str
    column: str
    dtype: Literal["category", "date"] = "category"
    sort: list | None = None  # explicit category order; default = natural ascending


@dataclass
class Measure:
    name: str
    column: str
    agg: AggFn = "sum"


@dataclass
class QueryResult:
    categories: list
    values: np.ndarray  # 1D (dim only) or 2D shape (len(categories), len(legend_categories))
    legend_categories: list | None = None

    def to_tuple(self):
        if self.legend_categories is None:
            return self.categories, self.values
        return self.categories, self.legend_categories, self.values


class Dataset:
    def __init__(
        self,
        df: pl.DataFrame,
        dimensions: list[Dimension] = (),
        measures: list[Measure] = (),
    ):
        self.df = df
        self._dims: dict[str, Dimension] = {d.name: d for d in dimensions}
        self._measures: dict[str, Measure] = {m.name: m for m in measures}

    def add_dimension(self, dim: Dimension) -> None:
        self._dims[dim.name] = dim

    def add_measure(self, measure: Measure) -> None:
        self._measures[measure.name] = measure

    def _resolve_dim(self, name: str) -> Dimension:
        if name not in self._dims:
            raise ValueError(f"Unknown dimension {name!r}. Registered: {sorted(self._dims)}")
        return self._dims[name]

    def _resolve_measure(self, name: str) -> Measure:
        if name not in self._measures:
            raise ValueError(f"Unknown measure {name!r}. Registered: {sorted(self._measures)}")
        return self._measures[name]

    def query(
        self,
        dim: str,
        measure: str,
        legend: str | None = None,
        filters: dict[str, object] | None = None,
    ) -> QueryResult:
        dim_obj = self._resolve_dim(dim)
        legend_obj = self._resolve_dim(legend) if legend else None
        measure_obj = self._resolve_measure(measure)

        frame = self.df
        if filters:
            for column, value in filters.items():
                if isinstance(value, (list, tuple, set)):
                    frame = frame.filter(pl.col(column).is_in(list(value)))
                else:
                    frame = frame.filter(pl.col(column) == value)

        agg_expr = _AGG_EXPRS[measure_obj.agg](pl.col(measure_obj.column)).alias(measure_obj.name)
        group_cols = [dim_obj.column] + ([legend_obj.column] if legend_obj else [])
        grouped = frame.group_by(group_cols).agg(agg_expr)

        categories = dim_obj.sort or sorted(grouped[dim_obj.column].unique().to_list())

        if legend_obj is None:
            grouped = grouped.sort(dim_obj.column)
            row_by_cat = dict(zip(grouped[dim_obj.column].to_list(), grouped[measure_obj.name].to_list()))
            values = np.array([row_by_cat.get(c, 0) for c in categories], dtype=float)
            return QueryResult(categories=categories, values=values)

        wide = grouped.pivot(on=legend_obj.column, index=dim_obj.column, values=measure_obj.name)
        legend_categories = legend_obj.sort or sorted(c for c in wide.columns if c != dim_obj.column)

        wide_by_cat = {row[dim_obj.column]: row for row in wide.to_dicts()}
        values = np.zeros((len(categories), len(legend_categories)), dtype=float)
        for i, cat in enumerate(categories):
            row = wide_by_cat.get(cat, {})
            for j, leg in enumerate(legend_categories):
                v = row.get(leg)
                values[i, j] = 0.0 if v is None else v

        return QueryResult(categories=categories, legend_categories=legend_categories, values=values)


if __name__ == "__main__":
    demo = pl.DataFrame(
        {
            "quarter": ["Q1 2024", "Q1 2024", "Q2 2024", "Q2 2024"],
            "sector": ["Technology", "Healthcare", "Technology", "Healthcare"],
            "allocation": [12.0, 8.0, 14.0, 9.0],
        }
    )
    ds = Dataset(
        demo,
        dimensions=[Dimension("quarter", "quarter"), Dimension("sector", "sector")],
        measures=[Measure("allocation", "allocation", agg="mean")],
    )

    print("unfiltered:", ds.query(dim="quarter", legend="sector", measure="allocation").to_tuple())
    print("filtered:", ds.query(dim="quarter", legend="sector", measure="allocation",
                                 filters={"quarter": "Q1 2024"}).to_tuple())
    try:
        ds.query(dim="not_a_dim", measure="allocation")
    except ValueError as exc:
        print("error path ok:", exc)
