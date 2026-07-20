"""Test-only glue between in-memory generated data and Dataset.

Dataset only loads from a parquet file (see src/dataset.py) — it has no
in-memory-DataFrame constructor and never generates data itself. Tests and
the gallery scenario runner still generate data in memory (random or fixed),
so this materializes that DataFrame to a temp parquet file first. Importable
from both pytest (tests/conftest.py) and the plain-script gallery runner
(tests/gallery/scenarios/*.py).
"""

from __future__ import annotations

import os
import tempfile

import polars as pl

from src.dataset import Dataset
from typing import Literal

SCALES = Literal["H", "K", "M", "B"]

_SCALE_RANGES: dict[SCALES, tuple[float, float]] = {
    "H": (10, 30),
    "K": (10_000, 30_000),
    "M": (10_000_000, 30_000_000),
    "B": (10_000_000_000, 30_000_000_000),
}

def dataset_from_df(df: pl.DataFrame) -> Dataset:
    fd, path = tempfile.mkstemp(suffix=".parquet")
    os.close(fd)
    df.write_parquet(path)
    return Dataset(path)


def _gen_orders(n=1000, seed=0) -> pl.DataFrame:
    import polars as pl
    import numpy as np
    FRUITS = ["apple","banana","orange","mango","grape","pineapple",
                "watermelon","strawberry","kiwi","peach"]
    VENDORS = [f"Vendor{i}" for i in range(1, 11)]
    rng = np.random.default_rng(seed)
    statuses = ["pending", "shipped", "delivered", "cancelled"]
    return pl.DataFrame({
        "order_id": [f"ORD{i:05d}" for i in range(n)],
        "cuid": rng.integers(1, 30, n),
        "date": pl.date_range(pl.date(2025,1,1), pl.date(2025,12,31), eager=True).sample(n, with_replacement=True, seed=seed),
        "status": rng.choice(statuses, n),
        "price": np.round(rng.uniform(10, 500, n), 2),
        "fruit": rng.choice(FRUITS, n),
        "vendor": rng.choice(VENDORS, n),
    })

def _gen_data_3dim(scale: SCALES = "H", seed=0, ndim=7):
    """1 main dimension (quarter), 1 legend dimension (sector, 7 values), 1 measure (allocation %)."""
    import numpy as np
    import polars as pl

    rng = np.random.default_rng(seed)

    periods = [
        f"{y}-Q{q}" for y in (2024, 2025) for q in (1, 2, 3, 4)
    ]  # main dimension, 8 values
    sectors = [
        "Technology",
        "Healthcare",
        "Financials",
        "Energy",
        "Consumer",
        "Industrials",
        "Utilities",
        "Education",
        "Hospitality",
    ]  # legend dimension, 7 values

    sectors = sectors[:ndim]

    lo, hi = _SCALE_RANGES[scale]
    stddev = (
        hi - lo
    ) * 0.25  # same ratio as the original hardcoded (10, 30) / stddev=5

    base = rng.uniform(lo, hi, size=len(sectors))
    walk = rng.normal(0, stddev, size=(len(periods), len(sectors))).cumsum(axis=0)
    values = np.clip(base + walk, 1, None)  # rows=periods, cols=sectors

    df = pl.DataFrame(
        {
            "quarter": [p for p in periods for _ in sectors],
            "sector": [s for _ in periods for s in sectors],
            "allocation": values.flatten(),
        }
    )
    return df

def _gen_data_2dim():
    """Fixed (non-random) revenue-scale values chosen to visibly exercise
    both K-scaling/thousand-sep and threshold-hiding: 2 of 5 fall below the
    100K threshold, one scaled value (1,400K) is large enough to show comma
    grouping."""
    import polars as pl

    regions = ["North America", "Europe", "APAC", "LATAM", "MEA"]
    revenue = [45_000, 220_000, 1_400_000, 80_000, 960_000]
    return pl.DataFrame({"region": regions, "revenue": revenue})
