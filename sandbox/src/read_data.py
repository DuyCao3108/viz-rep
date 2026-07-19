import pandas as pd
from icecream import ic
from typing import Literal, Callable
import polars as pl
import numpy as np
import duckdb
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Dimension:
    name: str
    column: str
    transform: str
    dtype: Literal["category", "date"] = "category"


@dataclass
class Measure:
    name: str
    formula: str


class NewDataset:
    def __init__(self, data_path, duckdb_name=None, df=None) -> None:
        self.data_path=data_path
        self.duckdb_name=duckdb_name
        self._set_up_model()

    def _set_up_model(self):
        """
        -list all columns of data
        -each column is a dimension
            such as:
                self.dimensions=[
                    Dimension('date','date'),
                    Dimension('vendor','vendor'),
                    Dimension('status','status'),
                    ...
                ]
        this is similar to how powerbi works
        """
        pass

    def set_cal_col(self):
        """
        -same as calculated columns in powerbi
        -can apply sql case when on that column to create another column
        such as:
            dataset.set_cal_col(
                Dimension(name='month',transform="trunc(date,'mm')")
            )
        """
        pass

    def set_measures(self):
        """
        -just like dax in powerib
        -and use oracle sql to transform the data
        -can be apply formating automatically on it,
            this can later be understand and checked by chart when visualize
        """
        pass

    def set_model(self):
        pass

    def _make_sql(self):
        pass

    def query(self) -> queryresult:
        """
        -makesql, to pull those dim/mes/filter/legend into a runable duckdb sql query
        -into a df
        -parse into a queryresult like the olde Dataset has done
        -utilize anything we can from old Datatset class that match with current design
        """
        pass
