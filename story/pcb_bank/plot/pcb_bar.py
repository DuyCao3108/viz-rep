"""Client prime mix by XS lender — 100%-stacked bar, per quarter."""

from __future__ import annotations

import matplotlib.pyplot as plt

from plot.base import register_plot
from src.dataset import Dataset
from src.vizzy import Vizzy
from src.custom.fonts import resolve_installed_font

COLOR_THEME='powerbi'
plt.rcParams['font.family'] = resolve_installed_font('Arial', 'Helvetica', 'DejaVu Sans')


def _widen_bars(bar, width: float) -> None:
    """StackBar._chart_plot() (src/charts/bar.py) draws every segment at the
    fixed class-level Bar.BAR_WIDTH (0.6) before we ever get the chart object
    back, so there's no plot()-time hook to request a different width.
    Resize the already-drawn Rectangle patches in place instead, re-centering
    each on its original position — avoids touching src for a per-chart
    cosmetic tweak."""
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

def stackbar_multiple(
    ds: Dataset,
    dim: str,
    facet: str,
    measure: str,
    legend: str,
    title: str,
    bar_width: float = 0.9,
    figsize_per_facet: float = 2.4,
    min_figsize_width: float = 10.0,
    figsize_height: float = 5.5,
    tick_rotation: float = 30,
    ) -> plt.Figure:
    """Template for a row of 100%-stacked-bar small multiples (one ax per
    `facet` category). Reuse by calling this with new dim/facet/measure/
    legend/title args — don't fork the body; tune bar_width/figsize_*/
    tick_rotation per chart instead.

    rc_context (not a bare plt.rcParams assignment) so the font-size-8
    override doesn't leak into whichever chart renders next in the same
    process — main.py calls every registered plot function back to back."""
    with plt.rc_context({"font.size": 8}):
        facet_vals = ds.query(dim=facet, measure=measure).categories.value
        n = len(facet_vals)

        def plot_fn(ax, val):
            fig = ax.get_figure()
            bar = Vizzy(fig, ax, ds).stack_bar_100(
                dim=dim, measure=measure, legend=legend,
                filters=f"{facet} = '{val}' AND {legend} IS NOT NULL",
            )
            bar.set_theme(pal=COLOR_THEME, tone=None)
            _widen_bars(bar, bar_width)
            bar.show_data_label()

            # A StackBar100's total is always 100 and its labels are
            # center-anchored inside each segment (no edge label needing
            # headroom above the bar) — clamp back the inherited
            # cmax*1.18 ylim that otherwise leaves ~18% blank space between
            # the tallest bar and the ax title sitting right above it.
            ax.set_ylim(0, 105)

            ax.set_title(val, loc="left", style="italic", size=8)
            ax.tick_params(axis="y", left=False, labelleft=False)

            # Quarter labels collide at the default horizontal alignment
            # once each facet's plot width shrinks (more facets = narrower
            # ax) — rotating lets them stack diagonally instead of into
            # each other.
            for tick_label in ax.get_xticklabels():
                # tick_label.set_rotation(tick_rotation)
                # tick_label.set_ha("right")
                pass

            for s in ax.spines.values():
                s.set_visible(False)

            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)

        fig, axes = Vizzy.small_multiple(
            facet_vals=facet_vals,
            plot_fn=plot_fn,
            # Fluid width: a fixed figsize forces more facets into the same
            # space, which is what was squeezing the dimension labels
            # together — scale with facet count instead, floored so a
            # 2-3-facet chart doesn't end up too cramped either.
            figsize=(max(min_figsize_width, figsize_per_facet * n), figsize_height),
            title=title,
            legend_loc="bottom_center",
        )

        # small_multiple() sizes the bottom margin to the legend's own
        # rendered height only — it can't account for the tick-label
        # rotation applied above (that happens inside plot_fn, before
        # small_multiple's own layout pass reads label bboxes), so the
        # reserved room ends up too tight and the legend collides with the
        # now-taller x-axis labels. Re-measure and pad further, and drop the
        # legend's border per request.
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

def stackbar_single(
    ds: Dataset,
    dim: str,
    measure: str,
    legend: str,
    title: str,
    pal: str = "step5-blue",
    ) -> plt.Figure:
    """Template for a single (no-facet) 100%-stacked-bar chart. Reuse by
    calling this with new dim/measure/legend/title/pal args — don't fork the
    body."""
    plt.rcParams['font.size']=12.5
    fig, ax = plt.subplots(figsize=(8, 6))

    bar = Vizzy(fig, ax, ds).stack_bar_100(
        dim=dim,
        measure=measure,
        legend=legend,
    )
    bar.set_theme(pal=pal)
    bar.show_data_label()

    for s in ax.spines.values():
        s.set_visible(False)

    ax.spines['top'].set_visible(True)
    ax.spines['bottom'].set_visible(True)


    ax.set_title(title, loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=3, frameon=False)

    # custom
    ax.set_ylim(0,105)

    fig.tight_layout()

    return fig

@register_plot("pcb_bar")
def stackbar_single_prime_vs_competitor(ds: Dataset):
    return stackbar_single(
        ds,
        dim="DATE_REPORT_QUARTER",
        measure="# Client prime",
        legend="F_ACT_PCB_XS",
        title="50% of prime client having active CL/CC contract with competitor",
    )

@register_plot("pcb_bar")
def stackbar_multi_5(ds: Dataset):
    return stackbar_multiple(
        ds,
        dim="DATE_REPORT_QUARTER",
        facet="PCB_XS_LENDER_GR",
        measure="# Client prime",
        legend="SCOR_FST_BOD0_CHANNEL",
        title="Client prime mix by XS lender, per quarter, by HCVN active product group",
    )
