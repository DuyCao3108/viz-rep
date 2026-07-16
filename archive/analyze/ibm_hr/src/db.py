"""DuckDB connection setup for the ibm_hr dataset.

Loads the CSV in data/ as a DuckDB table so it can be queried with SQL.
"""
from pathlib import Path

import duckdb

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "ibm_hr_employee_attrition.csv"
TABLE_NAME = "hr"


def connect(csv_path: Path = CSV_PATH, table_name: str = TABLE_NAME) -> duckdb.DuckDBPyConnection:
    """Return an in-memory DuckDB connection with the CSV loaded as `table_name`."""
    con = duckdb.connect(database=":memory:")
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{csv_path}')")
    return con


def query(sql: str, con: duckdb.DuckDBPyConnection | None = None):
    """Run a SQL query and return the result as a pandas DataFrame."""
    own_con = con is None
    con = con or connect()
    df = con.execute(sql).df()
    if own_con:
        con.close()
    return df
