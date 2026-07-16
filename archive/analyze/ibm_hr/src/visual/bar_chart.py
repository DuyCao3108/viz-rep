"""Example viz: horizontal bar chart of a category vs a measure."""
import matplotlib.pyplot as plt
import pandas as pd


def plot(df: pd.DataFrame, category: str, measure: str, title: str = "", ax: plt.Axes | None = None):
    own_ax = ax is None
    if own_ax:
        fig, ax = plt.subplots(figsize=(8, 5))

    ax.barh(df[category], df[measure])
    ax.set_xlabel(measure)
    ax.set_title(title)
    ax.invert_yaxis()

    if own_ax:
        fig.tight_layout()
    return ax
