from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from numpy import pad

from plot.base import register_plot
from src.dataset import Dataset
from src.vizzy import Vizzy
from src.custom.fonts import resolve_installed_font
from src.charts.line import AdjustPos

COLOR_THEME='cate-25'
plt.rcParams['font.family'] = resolve_installed_font('Arial', 'Helvetica', 'DejaVu Sans')
FONT_SIZE=9.5
MULTI_TITLE_SIZE=9.5
FIG_SIZE=(16, 4.5)

def wrap_title(ax, title, fontsize=None):
    import textwrap
    fontsize = fontsize or plt.rcParams['font.size']
    ax.figure.canvas.draw()  # force layout so extents are real
    ax_width_px = ax.get_window_extent().width
    char_width_px = fontsize * 0.6
    width = max(int(ax_width_px / char_width_px), 10)
    return "\n".join(textwrap.wrap(title, width=width))


def _relabel_legend(ax, relabel: dict[str, str]) -> None:
    for text in ax.get_legend().get_texts():
        text.set_text(relabel.get(text.get_text(), text.get_text()))

@register_plot("quest_1_xsel")
def quest_1_xsel(ds: Dataset):
    dim = "DATE_REPORT_QUARTER"
    facet = "F_ACT_PCB_XS"
    measures = [
        "% Client eli XS",
        "% Client submit BOD0 XS",
        "% Client signnc XS",
    ]

    with plt.rc_context({"font.size": FONT_SIZE}):
        facet_vals = ds.query(dim=facet, measure=measures[0]).categories.value

        # Shared y-scale across facets (pcb.line_multi_3dim precedent) so the
        # Active vs Non-Active funnels are directly comparable in magnitude.
        all_vals = np.concatenate([
            ds.query(dim=dim, measure=m, filters=f"{facet} = '{val}'").values.value
            for val in facet_vals for m in measures
        ])
        shared_ylim = (float(all_vals.min()), float(all_vals.max()))

        def plot_fn(ax, val):
            fig = ax.get_figure()

            adjust_pos= [
                AdjustPos(at_dimension_val='26-Q2', of_measure="% Client signnc XS", pad_v=-10,pad_h=20),
                # all signnc 2 down vertical
                AdjustPos(at_dimension_val='25-Q3', of_measure="% Client signnc XS", pad_v=-27),
                AdjustPos(at_dimension_val='25-Q4', of_measure="% Client signnc XS", pad_v=-27),
                AdjustPos(at_dimension_val='26-Q1', of_measure="% Client signnc XS", pad_v=-27),
                AdjustPos(at_dimension_val='26-Q2', of_measure="% Client signnc XS", pad_v=-27, pad_h=15),
            ]

            line = Vizzy(fig, ax, ds).line(
                dim=dim, measure=measures,
                filters=f"{facet} = '{val}'",
            )
            line.format_measure(fmt="%.1")
            line.set_theme(pal=COLOR_THEME)
            line.show_data_label(
                adjust_pos=adjust_pos
            )
            line.set_mes_scale(ylim=shared_ylim, std=0.1)

            ax.set_title(val, loc="left", style="italic",size=MULTI_TITLE_SIZE)
            ax.tick_params(axis='y', left=False, labelleft=False)

            for s in ax.spines.values():
                s.set_visible(False)

            ax.spines['top'].set_visible(True)
            ax.spines['top'].set_color('gray')
            ax.spines['bottom'].set_visible(True)
            ax.legend()

        fig, axes = Vizzy.small_multiple(
            facet_vals=facet_vals,
            plot_fn=plot_fn,
            figsize=FIG_SIZE,
            title="They have high demand (higher BOD0 rate), but lower eligibility",
            f_show_legend=False
        )

        # customize axes
        axes[0].legend(frameon=False)
        _relabel_legend(axes[0], {
            "% Client eli XS": "% Eli XS",
            "% Client submit BOD0 XS": "% BOD0 submit",
            "% Client signnc XS": "% Signnc XS",
        })
        axes[1].legend().set_visible(False)


    return fig
