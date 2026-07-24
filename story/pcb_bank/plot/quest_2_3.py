from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from plot.base import register_plot
from src.dataset import Dataset
from src.vizzy import Vizzy
from src.custom.fonts import resolve_installed_font
from src.charts.line import AdjustPos

COLOR_THEME = 'cate-30'
plt.rcParams['font.family'] = resolve_installed_font('Arial', 'Helvetica', 'DejaVu Sans')
FONT_SIZE = 9.5
FIG_SIZE = (16 / 2, 6)

MEASURES = [
    "% Client act XS with BANK",
    "% Client act XS with FI",
]
RELABEL = {
    "% Client act XS with BANK": "% Active w Bank",
    "% Client act XS with FI": "% Active w FI",
}

# STAGE_F_PRIME_DIGITAL_BOP is a raw 0/1 flag (F_ prefix convention, like
# F_ACT_PCB_XS), not a named segment dimension — give its facet titles a
# readable label instead of the bare "0"/"1" DuckDB returns.
FACET_LABELS = {
    "STAGE_F_PRIME_DIGITAL_BOP": {1: "Digital Prime", 0: "Non Digital Prime"},
}


def _relabel_legend(ax, relabel: dict[str, str]) -> None:
    for text in ax.get_legend().get_texts():
        text.set_text(relabel.get(text.get_text(), text.get_text()))


# "Digital Prime" (facet val 1) is the only STAGE_F_PRIME_DIGITAL_BOP panel
# where BANK/FI land within ~1pp of each other — at 25-Q3/25-Q4 FI sits just
# above BANK, at 26-Q1 it flips (BANK just above FI) — close enough each time
# that the default above-point labels collide (see quest2_3_1.png before
# this fix). Push whichever series is lower at that quarter down out of the
# way.
PRIME_DIGITAL_ADJUST_POS = {
    1: [
        AdjustPos(at_dimension_val="25-Q3", of_measure="% Client act XS with BANK", pad_v=-20),
        AdjustPos(at_dimension_val="25-Q4", of_measure="% Client act XS with BANK", pad_v=-20),
        AdjustPos(at_dimension_val="26-Q1", of_measure="% Client act XS with FI", pad_v=-20),
    ],
}


def _prime_digital_multiple(ds: Dataset) -> plt.Figure:
    """Same shape as _saviness_gr_multiple, split out for the
    STAGE_F_PRIME_DIGITAL_BOP facet specifically because its "Digital Prime"
    panel needs per-dimension-value AdjustPos label nudges
    (PRIME_DIGITAL_ADJUST_POS) that a shared facet-agnostic template has no
    parameter for."""
    facet = "STAGE_F_PRIME_DIGITAL_BOP"
    dim = "DATE_REPORT_QUARTER"
    title = "BANK users are concentrated in high digital-saviness segments such as Digital Prime"

    with plt.rc_context({"font.size": FONT_SIZE}):
        facet_vals = ds.query(dim=facet, measure=MEASURES[0]).categories.value

        all_vals = np.concatenate([
            ds.query(dim=dim, measure=m, filters=f"{facet} = '{val}'").values.value
            for val in facet_vals for m in MEASURES
        ])
        shared_ylim = (float(all_vals.min()), float(all_vals.max()))

        def plot_fn(ax, val):
            fig = ax.get_figure()

            line = Vizzy(fig, ax, ds).line(
                dim=dim, measure=MEASURES,
                filters=f"{facet} = '{val}'",
            )
            line.format_measure(fmt="%.0")
            line.set_theme(pal=COLOR_THEME)
            line.show_data_label(adjust_pos=PRIME_DIGITAL_ADJUST_POS.get(val))
            line.set_mes_scale(ylim=shared_ylim, std=0.1)

            label = FACET_LABELS.get(facet, {}).get(val, val)
            ax.set_title(label, loc="left", style="italic", size=FONT_SIZE)
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
            # See quest_2_2.py's identical comment: FIG_SIZE is the
            # per-2-facet baseline, scaled up so >2 facets don't cram titles/
            # tick labels into each other.
            figsize=(max(FIG_SIZE[0], FIG_SIZE[0] * len(facet_vals) / 2), FIG_SIZE[1]),
            title=title,
            f_show_legend=False,
        )

        # No rename API exists on Line/Vizzy — relabel by mutating the
        # already-drawn legend Text objects (same as quest_1.py/
        # quest_1_pt2.py's _relabel_legend usage).
        axes[0].legend(frameon=False)
        _relabel_legend(axes[0], RELABEL)
        for ax in axes[1:]:
            ax.legend().set_visible(False)

    return fig


@register_plot("quest_2_3")
def quest2_3_1(ds: Dataset):
    return _prime_digital_multiple(ds)


# "1. Advanced Active" is the only HAPPY_SAVINESS_GR panel where BANK/FI
# land within ~0.6pp of each other at 25-Q3 and 25-Q4, close enough that
# their default above-point data labels collide (see quest2_3_2.png before
# this fix) — push FI's label below its point at just those two quarters.
SAVINESS_GR_ADJUST_POS = {
    "1. Advanced Active": [
        AdjustPos(at_dimension_val="25-Q3", of_measure="% Client act XS with FI", pad_v=-20),
        AdjustPos(at_dimension_val="25-Q4", of_measure="% Client act XS with FI", pad_v=-20),
        AdjustPos(at_dimension_val="26-Q1", of_measure="% Client act XS with FI", pad_v=-20),
        AdjustPos(at_dimension_val="26-Q2", of_measure="% Client act XS with FI", pad_v=-20),
    ],
}


def _saviness_gr_multiple(ds: Dataset) -> plt.Figure:
    """Same shape as _digital_saviness_multiple, split out for the
    HAPPY_SAVINESS_GR facet specifically because its "Advanced Active" panel
    needs per-dimension-value AdjustPos label nudges (SAVINESS_GR_ADJUST_POS)
    that the generic template has no parameter for."""
    facet = "HAPPY_SAVINESS_GR"
    dim = "DATE_REPORT_QUARTER"
    title = "BANK users are concentrated in high digital-saviness segments such as Digital saviness gr"

    with plt.rc_context({"font.size": FONT_SIZE}):
        facet_vals = ds.query(dim=facet, measure=MEASURES[0]).categories.value

        all_vals = np.concatenate([
            ds.query(dim=dim, measure=m, filters=f"{facet} = '{val}'").values.value
            for val in facet_vals for m in MEASURES
        ])
        shared_ylim = (float(all_vals.min()), float(all_vals.max()))

        def plot_fn(ax, val):
            fig = ax.get_figure()

            line = Vizzy(fig, ax, ds).line(
                dim=dim, measure=MEASURES,
                filters=f"{facet} = '{val}'",
            )
            line.format_measure(fmt="%.0")
            line.set_theme(pal=COLOR_THEME)
            line.show_data_label(adjust_pos=SAVINESS_GR_ADJUST_POS.get(val))
            line.set_mes_scale(ylim=shared_ylim, std=0.1)

            ax.set_title(val, loc="left", style="italic", size=FONT_SIZE)
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
            figsize=(max(FIG_SIZE[0], FIG_SIZE[0] * len(facet_vals) / 2), FIG_SIZE[1]),
            title=title,
            f_show_legend=False,
        )

        axes[0].legend(frameon=False)
        _relabel_legend(axes[0], RELABEL)
        for ax in axes[1:]:
            ax.legend().set_visible(False)

    return fig


@register_plot("quest_2_3")
def quest2_3_2(ds: Dataset):
    return _saviness_gr_multiple(ds)
