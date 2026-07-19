import pandas as pd
from icecream import ic
from typing import Literal, Callable
import polars as pl
import numpy as np
import duckdb
from pathlib import Path
from dataclasses import dataclass


SCALES = Literal['H','K','M','B']
_SCALE_RANGES: dict[SCALES, tuple[float, float]] = {
    "H": (10, 30),
    "K": (10_000, 30_000),
    "M": (10_000_000, 30_000_000),
    "B": (10_000_000_000, 30_000_000_000),
}

SANDBOX_DIR = Path(__file__).resolve().parent

TABLE_NAME='allocation'
PARQUET_PATH=f'{SANDBOX_DIR}/data/{TABLE_NAME}.parquet'

@dataclass
class Datamodel:
    table_name:str
    parquet_folder:str
    sqls:list[str]
    gen_fnc:Callable[..., pl.DataFrame]

    def _parquet_path(self):
        return f'{self.parquet_folder}/{self.table_name}.parquet'



def _gen_data_3dim(scale: SCALES = 'H', seed=0, ndim=7) -> pl.DataFrame:
    """1 main dimension (quarter), 1 legend dimension (sector, 7 values), 1 measure (allocation %)."""
    import polars as pl
    import numpy as np

    rng = np.random.default_rng(seed)

    periods = [f"{y}-Q{q}" for y in (2024, 2025) for q in (1, 2, 3, 4)]  # main dimension, 8 values
    sectors = [
        "Technology", "Healthcare", "Financials", "Energy",
        "Consumer", "Industrials",
        "Utilities",
        'Education', 'Hospitality'
    ]  # legend dimension, 7 values

    sectors=sectors[:ndim]

    lo, hi = _SCALE_RANGES[scale]
    stddev = (hi - lo) * 0.25  # same ratio as the original hardcoded (10, 30) / stddev=5

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


def regis_duck_tab(parquet_path, name)->duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_parquet('{parquet_path}')")
    return con

def _query(con, sql):
    return con.execute(sql).fetchdf()

def test_model(datamodel:Datamodel):
    df = datamodel.gen_fnc()
    parquet_folder = SANDBOX_DIR / datamodel.parquet_folder
    parquet_folder.mkdir(parents=True, exist_ok=True)
    parquet_path = str(parquet_folder / f"{datamodel.table_name}.parquet")
    df.write_parquet(parquet_path)

    con = regis_duck_tab(parquet_path, datamodel.table_name)
    for sql_template in datamodel.sqls:
        sql = sql_template.replace("{{self.table_name}}", datamodel.table_name)
        result = _query(con, sql)
        ic(datamodel.table_name, sql, result)
    con.close()


dm1=Datamodel(
    table_name='allocation',
    parquet_folder='./data',
    sqls=[
        'select * from {{self.table_name}} limit 5',
        'select quarter, sum(allocation) from {{self.table_name}} group by quarter',
    ],
    gen_fnc=_gen_data_3dim
)

dm2=Datamodel(
    table_name='allocation_wide',
    parquet_folder='./data',
    sqls=[
        'select * from {{self.table_name}} limit 5',
        'select sector, avg(allocation) from {{self.table_name}} group by sector order by 2 desc',
    ],
    gen_fnc=lambda: _gen_data_3dim(scale='K', seed=1, ndim=9)
)

DATAMODELs = [dm1,dm2]

def main():
    for model in DATAMODELs:
        test_model(model)

if __name__=="__main__":
    main()
