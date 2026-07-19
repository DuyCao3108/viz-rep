
import pandas as pd
from icecream import ic
from typing import Literal, Callable
import polars as pl
import numpy as np
import duckdb
from pathlib import Path
from dataclasses import dataclass
from src.read_data import NewDataset

SANDBOX_DIR = Path(__file__).resolve().parent

TABLE_NAME='fruits_order'
PARQUET_PATH=f'{SANDBOX_DIR}/data/{TABLE_NAME}.parquet'

@dataclass
class Dimension:
    name: str
    column: str
    dtype: Literal["category", "date"] = "category"


@dataclass
class Measure:
    name: str
    formula: str


def gen_orders(n=1000, seed=0) -> pl.DataFrame:
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

def main():
    dataset=NewDataset(data_path=PARQUET_PATH)
    dataset.set_measures(
        [
            Measure('#order', 'count(distinct order_id)', fmt='whole-thsep'),
            Measure('#apple_order', 'count(distinct case when fruit="apple" then order_id else null end)', fmt='whole-K'),
            Measure('%apple_order/order', f'{{#apple_order}}/{{#order}}', fmt='%.2'),
            Measure('avg. price', 'avg(price)',fmt='whole')
        ]
    )
    dataset.set_cal_col(
        Dimension(name='month',transform="trunc(date,'mm')")
    )
    df1=dataset.query(
        dim="month",
        measure="% apple",
        filters="price>100 and status='pending'",
        sort_by={'mes':'des'}
    )
    ic(df1)

    df2=dataset.query(
        dim="month",
        measure="avg. price",
        filters="status='delivered'",
        legend="fruit",
        sort_by={'mes':'des'}
    )
    ic(df2)
if __name__=="__main__":
    main()
