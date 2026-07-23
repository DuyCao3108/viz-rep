"""Client prime mix by XS lender — 100%-stacked bar, per quarter."""

from __future__ import annotations

import matplotlib.pyplot as plt

from plot.base import register_plot
from src.dataset import Dataset
from src.vizzy import Vizzy

MEASURE = "# Client prime"
LEGEND_DIM = "PCB_XS_LENDER_GR"
FACET_DIM = "HCVN_ACT_PROD_GR"


@register_plot("pcb_bar")
def stack100_bar_by_quarter_by_lender(ds: Dataset):
    fig, ax = plt.subplots(figsize=(10, 6))
    bar = Vizzy(fig, ax, ds).stack_bar_100(
        dim="DATE_REPORT_QUARTER", measure=MEASURE, legend=LEGEND_DIM,
    )
    bar.set_theme()
    bar.show_data_label()

    ax.set_title("Client prime mix by XS lender, per quarter", loc="left")
    fig.tight_layout()

    return fig


@register_plot("pcb_bar")
def stack100_bar_by_quarter_by_lender_by_prod(ds: Dataset):
    facet_vals = ds.query(dim=FACET_DIM, measure=MEASURE).categories.value

    def plot_fn(ax, val):
        fig = ax.get_figure()
        bar = Vizzy(fig, ax, ds).stack_bar_100(
            dim="DATE_REPORT_QUARTER", measure=MEASURE, legend=LEGEND_DIM,
            filters=f"{FACET_DIM} = '{val}'",
        )
        bar.set_theme()
        bar.show_data_label()
        ax.set_title(val, loc="left")

    fig, axes = Vizzy.small_multiple(
        facet_vals=facet_vals,
        plot_fn=plot_fn,
        figsize=(18, 6),
        title="Client prime mix by XS lender, per quarter, by HCVN active product group",
    )

    return fig
