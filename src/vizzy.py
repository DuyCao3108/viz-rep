"""Vizzy: the public entry point. Always constructed against a caller-owned
fig/ax (matplotlib never created internally). One method per chart family
(.bar()/.barh()/.line()), each querying the Dataset and returning the
concrete chart object it built — no wrapping, no shared post-hoc styling
facade. Customization is whatever methods that returned object implements
directly."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import numpy as np

from src.dataset import Dataset
from src.charts.base import get_shape_class
from src.charts.bar import (
    SimpleBarH,
    SimpleBarV,
    StackBar100H,
    StackBar100V,
    StackBarH,
    StackBarV,
)
from src.charts.line import Line
from src import charts  # noqa: F401 — runs @register_shape decorators

from icecream import ic

class Vizzy:
    def __init__(self, fig, ax, dataset: Dataset) -> None:
        self.fig = fig
        self.ax = ax
        self.dataset = dataset

    def bar(self, dim: str, measure: str, legend: str | None = None,
             filters: str | None = None, sort_by: dict | None = None,
             shape: str = "simple_bar")-> SimpleBarV:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def barh(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "h_simple_bar")-> SimpleBarH:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def stack_bar(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "stack_bar")-> StackBarV:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def h_stack_bar(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "h_stack_bar") -> StackBarH:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def stack_bar_100(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "stack_100_bar")-> StackBar100V:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def h_stack_bar_100(self, dim: str, measure: str, legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "h_stack_100_bar") -> StackBar100H:
        return self._build(shape, dim, measure, legend, filters, sort_by)

    def line(self, dim: str, measure: str | list[str], legend: str | None = None,
              filters: str | None = None, sort_by: dict | None = None,
              shape: str = "line") -> Line:
        measure_names = [measure] if isinstance(measure, str) else list(measure)
        if len(measure_names) > 1 and legend is not None:
            raise ValueError(
                "Vizzy.line(): multi-measure mode (measure=list[str]) can't be "
                "combined with a legend. Query one measure per line, or drop legend."
            )
        results = [
            self.dataset.query(dim=dim, measure=name, legend=legend,
                                filters=filters, sort_by=sort_by)
            for name in measure_names
        ]
        chart = get_shape_class(shape)(fig=self.fig, ax=self.ax)
        chart.plot(results[0].categories, [r.values for r in results], results[0].legend_categories)
        return chart

    @staticmethod
    def small_multiple(
        facet_vals: list,
        plot_fn,
        figsize: tuple[float, float] = (18, 6),
        sharex: bool = True,
        sharey: bool = True,
        title: str | None = None,
        ncol: int | None = None,
        legend_loc: Literal["bottom_left", "bottom_center"] = "bottom_left",
        f_show_legend: bool = True,
    ):

        """Generic facet-grid helper: builds one row of axes (one per
        facet_vals entry), calls plot_fn(ax, facet_val) to let the caller do
        the actual per-facet querying/styling, then (if f_show_legend)
        consolidates one shared fig-level legend (legend_loc="bottom_left":
        single column pinned to the figure's bottom-left corner;
        "bottom_center": single row, one column per legend entry, centered)
        and (if title given) a suptitle aligned to the first facet's
        ax.set_title(loc='left') — not a hardcoded x position, which drifts
        whenever layout params change."""
        n = len(facet_vals)
        fig, axes = plt.subplots(1, n, figsize=figsize, sharex=sharex, sharey=sharey)
        axes_flat = list(np.atleast_1d(axes).flat)

        for val, ax in zip(facet_vals, axes_flat):
            plot_fn(ax, val)

        if f_show_legend:
            handles, labels = axes_flat[0].get_legend_handles_labels()
            legend_ncol = ncol if ncol is not None else len(labels)
            for ax in axes_flat:
                legend = ax.get_legend()
                if legend is not None:
                    legend.remove()

            if legend_loc == "bottom_center":
                fig_legend = fig.legend(
                    handles, labels, loc="lower center", bbox_to_anchor=(0.55, 0.05),
                    ncol=legend_ncol, handleheight=1, handlelength=2,
                )
            else:
                fig_legend = fig.legend(handles, labels, loc="outside lower center", bbox_to_anchor=(0, 0))

        # Placeholder suptitle (x corrected below) added BEFORE tight_layout()
        # so tight_layout() reserves top-margin room for it — adding it after
        # layout is finalized leaves no vertical room and it collides with
        # ax[0]'s own title.
        suptitle = fig.suptitle(title, x=0, ha="left") if title is not None else None

        fig.tight_layout()
        fig.subplots_adjust(left=0.16)

        if f_show_legend:
            # Reserve bottom margin for the fig-level legend based on its
            # actual rendered height — tight_layout() only accounts for axes
            # content, not fig.legend(), and "bottom_center" (one row) vs.
            # "bottom_left" (one column per label) occupy very different
            # heights, so a fixed margin would be wrong for one of the two.
            # Without this, the legend (anchored at fig y=0) sits underneath
            # the axes with no guaranteed clearance and gets clipped unless
            # the caller saves with bbox_inches="tight".
            fig.canvas.draw()
            legend_height = (
                fig_legend.get_window_extent(fig.canvas.get_renderer())
                .transformed(fig.transFigure.inverted())
                .height
            )
            fig.subplots_adjust(bottom=legend_height + 0.04)

        if suptitle is not None:
            # x is corrected AFTER layout is finalized, since tight_layout()/
            # subplots_adjust() are what determine ax[0]'s real left edge —
            # this is the alignment fix (was hardcoded, drifted from ax[0]'s
            # title position whenever layout params changed).
            x0 = axes_flat[0].get_position().x0
            suptitle.set_x(x0)

        return fig, axes

    def _build(self, shape_name: str, dim: str, measure: str, legend, filters, sort_by=None):
        result = self.dataset.query(dim=dim, measure=measure, legend=legend,
                                     filters=filters, sort_by=sort_by)
        chart = get_shape_class(shape_name)(fig=self.fig, ax=self.ax)
        chart.plot(result.categories, result.values, result.legend_categories)
        return chart
