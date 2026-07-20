"""Shared pytest fixtures for tests/. Nothing under tests/gallery/ uses this —
the gallery is a plain script, not pytest-collected."""

import matplotlib
matplotlib.use("Agg")  # headless: chart-class tests must never pop up a GUI window

from datetime import date

import polars as pl
import pytest
from matplotlib import pyplot as plt

from src.dataset import Dataset, Dimension, Measure
from tests.dataset_factory import dataset_from_df


@pytest.fixture
def sample_dataset() -> Dataset:
    df = pl.DataFrame(
        {
            "quarter": ["Q1 2024", "Q1 2024", "Q2 2024", "Q2 2024"],
            "sector": ["Technology", "Healthcare", "Technology", "Healthcare"],
            "allocation": [12.0, 8.0, 14.0, 9.0],
        }
    )
    ds = dataset_from_df(df)  # dimensions ("quarter"/"sector") auto-discovered
    ds.add_measure(Measure("allocation", "avg(allocation)"))
    return ds


@pytest.fixture
def orders_dataset() -> Dataset:
    """Exercises the DuckDB-backed features sample_dataset doesn't: a
    calculated (derived) dimension, raw-SQL filters, and a measure that
    references another measure by name."""
    df = pl.DataFrame(
        {
            "order_id": ["O1", "O2", "O3", "O4", "O5", "O6"],
            "date": [
                date(2025, 1, 15), date(2025, 1, 20),
                date(2025, 2, 5), date(2025, 2, 10), date(2025, 2, 15),
                date(2025, 3, 1),
            ],
            "fruit": ["apple", "banana", "apple", "apple", "banana", "apple"],
            "status": ["delivered", "delivered", "delivered", "cancelled", "delivered", "delivered"],
        }
    )
    ds = dataset_from_df(df)
    ds.set_cal_col(Dimension(name="month", transform="date_trunc('month', date)"))
    ds.set_measures(
        [
            Measure("num_orders", "count(distinct order_id)"),
            Measure(
                "num_apple_orders",
                "count(distinct case when fruit='apple' then order_id else null end)",
            ),
            Measure("pct_apple", "{num_apple_orders}/{num_orders}"),
        ]
    )
    return ds


@pytest.fixture
def fig_ax():
    """A bare (fig, ax) pair for chart-class tests, matching the fig/ax every
    chart class takes at construction. Closed after the test so repeated runs
    don't accumulate open figures."""
    fig, ax = plt.subplots()
    yield fig, ax
    plt.close(fig)
