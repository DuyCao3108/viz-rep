"""ibm_hr analysis entry point.

Set MODEL to the name of the script (module) in src/scripts/ you want to run.
Its `run(con)` function is called against the DuckDB connection, then the
matching viz function (if any) renders the result.
"""
import matplotlib.pyplot as plt

from src.db import connect
from src.scripts import attrition_by_department
from src.visual import bar_chart

MODEL = "attrition_by_department"

SCRIPTS = {
    "attrition_by_department": attrition_by_department,
}

if __name__ == "__main__":
    con = connect()

    df = SCRIPTS[MODEL].run(con)
    print(df)

    bar_chart.plot(df, category="Department", measure="attrition_rate", title=MODEL)
    plt.show()
