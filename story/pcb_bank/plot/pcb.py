from __future__ import annotations

import matplotlib.pyplot as plt

from plot.base import register_plot
from src.charts.line import AdjustPos
from src.dataset import Dataset
from src.vizzy import Vizzy
from src.custom.fonts import FONT_STACKS, resolve_installed_font

@register_plot("pcb")
def bar_by_quarter(ds: Dataset):
    fig, ax = plt.subplots(figsize=(10, 6))
    line = Vizzy(fig, ax, ds).line(dim="DATE_REPORT_QUARTER", measure=["% Client act CL PCB/act XS PCB", "% Client act CC PCB/act XS PCB"])

    ap1 = AdjustPos(at_dimension_val='26-04', of_measure="% Client act CC PCB/act XS PCB", pad_v=-22)

    line.set_theme(pal='step5-blue')
    line.show_data_label(adjust_pos=[ap1])
    ax.yaxis.set_visible(False)

    title_font = resolve_installed_font(*[n.strip(" '") for n in FONT_STACKS["sans_headline"].split(",")])
    ax.set_title('~65% has active CC, ~65% has active CL', loc='left', fontfamily=title_font)

    return fig
