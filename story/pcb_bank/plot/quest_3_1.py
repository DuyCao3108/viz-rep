from __future__ import annotations

import matplotlib.pyplot as plt

from plot.base import register_plot
from src.dataset import Dataset
from src.vizzy import Vizzy
from src.custom.fonts import resolve_installed_font

COLOR_THEME = 'cate-25'
plt.rcParams['font.family'] = resolve_installed_font('Arial', 'Helvetica', 'DejaVu Sans')
FONT_SIZE = 12
FIG_SIZE = (16/2, 8)


def _widen_bars(bar, width: float) -> None:
    """StackBar._chart_plot() (src/charts/bar.py) draws every segment at the
    fixed class-level Bar.BAR_WIDTH before we ever get the chart object back,
    so there's no plot()-time hook to request a different width. Resize the
    already-drawn Rectangle patches in place instead — same workaround as
    story/pcb_bank/plot/quest_2_2.py's/pcb_bar.py's _widen_bars, duplicated
    here to match this project's one-file-per-topic convention rather than
    imported."""
    is_vertical = bar.DIM_AXIS == "x"
    for container in bar.bars:
        for patch in container.patches:
            if is_vertical:
                center = patch.get_x() + patch.get_width() / 2
                patch.set_x(center - width / 2)
                patch.set_width(width)
            else:
                center = patch.get_y() + patch.get_height() / 2
                patch.set_y(center - width / 2)
                patch.set_height(width)


def _channel_mix_multiple(
    ds: Dataset,
    dim: str,
    facet: str,
    measure: str,
    legend: str,
    title: str,
    bar_width: float = 0.9,
    ) -> plt.Figure:
    """Template for a row of 100%-stacked-bar small multiples showing product
    mix (one ax per `facet` category). Same shape as quest_2_2._channel_mix_
    multiple — duplicated here (not imported) per the one-file-per-topic
    convention, using this file's own FIG_SIZE (standalone full-width chart,
    not a split-row chart) instead of quest_2_2's 16/2 baseline."""
    with plt.rc_context({"font.size": FONT_SIZE}):
        facet_in = {
            '2. Active HCVN X BANK': '2. Active HCVN X BANK',
            '3. Active HCVN X FI': '1. Active HCVN X FI',
        }

        facet_vals = ds.query(dim=facet, measure=measure).categories.value
        facet_vals = [v for v in facet_vals if v in facet_in]
        facet_vals = sorted(facet_vals, key=lambda v: facet_in[v])

        # Some facet x legend combos have zero rows — StackBar100's
        # percent-label formatter can't vectorize over a size-0 array, so
        # drop empty facets before building the small multiple rather than
        # rendering a blank ax.
        facet_vals = [
            val for val in facet_vals
            if ds.query(
                dim=dim, measure=measure, legend=legend,
                filters=f"{facet} = '{val}' AND {legend} IS NOT NULL",
            ).values.value.size > 0
        ]
        facet_vals = [v for v in facet_vals if v in facet_in]
        facet_vals = sorted(facet_vals, key=lambda v: facet_in[v])

        def plot_fn(ax, val):
            fig = ax.get_figure()
            bar = Vizzy(fig, ax, ds).stack_bar_100(
                dim=dim, measure=measure, legend=legend,
                filters=f"{facet} = '{val}' AND {legend} IS NOT NULL",
            )
            bar.set_theme(pal=COLOR_THEME, tone=None)
            _widen_bars(bar, bar_width)
            bar.show_data_label()
            ax.set_ylim(0, 105)

            ax.set_title(facet_in[val], loc="left", style="italic", size=FONT_SIZE)
            ax.tick_params(axis="y", left=False, labelleft=False)

            for s in ax.spines.values():
                s.set_visible(False)

            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)

        fig, axes = Vizzy.small_multiple(
            facet_vals=facet_vals,
            plot_fn=plot_fn,
            # FIG_SIZE alone is too narrow once split across many facets
            # (titles/tick labels start overlapping) — scale width by facet
            # count, using FIG_SIZE as the per-2-facet baseline so a
            # 2-facet chart still renders at exactly FIG_SIZE.
            figsize=(max(FIG_SIZE[0], FIG_SIZE[0] * len(facet_vals) / 2), FIG_SIZE[1]),
            title=title,
            legend_loc="bottom_center",
        )

        # Legend height varies with the number of legend entries — re-measure
        # and reserve room, same pattern as quest_2_2._channel_mix_multiple.
        fig_legend = fig.legends[-1]
        fig_legend.set_frame_on(False)
        fig.canvas.draw()
        legend_height = (
            fig_legend.get_window_extent(fig.canvas.get_renderer())
            .transformed(fig.transFigure.inverted())
            .height
        )
        fig.subplots_adjust(bottom=legend_height + 0.14)

    return fig


@register_plot("quest_3_1")
def quest3_1_1(ds: Dataset):
    return _channel_mix_multiple(
        ds,
        dim="DATE_REPORT_QUARTER",
        facet="PCB_XS_LENDER_GR",
        measure="# Client prime",
        legend="PCB_ACT_PROD_GR",
        title="BANK users have more % of active PCB with only Card",
    )


@register_plot("quest_3_1")
def quest3_1_2(ds: Dataset):
    return _channel_mix_multiple(
        ds,
        dim="DATE_REPORT_QUARTER",
        facet="PCB_XS_LENDER_GR",
        measure="# Client prime",
        legend="HIST_PROD_XS_GR",
        title="...and more % of only has experience with Card from HCVN",
    )
