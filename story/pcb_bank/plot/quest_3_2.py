from __future__ import annotations

import matplotlib.pyplot as plt

from plot.base import register_plot
from src.dataset import Dataset, Dimension
from src.vizzy import Vizzy
from src.custom.fonts import resolve_installed_font

COLOR_THEME = 'cate-25'
plt.rcParams['font.family'] = resolve_installed_font('Arial', 'Helvetica', 'DejaVu Sans')
FONT_SIZE = 9
FIG_SIZE = (16 / 3, 8)

DIM = "DATE_REPORT_QUARTER"
MEASURE = "# Client prime"

TICKET_BANK_COL = "PCB_ACT_CASH_BANK_MAX_TICKET_GR"
TICKET_FI_COL = "PCB_ACT_CASH_FI_MAX_TICKET_GR"
TICKET_BANK_GR4 = "PCB_ACT_CASH_BANK_TICKET_GR4"
TICKET_FI_GR4 = "PCB_ACT_CASH_FI_TICKET_GR4"

TENOR_BANK_COL = "PCB_ACT_CASH_BANK_MAX_TENOR_GR"
TENOR_FI_COL = "PCB_ACT_CASH_FI_MAX_TENOR_GR"


def _ticket_bucket_transform(col: str) -> str:
    """Regroups the 8 raw ticket-size buckets on `col` down to the 4
    requested by the pseudocode. Buckets are prefixed 1./2./3./4. so the
    default alphabetical dim sort (matching every other pre-bucketed GR
    column in this dataset, e.g. PCB_ACT_PROD_GR) renders them in the right
    order with no explicit sort_by."""
    return f"""CASE
        WHEN "{col}" IN ('1. <=10 mil', '2. (10-20] mil') THEN '1. <=20 Mil'
        WHEN "{col}" IN ('3. (20-30] mil', '4. (30-40] mil', '5. (40-50] mil', '6. (50-100] mil') THEN '2. (20, 100] Mil'
        WHEN "{col}" = '7. (100-250] mil' THEN '3. (100, 250] Mil'
        WHEN "{col}" = '8. 250+ mil' THEN '4. 250Mil+'
        ELSE NULL
    END"""


def _register_ticket_bucket_cols(ds: Dataset) -> None:
    """set_cal_col is idempotent to call repeatedly (plain dict reassignment
    + cache clear, see src/dataset.py), so it's safe to call this at the top
    of every plot function in this file rather than requiring main.py to
    register it once up front."""
    ds.set_cal_col(Dimension(name=TICKET_BANK_GR4, transform=_ticket_bucket_transform(TICKET_BANK_COL)))
    ds.set_cal_col(Dimension(name=TICKET_FI_GR4, transform=_ticket_bucket_transform(TICKET_FI_COL)))


def _two_row_stack_100(
    ds: Dataset,
    title: str,
    bank_legend: str,
    bank_filter_col: str,
    fi_legend: str,
    fi_filter_col: str,
    ) -> plt.Figure:
    """Two vertically-stacked 100%-stacked-bar axes in one figure (Bank on
    top, Other FI below) — same per-ax body as pcb_bar.stackbar_single(),
    duplicated here per the one-file-per-topic convention. Can't reuse
    Vizzy.small_multiple() for the layout since it only builds a horizontal
    row of axes; the suptitle-left-align-after-layout trick is borrowed from
    it directly instead."""
    with plt.rc_context({"font.size": FONT_SIZE}):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIG_SIZE)

        for ax, legend, filter_col, ax_title in (
            (ax1, bank_legend, bank_filter_col, "Bank"),
            (ax2, fi_legend, fi_filter_col, "Other FI"),
        ):
            bar = Vizzy(fig, ax, ds).stack_bar_100(
                dim=DIM, measure=MEASURE, legend=legend,
                filters=f"{filter_col} IS NOT NULL",
            )
            bar.set_theme(pal=COLOR_THEME)
            bar.show_data_label()
            ax.set_ylim(0, 105)

            ax.set_title(ax_title, loc="left", style="italic", size=FONT_SIZE)
            ax.tick_params(axis="y", left=False, labelleft=False)

            for s in ax.spines.values():
                s.set_visible(False)

            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)

            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)

        # Placeholder suptitle (x corrected below) added BEFORE tight_layout()
        # so tight_layout() reserves top-margin room for it — same ordering
        # Vizzy.small_multiple() uses for its own suptitle.
        suptitle = fig.suptitle(title, x=0, ha="left")

        fig.tight_layout()

        x0 = ax1.get_position().x0
        suptitle.set_x(x0)

    return fig


@register_plot("quest_3_2")
def quest3_2_1(ds: Dataset):
    _register_ticket_bucket_cols(ds)
    return _two_row_stack_100(
        ds,
        title="Since they have a higher share of small ticket Cash loan",
        bank_legend=TICKET_BANK_GR4,
        bank_filter_col=TICKET_BANK_COL,
        fi_legend=TICKET_FI_GR4,
        fi_filter_col=TICKET_FI_COL,
    )


@register_plot("quest_3_2")
def quest3_2_2(ds: Dataset):
    return _two_row_stack_100(
        ds,
        title="...and slightly higher share of small tenor Cash loan",
        bank_legend=TENOR_BANK_COL,
        bank_filter_col=TENOR_BANK_COL,
        fi_legend=TENOR_FI_COL,
        fi_filter_col=TENOR_FI_COL,
    )
