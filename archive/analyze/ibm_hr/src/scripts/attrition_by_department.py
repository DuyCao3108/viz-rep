"""Example query: attrition rate by department."""
import duckdb

SQL = """
    SELECT
        Department,
        COUNT(*) AS headcount,
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
        ROUND(100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS attrition_rate
    FROM hr
    GROUP BY Department
    ORDER BY attrition_rate DESC
"""


def run(con: duckdb.DuckDBPyConnection):
    return con.execute(SQL).df()
