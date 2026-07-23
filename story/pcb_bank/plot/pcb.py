from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from plot.base import register_plot
from src.charts.line import AdjustPos
from src.dataset import Dataset
from src.vizzy import Vizzy

@register_plot("pcb")
def bar_by_quarter(ds: Dataset):
    fig, ax = plt.subplots(figsize=(8, 6))
    line = Vizzy(fig, ax, ds).line(dim="DATE_REPORT_QUARTER", measure=["% Client act CL PCB/act XS PCB", "% Client act CC PCB/act XS PCB"])

    ap1 = AdjustPos(at_dimension_val='2026-Q2', of_measure="% Client act CC PCB/act XS PCB", pad_v=-22)

    line.format_measure(fmt='%.1')
    line.set_theme(pal='cate-30')
    line.show_data_label(adjust_pos=[ap1])
    line.set_mes_scale(std=0.1)

    ax.set_title('BANK users are concentrated in high digital-saviness segments', loc='left')

    ax.tick_params(axis='y', left=False, labelleft=False)
    # ax.yaxis.grid(True, color="gray", linewidth=0.6, linestyle='-', zorder=0)

    for s in ax.spines.values():
        s.set_visible(False)

    ax.spines['top'].set_visible(True)
    ax.spines['bottom'].set_visible(True)

    fig.tight_layout()

    return fig

@register_plot("pcb")
def bar_by_quarter_by_saviness(ds: Dataset):
    measures = [
        "% Client act CL PCB/act XS PCB",
        "% Client act CC PCB/act XS PCB",
        "% Client act XS PCB",
        "% Client login w advanced act/Login",
        "% Client login w advanced act",
    ]
    facet_dim = "HAPPY_SAVINESS_GR"
    facet_vals = ds.query(dim=facet_dim, measure=measures[0]).categories.value

    all_vals = np.concatenate([
        ds.query(dim="DATE_REPORT_QUARTER", measure=m,
                 filters=f"{facet_dim} = '{val}'").values.value
        for val in facet_vals for m in measures
    ])
    shared_ylim = (float(all_vals.min()), float(all_vals.max()))

    fig, axes = plt.subplots(1, len(facet_vals), figsize=(18, 6), sharex=True, sharey=True)

    for val, ax in zip(facet_vals, axes.flat):
        line = Vizzy(fig, ax, ds).line(
            dim="DATE_REPORT_QUARTER", measure=measures,
            filters=f"{facet_dim} = '{val}'",
        )
        line.format_measure(fmt='%.1')
        line.show_data_label()
        line.set_mes_scale(ylim=shared_ylim, std=0.1)

        ax.set_title(val, loc='left')
        ax.tick_params(axis='y', left=False, labelleft=False)

        for s in ax.spines.values():
            s.set_visible(False)

        ax.spines['top'].set_visible(True)
        ax.spines['bottom'].set_visible(True)

    fig.suptitle(
        'BANK users are concentrated in high digital-saviness segments', x=0.01, ha='left'
    )
    fig.tight_layout()

    return fig


@register_plot("pcb")
def bar_by_quarter_by_saviness_shared_legend(ds: Dataset):
    measures = [
        "% Client act CL PCB/act XS PCB",
        "% Client act CC PCB/act XS PCB",
        "% Client act XS PCB",
        "% Client login w advanced act/Login",
        "% Client login w advanced act",
    ]
    facet_dim = "HAPPY_SAVINESS_GR"
    facet_vals = ds.query(dim=facet_dim, measure=measures[0]).categories.value

    all_vals = np.concatenate([
        ds.query(dim="DATE_REPORT_QUARTER", measure=m,
                 filters=f"{facet_dim} = '{val}'").values.value
        for val in facet_vals for m in measures
    ])
    shared_ylim = (float(all_vals.min()), float(all_vals.max()))

    def plot_fn(ax, val):
        fig = ax.get_figure()
        line = Vizzy(fig, ax, ds).line(
            dim="DATE_REPORT_QUARTER", measure=measures,
            filters=f"{facet_dim} = '{val}'",
        )
        line.format_measure(fmt='%.1')
        line.show_data_label()
        line.set_mes_scale(ylim=shared_ylim, std=0.1)

        ax.set_title(val, loc='left')
        ax.tick_params(axis='y', left=False, labelleft=False)

        for s in ax.spines.values():
            s.set_visible(False)

        ax.spines['top'].set_visible(True)
        ax.spines['bottom'].set_visible(True)

    fig, axes = Vizzy.small_multiple(
        facet_vals=facet_vals,
        plot_fn=plot_fn,
        figsize=(18, 6),
        title='BANK users are concentrated in high digital-saviness segments',
    )

    return fig


@register_plot("pcb")
def bar_by_quarter_by_saviness_shared_legend_font(ds: Dataset):
    # plt.rcParams['font.family'] = ['Arial', 'Helvetica', 'sans-serif']
    plt.rcParams['font.family'] = 'Helvetica'
    plt.rcParams['font.size'] = 10

    measures = [
        "% Client act CL PCB/act XS PCB",
        "% Client act CC PCB/act XS PCB",
        "% Client act XS PCB",
    ]
    facet_dim = "HAPPY_SAVINESS_GR"
    facet_vals = ds.query(dim=facet_dim, measure=measures[0]).categories.value

    all_vals = np.concatenate([
        ds.query(dim="DATE_REPORT_QUARTER", measure=m,
                 filters=f"{facet_dim} = '{val}'").values.value
        for val in facet_vals for m in measures
    ])
    shared_ylim = (float(all_vals.min()), float(all_vals.max()))

    def plot_fn(ax, val):
        fig = ax.get_figure()
        line = Vizzy(fig, ax, ds).line(
            dim="DATE_REPORT_QUARTER", measure=measures,
            filters=f"{facet_dim} = '{val}'",
        )
        line.format_measure(fmt='%.0')
        line.show_data_label()
        line.set_mes_scale(ylim=shared_ylim, std=0.1)

        ax.set_title(val, loc='left',fontstyle='italic', fontsize=10)
        ax.tick_params(axis='y', left=False, labelleft=False)

        for s in ax.spines.values():
            s.set_visible(False)

        ax.grid(axis='y', color='0.85', linewidth=0.5, zorder=0)
        ax.spines['top'].set_visible(True)
        ax.spines['bottom'].set_visible(True)

    fig, axes = Vizzy.small_multiple(
        facet_vals=facet_vals,
        plot_fn=plot_fn,
        figsize=(15, 4),
        title='BANK users are concentrated in high digital-saviness segments',
    )

    from matplotlib.lines import Line2D

    fig.add_artist(Line2D([0, 1], [0.92, 0.92], transform=fig.transFigure,
                           color='black', linewidth=0.8))

    return fig
