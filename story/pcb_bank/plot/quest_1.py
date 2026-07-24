from __future__ import annotations

import matplotlib.pyplot as plt
from numpy import pad

from plot.base import register_plot
from src.dataset import Dataset
from src.vizzy import Vizzy
from src.custom.fonts import resolve_installed_font
from src.charts.line import AdjustPos

COLOR_THEME='cate-30'
plt.rcParams['font.family'] = resolve_installed_font('Arial', 'Helvetica', 'DejaVu Sans')
FONT_SIZE=12
FIG_SIZE=(16, 8)

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

def quest1_1_bar(fig, ax, ds: Dataset):
    """
    same with pcb_bar.stackbar_single_prime_vs_competitor()
    """
    bar = Vizzy(fig, ax, ds).stack_bar_100(
        dim="DATE_REPORT_QUARTER",
        measure="# Client prime",
        legend="F_ACT_PCB_XS",
    )
    bar.set_theme(pal=COLOR_THEME)
    # customize
    ax.spines['top'].set_color('gray')
    # customize-end

    bar.show_data_label()

    for s in ax.spines.values():
        s.set_visible(False)
    ax.spines['top'].set_visible(True)
    ax.spines['bottom'].set_visible(True)

    title = wrap_title(ax, "50% of prime client having active CL/CC with competitor")
    ax.set_title(title, loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=3, frameon=False)
    ax.set_ylim(0, 105)

def quest1_21_line(fig, ax, ds: Dataset):
    measures = [
        "% Client act CL PCB/act XS PCB",
        "% Client act CC PCB/act XS PCB",
    ]
    line = Vizzy(fig, ax, ds).line(dim="DATE_REPORT_QUARTER", measure=measures)
    line.format_measure(fmt="%.2")

    # customize
    adjust_pos= [
        AdjustPos(at_dimension_val='26-Q2', of_measure="% Client act CC PCB/act XS PCB", pad_v=-25),
    ]
    line.show_data_label(
        adjust_pos=adjust_pos
    )
    line.set_theme(pal=COLOR_THEME)
    ax.tick_params(axis='y', left=False, labelleft=False)
    ax.spines['top'].set_visible(True)
    ax.spines['top'].set_color('gray')
    ax.spines['left'].set_visible(False)
    ax.legend(frameon=False)


    # customize-end
    line.set_mes_scale(std=0.2)

    ax.set_title("Among whom, 64% has active CC, 65% has active CL", loc="left")

    _relabel_legend(ax, {
        "% Client act CL PCB/act XS PCB": "% Active CL PCB",
        "% Client act CC PCB/act XS PCB": "% Active CC PCB",
    })

def quest1_22_line(fig, ax, ds: Dataset):
    measures = [
        "% Client act XS with BANK/act XS PCB",
        "% Client act XS with FI/act XS PCB",
    ]
    line = Vizzy(fig, ax, ds).line(dim="DATE_REPORT_QUARTER", measure=measures)
    line.format_measure(fmt="%.2")

    line.set_theme(pal=COLOR_THEME)
    line.set_mes_scale(std=0.15)

    # customize
    ax.tick_params(axis='y', left=False, labelleft=False)
    ax.spines['top'].set_visible(True)
    ax.spines['top'].set_color('gray')
    ax.spines['left'].set_visible(False)
    ax.legend(frameon=False)

    # customize-end

    ax.set_title("... 61% borrowing from BANK, 66% borrowing from FI", loc="left")

    _relabel_legend(ax, {
        "% Client act XS with BANK/act XS PCB": "% Active Bank PCB",
        "% Client act XS with FI/act XS PCB": "% Active Fi PCB",
    })

@register_plot("quest_1")
def quest1_multi_ax(ds: Dataset):
    plt.rcParams['font.size']=FONT_SIZE

    fig = plt.figure(figsize=FIG_SIZE)
    gs = fig.add_gridspec(2, 2, width_ratios=[2, 3])
    ax1 = fig.add_subplot(gs[:, 0])   # left, spans both rows
    ax2 = fig.add_subplot(gs[0, 1])   # top-right
    ax3 = fig.add_subplot(gs[1, 1])   # bottom-right

    quest1_1_bar(fig, ax1, ds)
    quest1_21_line(fig, ax2, ds)
    quest1_22_line(fig, ax3, ds)

    fig.tight_layout()

    return fig
