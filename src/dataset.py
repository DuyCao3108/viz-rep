"""
Dimension/Measure data layer — a Power BI-style semantic layer over a single
DuckDB-backed parquet file.

Dataset loads exactly one parquet file (no in-memory frames, no other
options yet — that's deliberate, see Dataset.__init__). Every column of the
file is a dimension by default; measures are declared afterward as raw SQL
aggregate expressions (which may reference other measures by name, DAX-
style, e.g. "{other_measure}/{total}") and calculated (derived) dimension
columns as raw SQL expressions too. dim/legend are just group-by columns,
measures are SQL aggregates, filters are a raw SQL WHERE-clause string —
query() turns all of that into one DuckDB SQL query, then reshapes the
result into the same QueryResult/ResultDimension/ResultMeasure/ResultLegend
shapes the chart layer already consumes.

Performance note (import mode): the first query() call materializes the
parquet file into a native in-memory DuckDB table once; every subsequent
query() reuses that table instead of re-decoding the file from disk, so one
Dataset queried many times (a gallery run, a multi-measure line chart) pays
the file-decode cost once, not per call. If production queries commonly
filter on one column (date range, region, ...), Hive-partitioning the
source parquet by that column upstream lets DuckDB skip whole files before
this table is even built — a data-prep concern, not something Dataset
itself does.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import duckdb
import numpy as np
import polars as pl

from src.custom.formatting import DataLabelFormat, DimensionFormat

PbiComponents = Literal["dim", "mes", "legend"]
SortOptions = Literal["asc", "desc"]

_MEASURE_REF_RE = re.compile(r"\{([^{}]+)\}")
_DATE_TYPE_PREFIXES = ("DATE", "TIMESTAMP")


@dataclass
class Dimension:
    name: str
    column: str | None = None
    dtype: Literal["category", "date"] = "category"
    fmt: DimensionFormat | None = None
    transform: str | None = (
        None  # SQL expression for a calculated column; None for a plain source column
    )

    def __post_init__(self):
        if self.column is None:
            self.column = self.name


@dataclass
class Measure:
    name: str
    formula: str  # raw SQL aggregate expression; may reference other measures via "{other_name}"
    fmt: DataLabelFormat | None = None

    # For high-cardinality distinct counts (e.g. count(distinct customer_id)
    # over millions of rows), prefer DuckDB's approx_count_distinct(...) —
    # a HyperLogLog-based approximation that's dramatically cheaper than an
    # exact count(distinct ...) at large scale. No Dataset changes needed:
    # formula is raw SQL, so this is just a different function call, e.g.
    # Measure("distinct_customers", "approx_count_distinct(customer_id)").


@dataclass
class ResultArray:
    name: str


@dataclass
class ResultDimension(ResultArray):
    value: list
    result_from: Dimension


@dataclass
class ResultMeasure(ResultArray):
    value: np.ndarray
    result_from: Measure
    fmt: DataLabelFormat | None = None


@dataclass
class ResultLegend(ResultArray):
    value: list
    result_from: Dimension


@dataclass
class QueryResult:
    categories: ResultDimension
    values: ResultMeasure  # 1D (dim only) or 2D shape (len(categories), len(legend_categories))
    legend_categories: ResultLegend | None = None

    def to_tuple(self):
        if self.legend_categories is None:
            return self.categories, self.values
        return self.categories, self.legend_categories, self.values


class Dataset:
    def __init__(
        self,
        path: str | Path,
        threads: int | None = None,
        memory_limit: str | None = None,
    ) -> None:
        """Loads exactly one parquet file — nothing else. Every column
        becomes a dimension automatically (see _discover_dimensions());
        measures and calculated columns are always declared afterward via
        add_measure()/set_measures()/set_cal_col(), since DuckDB has no way
        to infer what aggregation or derived expression you want.

        `threads`/`memory_limit` are optional DuckDB connection tuning
        knobs (PRAGMA threads / memory_limit) — left unset by default so
        behavior matches DuckDB's own defaults; set them explicitly if a
        production deployment needs a pinned thread count or a memory cap."""
        self.path = Path(path)
        self._con = duckdb.connect()
        if threads is not None:
            self._con.sql(f"PRAGMA threads={int(threads)}")
        if memory_limit is not None:
            self._con.sql(f"PRAGMA memory_limit='{memory_limit}'")
        self._dims: dict[str, Dimension] = {}
        self._measures: dict[str, Measure] = {}
        self._discover_dimensions()

        # Import-mode materialization state — see _materialize()/_source_sql().
        self._materialized = False
        self._query_cache: dict[tuple, QueryResult] = {}

        # Scratch state for the in-flight query() call — see query().
        self._dim_obj: Dimension | None = None
        self._legend_obj: Dimension | None = None
        self._measure_obj: Measure | None = None
        self._sort_by: dict | None = None
        self._grouped: pl.DataFrame | None = None
        self._categories: list | None = None
        self._legend_categories: list | None = None
        self._values: np.ndarray | None = None

    def _escaped_path(self) -> str:
        return str(self.path).replace("'", "''")

    def _discover_dimensions(self) -> None:
        rows = self._con.sql(
            f"DESCRIBE SELECT * FROM read_parquet('{self._escaped_path()}')"
        ).fetchall()
        for column_name, duckdb_type, *_rest in rows:
            dtype = (
                "date"
                if duckdb_type.upper().startswith(_DATE_TYPE_PREFIXES)
                else "category"
            )
            self._dims[column_name] = Dimension(
                name=column_name, column=column_name, dtype=dtype
            )

    def add_dimension(self, dim: Dimension) -> None:
        self._dims[dim.name] = dim
        self._query_cache.clear()

    def set_cal_col(self, dim: Dimension) -> None:
        """Registers a calculated (derived) dimension column, computed by a
        raw SQL expression over the source columns, e.g.
        set_cal_col(Dimension(name="month", transform="date_trunc('month', date)"))."""
        if not dim.transform:
            raise ValueError(
                f"set_cal_col requires a Dimension with `transform` set, got {dim!r}."
            )
        self.add_dimension(dim)

    def add_measure(self, measure: Measure) -> None:
        self._measures[measure.name] = measure
        self._query_cache.clear()

    def set_measures(self, measures: list[Measure]) -> None:
        for measure in measures:
            self.add_measure(measure)

    def _resolve_dim(self, name: str) -> Dimension:
        if name not in self._dims:
            raise ValueError(
                f"Unknown dimension {name!r}. Registered: {sorted(self._dims)}"
            )
        return self._dims[name]

    def _resolve_measure(self, name: str) -> Measure:
        if name not in self._measures:
            raise ValueError(
                f"Unknown measure {name!r}. Registered: {sorted(self._measures)}"
            )
        return self._measures[name]

    def _resolve_formula(self, measure: Measure, _stack: tuple[str, ...] = ()) -> str:
        """Recursively inlines any "{other_measure}" references in
        measure.formula with that measure's own resolved SQL, parenthesized,
        so the final result is one flat aggregate expression DuckDB can
        evaluate in a single GROUP BY — no multi-level CTEs needed, since
        every reference ultimately bottoms out in plain aggregate calls."""
        if measure.name in _stack:
            cycle = " -> ".join(_stack + (measure.name,))
            raise ValueError(f"Circular measure reference: {cycle}")

        def _substitute(match: re.Match) -> str:
            referenced = self._resolve_measure(match.group(1))
            resolved = self._resolve_formula(referenced, _stack + (measure.name,))
            return f"({resolved})"

        return _MEASURE_REF_RE.sub(_substitute, measure.formula)

    def _materialize(self) -> None:
        """Loads the parquet file into a native in-memory DuckDB table once
        (import mode), so every query() after the first scans a fast
        in-memory columnar table instead of re-decoding the parquet file
        from disk each call. Idempotent — safe to call on every query()."""
        if self._materialized:
            return
        self._con.sql(
            f"CREATE OR REPLACE TABLE _base AS SELECT * FROM read_parquet('{self._escaped_path()}')"
        )
        self._materialized = True

    def _source_sql(self) -> str:
        base = "_base" if self._materialized else f"read_parquet('{self._escaped_path()}')"
        calculated = [d for d in self._dims.values() if d.transform]
        if not calculated:
            return base
        extra_cols = ", ".join(f'{d.transform} AS "{d.column}"' for d in calculated)
        return f"(SELECT *, {extra_cols} FROM {base})"

    def query(
        self,
        dim: str,
        measure: str,
        legend: str | None = None,
        filters: str | None = None,
        sort_by: dict[PbiComponents, SortOptions] | None = None,
    ) -> QueryResult:
        self._dim_obj = self._resolve_dim(dim)
        self._legend_obj = self._resolve_dim(legend) if legend else None
        self._measure_obj = self._resolve_measure(measure)
        self._sort_by = sort_by if sort_by is not None else {"dim": "asc"}

        # Dataset is immutable after construction (no write-back path), so
        # an identical (dim, measure, legend, filters, sort_by) call always
        # produces the same QueryResult — safe to cache and skip re-querying
        # DuckDB entirely on repeat calls (e.g. gallery regeneration, a
        # multi-measure Vizzy.line() re-querying the same dim/filters).
        cache_key = (dim, measure, legend, filters, tuple(self._sort_by.items()))
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]

        self._materialize()
        self._categories = None
        self._legend_categories = None
        self._values = None

        group_cols = [self._dim_obj.column] + (
            [self._legend_obj.column] if self._legend_obj else []
        )
        select_sql = ", ".join(f'"{c}"' for c in group_cols)
        formula_sql = self._resolve_formula(self._measure_obj)
        sql = (
            f'SELECT {select_sql}, {formula_sql} AS "{self._measure_obj.name}" '
            f"FROM {self._source_sql()} AS base "
            + (f"WHERE {filters} " if filters else "")
            + f"GROUP BY {select_sql}"
        )
        self._grouped = pl.DataFrame(self._con.sql(sql).fetchnumpy())

        if self._legend_obj is None:
            self._query_2dim()
        else:
            self._query_3dim()

        result = QueryResult(
            categories=ResultDimension(
                name=self._dim_obj.name,
                value=self._categories,
                result_from=self._dim_obj,
            ),
            values=ResultMeasure(
                name=self._measure_obj.name,
                value=self._values,
                fmt=self._measure_obj.fmt,
                result_from=self._measure_obj,
            ),
            legend_categories=(
                ResultLegend(
                    name=self._legend_obj.name,
                    value=self._legend_categories,
                    result_from=self._legend_obj,
                )
                if self._legend_obj is not None
                else None
            ),
        )
        self._query_cache[cache_key] = result
        return result

    def _sort_keys(self) -> tuple[list, list]:
        """self._sort_by's dim/mes entries -> Polars .sort(by=, descending=)
        args, in dict insertion order (SQL ORDER BY col1, col2, ... style
        multi-key sort). "legend" entries are handled separately (see
        _query_3dim())."""
        assert (
            self._sort_by is not None
            and self._dim_obj is not None
            and self._measure_obj is not None
        )
        keys, descending = [], []
        for component, direction in self._sort_by.items():
            if component == "dim":
                keys.append(self._dim_obj.column)
            elif component == "mes":
                keys.append(self._measure_obj.name)
            else:
                continue
            descending.append(direction == "desc")
        return keys, descending

    def _query_2dim(self) -> None:
        """No legend: one value per category. Assigns self._categories/._values."""
        assert (
            self._grouped is not None
            and self._dim_obj is not None
            and self._measure_obj is not None
        )
        keys, descending = self._sort_keys()
        grouped = self._grouped.sort(by=keys, descending=descending)
        self._categories = grouped[self._dim_obj.column].to_list()
        self._values = np.array(grouped[self._measure_obj.name].to_list(), dtype=float)

    def _query_3dim(self) -> None:
        """Legend present: one value per category per legend category.
        Assigns self._categories/._legend_categories/._values."""
        assert (
            self._grouped is not None
            and self._dim_obj is not None
            and self._measure_obj is not None
            and self._legend_obj is not None
        )
        keys, descending = self._sort_keys()

        totals = self._grouped.group_by(self._dim_obj.column).agg(
            pl.col(self._measure_obj.name).sum()
        )
        totals = totals.sort(by=keys, descending=descending)
        categories = totals[self._dim_obj.column].to_list()

        wide = self._grouped.pivot(
            on=self._legend_obj.column,
            index=self._dim_obj.column,
            values=self._measure_obj.name,
        )
        legend_categories = sorted(
            (c for c in wide.columns if c != self._dim_obj.column),
            reverse=self._sort_by.get("legend") == "desc",
        )

        wide_by_cat = {row[self._dim_obj.column]: row for row in wide.to_dicts()}
        values = np.zeros((len(categories), len(legend_categories)), dtype=float)
        for i, cat in enumerate(categories):
            row = wide_by_cat.get(cat, {})
            for j, leg in enumerate(legend_categories):
                v = row.get(leg)
                values[i, j] = 0.0 if v is None else v

        self._categories = categories
        self._legend_categories = legend_categories
        self._values = values


if __name__ == "__main__":
    import tempfile

    demo = pl.DataFrame(
        {
            "quarter": ["Q1 2024", "Q1 2024", "Q2 2024", "Q2 2024"],
            "sector": ["Technology", "Healthcare", "Technology", "Healthcare"],
            "allocation": [12.0, 8.0, 14.0, 9.0],
        }
    )
    with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
        demo.write_parquet(tmp.name)

        ds = Dataset(tmp.name)
        ds.set_measures(
            [
                Measure("allocation", "avg(allocation)"),
                Measure("total_allocation", "sum(allocation)"),
                Measure(
                    "avg_over_total", "{allocation}/{total_allocation}"
                ),  # cross-measure formula
            ]
        )

        print(
            "unfiltered:",
            ds.query(dim="quarter", legend="sector", measure="allocation").to_tuple(),
        )
        print(
            "filtered:",
            ds.query(
                dim="quarter",
                legend="sector",
                measure="allocation",
                filters="quarter = 'Q1 2024'",
            ).to_tuple(),
        )
        try:
            ds.query(dim="not_a_dim", measure="allocation")
        except ValueError as exc:
            print("error path ok:", exc)
