import numpy as np
import polars as pl
import matplotlib.pyplot as plt
from src.dataset import Dataset, Dimension, Measure
from src.vizzy import Vizzy

def generate_mock_data(seed: int = 0):
    """1 main dimension (quarter), 1 legend dimension (sector, 7 values), 1 measure (allocation %)."""
    rng = np.random.default_rng(seed)

    periods = [f"Q{q} {y}" for y in (2024, 2025) for q in (1, 2, 3, 4)]  # main dimension, 8 values
    sectors = [
        "Technology", "Healthcare", "Financials", "Energy",
        "Consumer", "Industrials",
        "Utilities",
        # 'Education', 'Hospitality'
    ]  # legend dimension, 7 values

    base = rng.uniform(5, 20, size=len(sectors))
    walk = rng.normal(0, 1.2, size=(len(periods), len(sectors))).cumsum(axis=0)
    values = np.clip(base + walk, 1, None)  # rows=periods, cols=sectors

    df = pl.DataFrame(
        {
            "quarter": [p for p in periods for _ in sectors],
            "sector": [s for _ in periods for s in sectors],
            "allocation": values.flatten(),
        }
    )
    dataset = Dataset(
        df,
        dimensions=[
            Dimension("quarter", "quarter", sort=periods),
            Dimension("sector", "sector", sort=sectors),
        ],
        measures=[Measure("allocation", "allocation", agg="mean")],
    )
    return dataset

def plot_bar():
    dataset = generate_mock_data()
    fig, ax = plt.subplots(figsize=(12, 6))
    viz = Vizzy(fig, ax, dataset)
    viz.line(dim="quarter", legend="sector", measure="allocation")
    viz.artist.show_data_label()
    fig.savefig("./output/bar_1.png")


if __name__=="__main__":
    plot_bar()
