"""Shared pytest fixtures for tests/. Nothing under tests/gallery/ uses this —
the gallery is a plain script, not pytest-collected."""

import matplotlib
matplotlib.use("Agg")  # headless: chart-class tests must never pop up a GUI window

import polars as pl
import pytest
from matplotlib import pyplot as plt

from src.dataset import Dataset, Dimension, Measure


@pytest.fixture
def sample_dataset() -> Dataset:
    df = pl.DataFrame(
        {
            "quarter": ["Q1 2024", "Q1 2024", "Q2 2024", "Q2 2024"],
            "sector": ["Technology", "Healthcare", "Technology", "Healthcare"],
            "allocation": [12.0, 8.0, 14.0, 9.0],
        }
    )
    return Dataset(
        df,
        dimensions=[Dimension("quarter", "quarter"), Dimension("sector", "sector")],
        measures=[Measure("allocation", "allocation", agg="mean")],
    )


@pytest.fixture
def fig_ax():
    """A bare (fig, ax) pair for chart-class tests, matching the fig/ax every
    chart class takes at construction. Closed after the test so repeated runs
    don't accumulate open figures."""
    fig, ax = plt.subplots()
    yield fig, ax
    plt.close(fig)
