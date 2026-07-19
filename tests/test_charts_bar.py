"""SimpleBar/StackBar plot() geometry, validation, and shared show_data_label/
set_theme behavior. Assertion-based only — actual visual correctness is
judged by eye via tests/gallery/, not here."""

import matplotlib.colors as mcolors
import numpy as np
import pytest

from src.charts.bar import SimpleBarH, SimpleBarV, StackBarH, StackBarV
from src.custom.colors import get_theme_colors

DIMENSION = ["A", "B", "C"]
LEGENDS = ["x", "y"]
MEASURES_1D = np.array([1.0, 2.0, 3.0])
MEASURES_2D = np.array(
    [
        [1.0, 2.0],
        [3.0, 4.0],
        [5.0, 6.0],
    ]
)


class TestSimpleBar:
    def test_rejects_2d_measures(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            SimpleBarV(fig, ax).plot(DIMENSION, MEASURES_2D)

    def test_vertical_bar_heights_match_measures(self, fig_ax):
        fig, ax = fig_ax
        bar = SimpleBarV(fig, ax).plot(DIMENSION, MEASURES_1D)
        heights = [p.get_height() for p in bar.bars.patches]
        assert heights == list(MEASURES_1D)

    def test_horizontal_bar_widths_match_measures(self, fig_ax):
        fig, ax = fig_ax
        bar = SimpleBarH(fig, ax).plot(DIMENSION, MEASURES_1D)
        widths = [p.get_width() for p in bar.bars.patches]
        assert widths == list(MEASURES_1D)

    def test_show_data_label_writes_one_label_per_category(self, fig_ax):
        fig, ax = fig_ax
        bar = SimpleBarV(fig, ax).plot(DIMENSION, MEASURES_1D)
        bar.show_data_label()
        assert [t.get_text() for t in ax.texts] == ["1", "2", "3"]

    def test_show_data_label_hides_labels_below_threshold(self, fig_ax):
        fig, ax = fig_ax
        bar = SimpleBarV(fig, ax).plot(DIMENSION, MEASURES_1D)
        bar.show_data_label(thresh_hold=2)
        assert [t.get_text() for t in ax.texts] == ["", "2", "3"]


class TestStackBar:
    def test_rejects_1d_measures(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            StackBarV(fig, ax).plot(DIMENSION, MEASURES_1D, LEGENDS)

    def test_requires_legends(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            StackBarV(fig, ax).plot(DIMENSION, MEASURES_2D, None)

    def test_vertical_first_segment_heights_match_first_legend_column(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarV(fig, ax).plot(DIMENSION, MEASURES_2D, LEGENDS)
        heights = [p.get_height() for p in bar.bars[0].patches]
        assert heights == list(MEASURES_2D[:, 0])

    def test_vertical_second_segment_sits_on_top_of_first(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarV(fig, ax).plot(DIMENSION, MEASURES_2D, LEGENDS)
        bottoms = [p.get_y() for p in bar.bars[1].patches]
        assert bottoms == list(MEASURES_2D[:, 0])

    def test_vertical_stack_total_equals_sum_of_segments(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarV(fig, ax).plot(DIMENSION, MEASURES_2D, LEGENDS)
        totals = [
            bar.bars[0].patches[i].get_height() + bar.bars[1].patches[i].get_height()
            for i in range(len(DIMENSION))
        ]
        assert totals == list(MEASURES_2D.sum(axis=1))

    def test_horizontal_second_segment_sits_right_of_first(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarH(fig, ax).plot(DIMENSION, MEASURES_2D, LEGENDS)
        widths = [p.get_width() for p in bar.bars[0].patches]
        lefts = [p.get_x() for p in bar.bars[1].patches]
        assert widths == list(MEASURES_2D[:, 0])
        assert lefts == list(MEASURES_2D[:, 0])

    def test_show_data_label_writes_one_label_per_segment_per_category(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarV(fig, ax).plot(DIMENSION, MEASURES_2D, LEGENDS)
        bar.show_data_label()
        # bar_label() is called once per legend container, in legend order,
        # so labels flatten legend-major/category-minor: column 0's three
        # categories, then column 1's.
        expected = [f"{v:.0f}" for v in MEASURES_2D.T.flatten()]
        assert [t.get_text() for t in ax.texts] == expected

    def test_set_theme_colors_each_segment_from_the_palette_in_order(self, fig_ax):
        fig, ax = fig_ax
        colors = get_theme_colors("cate-55")
        bar = StackBarV(fig, ax).plot(DIMENSION, MEASURES_2D, LEGENDS)
        bar.set_theme(pal="cate-55", tone=None)
        for j, container in enumerate(bar.bars):
            expected = mcolors.to_rgba(colors[j])
            for patch in container.patches:
                assert patch.get_facecolor() == expected

    def test_set_theme_refreshes_legend_swatch_colors(self, fig_ax):
        fig, ax = fig_ax
        colors = get_theme_colors("cate-55")
        bar = StackBarV(fig, ax).plot(DIMENSION, MEASURES_2D, LEGENDS)
        bar.set_theme(pal="cate-55", tone=None)
        legend_colors = [h.get_facecolor() for h in ax.get_legend().legend_handles]
        assert legend_colors == [mcolors.to_rgba(c) for c in colors[: len(LEGENDS)]]
