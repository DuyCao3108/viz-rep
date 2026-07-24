from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from plot.base import register_plot
from src.dataset import Dataset
from src.vizzy import Vizzy
from src.custom.fonts import resolve_installed_font

COLOR_THEME = 'cate-25'
plt.rcParams['font.family'] = resolve_installed_font('Arial', 'Helvetica', 'DejaVu Sans')
FONT_SIZE = 12
FIG_SIZE = (16, 8)

def _relabel_legend(ax, relabel: dict[str, str]) -> None:
    for text in ax.get_legend().get_texts():
        text.set_text(relabel.get(text.get_text(), text.get_text()))

@register_plot("quest_2_1")
def quest2_1(ds: Dataset):
    dim = "DATE_REPORT_QUARTER"
    facet = "PCB_XS_LENDER_GR"
    measures = [
        "% Client login",
        "% Client login w advanced act",
    ]
    facet_in = {
        '2. Active HCVN X BANK': '3. Active HCVN X BANK',
        '3. Active HCVN X FI': '2. Active HCVN X FI',
        '4. Active HCVN only': '1. Active HCVN only'
    }

    with plt.rc_context({"font.size": FONT_SIZE}):
        facet_vals = ds.query(dim=facet, measure=measures[0]).categories.value
        facet_vals = [v for v in facet_vals if v in facet_in]
        facet_vals = sorted(facet_vals, key=lambda v: facet_in[v])

        # Shared y-scale across facets (pcb.line_multi_3dim precedent) so
        # login vs advanced-act rates are directly comparable in magnitude.
        all_vals = np.concatenate([
            ds.query(dim=dim, measure=m, filters=f"{facet} = '{val}'").values.value
            for val in facet_vals for m in measures
        ])
        shared_ylim = (float(all_vals.min()), float(all_vals.max()))

        def plot_fn(ax, val):
            fig = ax.get_figure()

            line = Vizzy(fig, ax, ds).line(
                dim=dim, measure=measures,
                filters=f"{facet} = '{val}'",
            )
            line.format_measure(fmt="%.0")
            line.set_theme(pal=COLOR_THEME)
            line.show_data_label()
            line.set_mes_scale(ylim=shared_ylim, std=0.1)

            ax.set_title(facet_in[val], loc="left", style="italic", size=FONT_SIZE)
            ax.tick_params(axis='y', left=False, labelleft=False)

            for s in ax.spines.values():
                s.set_visible(False)

            ax.spines['top'].set_visible(True)
            ax.spines['top'].set_color('gray')
            ax.spines['bottom'].set_visible(True)


            # custom
            _relabel_legend(ax, relabel={
                "% Client login": "% Client login",
                "% Client login w advanced act": "% Client login w advanced action",
            })

        fig, axes = Vizzy.small_multiple(
            facet_vals=facet_vals,
            plot_fn=plot_fn,
            figsize=FIG_SIZE,
            title="BANK users login more, and perform advanced actions on Happy more",
            f_show_legend=False
        )

        # customize axes
        for n in range(len(axes)):
            axes[n].legend().set_visible(False)

        axes[0].legend().set_visible(True)
        # axes[0].legend(frameon=False,loc='upper left',borderaxespad=1.5)
        axes[0].legend(frameon=False)

    return fig
