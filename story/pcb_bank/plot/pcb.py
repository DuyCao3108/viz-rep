from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from plot.base import register_plot
from src.charts.line import AdjustPos
from src.dataset import Dataset
from src.vizzy import Vizzy

from src.custom.fonts import resolve_installed_font
plt.rcParams['font.family'] = resolve_installed_font('Arial', 'Helvetica', 'DejaVu Sans')


@register_plot("pcb")
def line_single(ds: Dataset):
    fig, ax = plt.subplots(figsize=(8, 6))
    dim="DATE_REPORT_QUARTER"
    measures=["# Client prime"]
    legend="F_ACT_PCB_XS"
    facet=""
    title='50% of prime client having active CL/CC contract with competitor'

    line = Vizzy(fig, ax, ds).line(
        dim=dim,
        measure=measures)

    # ap1 = AdjustPos(at_dimension_val='26-Q2', of_measure="% Client act CC PCB/act XS PCB", pad_v=-22)

    line.format_measure(fmt='%.1')
    line.set_theme(pal='powerbi')
    # line.show_data_label(adjust_pos=[ap1])
    line.set_mes_scale(std=0.1)

    ax.set_title(title, loc='left')

    ax.tick_params(axis='y', left=False, labelleft=False)
    # ax.yaxis.grid(True, color="gray", linewidth=0.6, linestyle='-', zorder=0)

    for s in ax.spines.values():
        s.set_visible(False)

    ax.spines['top'].set_visible(True)
    ax.spines['bottom'].set_visible(True)

    fig.tight_layout()

    return fig

@register_plot("pcb")
def line_multi_3dim(ds: Dataset):
    plt.rcParams['font.size']=8

    adjust_pos= [
    AdjustPos(at_dimension_val='26-Q1', of_measure="% Client act CC PCB/act XS PCB", pad_v=-25),
    AdjustPos(at_dimension_val='26-Q1', of_measure="% Client act CC PCB/act XS PCB", pad_v=-22)
    ]


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

    fig, axes = plt.subplots(1, len(facet_vals), figsize=(10, 5), sharex=True, sharey=True)

    for val, ax in zip(facet_vals, axes.flat):
        line = Vizzy(fig, ax, ds).line(
            dim="DATE_REPORT_QUARTER", measure=measures,
            filters=f"{facet_dim} = '{val}'",
        )
        line.format_measure(fmt='%.0')
        line.show_data_label(adjust_pos=adjust_pos)
        line.set_mes_scale(ylim=shared_ylim, std=0.2)

        ax.set_title(val, loc='left', style='italic', size=8)
        ax.tick_params(axis='y', left=False, labelleft=False)

        for s in ax.spines.values():
            s.set_visible(False)

        ax.spines['top'].set_visible(True)
        ax.spines['bottom'].set_visible(True)

    fig.suptitle(
        'BANK users are concentrated in high digital-saviness segments', x=0.01, ha='left'
    )
    # legend
    handles, labels = axes.flat[0].get_legend_handles_labels()
    for ax in axes.flat:
        ax.get_legend().remove()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.05), ncol=len(measures), frameon=False)
    # legend-end

    fig.tight_layout()

    return fig
