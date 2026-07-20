"""SimpleBar/StackBar plot() geometry, validation, and shared show_data_label/
set_theme behavior. Assertion-based only — actual visual correctness is
judged by eye via tests/gallery/, not here."""

import matplotlib.colors as mcolors
import numpy as np
import pytest

from src.charts.bar import (
    SimpleBarH,
    SimpleBarV,
    StackBar100H,
    StackBar100V,
    StackBarH,
    StackBarV,
)
from src.custom.colors import get_theme_colors
from src.dataset import Dimension, Measure, ResultDimension, ResultLegend, ResultMeasure

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


def _dim(value=DIMENSION):
    return ResultDimension(name="dim", value=value, result_from=Dimension(name="dim"))


def _mes(value, name="measure"):
    return ResultMeasure(name=name, value=value, result_from=Measure(name=name, formula="sum(x)"))


def _lgd(value=LEGENDS):
    return ResultLegend(name="legend", value=value, result_from=Dimension(name="legend"))


class TestSimpleBar:
    def test_rejects_2d_measures(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            SimpleBarV(fig, ax).plot(_dim(), _mes(MEASURES_2D))

    def test_vertical_bar_heights_match_measures(self, fig_ax):
        fig, ax = fig_ax
        bar = SimpleBarV(fig, ax).plot(_dim(), _mes(MEASURES_1D))
        heights = [p.get_height() for p in bar.bars.patches]
        assert heights == list(MEASURES_1D)

    def test_horizontal_bar_widths_match_measures(self, fig_ax):
        fig, ax = fig_ax
        bar = SimpleBarH(fig, ax).plot(_dim(), _mes(MEASURES_1D))
        widths = [p.get_width() for p in bar.bars.patches]
        assert widths == list(MEASURES_1D)

    def test_show_data_label_writes_one_label_per_category(self, fig_ax):
        fig, ax = fig_ax
        bar = SimpleBarV(fig, ax).plot(_dim(), _mes(MEASURES_1D))
        bar.show_data_label()
        assert [t.get_text() for t in ax.texts] == ["1", "2", "3"]

    def test_show_data_label_hides_labels_below_threshold(self, fig_ax):
        fig, ax = fig_ax
        bar = SimpleBarV(fig, ax).plot(_dim(), _mes(MEASURES_1D))
        bar.show_data_label(thresh_hold=2)
        assert [t.get_text() for t in ax.texts] == ["", "2", "3"]

    def test_format_measure_scales_labels_and_strips_unit_suffix(self, fig_ax):
        fig, ax = fig_ax
        measures = np.array([1_000_000.0, 2_000_000.0, 3_000_000.0])
        bar = SimpleBarV(fig, ax).plot(_dim(), _mes(measures))
        bar.format_measure(fmt="#,M", dedup_fmt=True)
        bar.show_data_label()
        # texts[0] is the subtitle format_measure() drew; labels follow.
        assert [t.get_text() for t in ax.texts[1:]] == ["1", "2", "3"]

    def test_format_measure_draws_subtitle_with_unit(self, fig_ax):
        fig, ax = fig_ax
        measures = np.array([1_000_000.0, 2_000_000.0, 3_000_000.0])
        bar = SimpleBarV(fig, ax).plot(_dim(), _mes(measures, name="Sales"))
        bar.format_measure(fmt="#,M", dedup_fmt=True)
        bar.show_data_label()
        assert ax.texts[0].get_text() == "Sales (in Millions)"

    def test_threshold_compares_raw_values_not_scaled_display(self, fig_ax):
        fig, ax = fig_ax
        measures = np.array([1_000_000.0, 2_000_000.0, 3_000_000.0])
        bar = SimpleBarV(fig, ax).plot(_dim(), _mes(measures))
        bar.format_measure(fmt="#,M", dedup_fmt=True)
        bar.show_data_label(thresh_hold=2_000_000)
        assert [t.get_text() for t in ax.texts[1:]] == ["", "2", "3"]


class TestStackBar:
    def test_rejects_1d_measures(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            StackBarV(fig, ax).plot(_dim(), _mes(MEASURES_1D), _lgd())

    def test_requires_legends(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            StackBarV(fig, ax).plot(_dim(), _mes(MEASURES_2D), None)

    def test_vertical_first_segment_heights_match_first_legend_column(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarV(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        heights = [p.get_height() for p in bar.bars[0].patches]
        assert heights == list(MEASURES_2D[:, 0])

    def test_vertical_second_segment_sits_on_top_of_first(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarV(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        bottoms = [p.get_y() for p in bar.bars[1].patches]
        assert bottoms == list(MEASURES_2D[:, 0])

    def test_vertical_stack_total_equals_sum_of_segments(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarV(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        totals = [
            bar.bars[0].patches[i].get_height() + bar.bars[1].patches[i].get_height()
            for i in range(len(DIMENSION))
        ]
        assert totals == list(MEASURES_2D.sum(axis=1))

    def test_horizontal_second_segment_sits_right_of_first(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarH(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        widths = [p.get_width() for p in bar.bars[0].patches]
        lefts = [p.get_x() for p in bar.bars[1].patches]
        assert widths == list(MEASURES_2D[:, 0])
        assert lefts == list(MEASURES_2D[:, 0])

    def test_show_data_label_writes_one_label_per_segment_per_category(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarV(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        bar.show_data_label(show_total=False)
        # bar_label() is called once per legend container, in legend order,
        # so labels flatten legend-major/category-minor: column 0's three
        # categories, then column 1's.
        expected = [f"{v:.0f}" for v in MEASURES_2D.T.flatten()]
        assert [t.get_text() for t in ax.texts] == expected

    def test_show_data_label_also_writes_total_label_by_default(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBarV(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        bar.show_data_label()
        segment_labels = [f"{v:.0f}" for v in MEASURES_2D.T.flatten()]
        total_labels = [f"{v:.0f}" for v in MEASURES_2D.sum(axis=1)]
        assert [t.get_text() for t in ax.texts] == segment_labels + total_labels

    def test_format_measure_strips_unit_from_segments_and_total(self, fig_ax):
        fig, ax = fig_ax
        measures = MEASURES_2D * 1_000_000
        bar = StackBarV(fig, ax).plot(_dim(), _mes(measures), _lgd())
        bar.format_measure(fmt="#,M", dedup_fmt=True)
        bar.show_data_label()
        data_labels = [t.get_text() for t in ax.texts[1:]]  # texts[0] is the subtitle
        assert not any("M" in label for label in data_labels)

    def test_format_measure_draws_subtitle_once_across_repeat_label_calls(self, fig_ax):
        fig, ax = fig_ax
        measures = MEASURES_2D * 1_000_000
        bar = StackBarV(fig, ax).plot(_dim(), _mes(measures, name="Sales"), _lgd())
        bar.format_measure(fmt="#,M", dedup_fmt=True)
        bar.show_data_label()
        bar.show_data_label()  # calling again shouldn't redraw the subtitle
        subtitle_matches = [t for t in ax.texts if t.get_text() == "Sales (in Millions)"]
        assert len(subtitle_matches) == 1

    def test_set_theme_colors_each_segment_from_the_palette_in_order(self, fig_ax):
        fig, ax = fig_ax
        colors = get_theme_colors("cate-55")
        bar = StackBarV(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        bar.set_theme(pal="cate-55", tone=None)
        for j, container in enumerate(bar.bars):
            expected = mcolors.to_rgba(colors[j])
            for patch in container.patches:
                assert patch.get_facecolor() == expected

    def test_set_theme_refreshes_legend_swatch_colors(self, fig_ax):
        fig, ax = fig_ax
        colors = get_theme_colors("cate-55")
        bar = StackBarV(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        bar.set_theme(pal="cate-55", tone=None)
        legend_colors = [h.get_facecolor() for h in ax.get_legend().legend_handles]
        assert legend_colors == [mcolors.to_rgba(c) for c in colors[: len(LEGENDS)]]


class TestStackBar100:
    def test_rejects_1d_measures(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            StackBar100V(fig, ax).plot(_dim(), _mes(MEASURES_1D), _lgd())

    def test_requires_legends(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            StackBar100V(fig, ax).plot(_dim(), _mes(MEASURES_2D), None)

    def test_vertical_segments_sum_to_100_per_category(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBar100V(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        totals = [
            bar.bars[0].patches[i].get_height() + bar.bars[1].patches[i].get_height()
            for i in range(len(DIMENSION))
        ]
        assert totals == pytest.approx([100.0, 100.0, 100.0])

    def test_segments_stay_proportional_to_original_ratios(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBar100V(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        first_segment_pct = [p.get_height() for p in bar.bars[0].patches]
        expected_pct = list(MEASURES_2D[:, 0] / MEASURES_2D.sum(axis=1) * 100)
        assert first_segment_pct == pytest.approx(expected_pct)

    def test_horizontal_segments_sum_to_100_per_category(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBar100H(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        totals = [
            bar.bars[0].patches[i].get_width() + bar.bars[1].patches[i].get_width()
            for i in range(len(DIMENSION))
        ]
        assert totals == pytest.approx([100.0, 100.0, 100.0])

    def test_zero_total_category_normalizes_to_zero_not_nan(self, fig_ax):
        fig, ax = fig_ax
        measures = np.array([[0.0, 0.0], [3.0, 4.0], [5.0, 6.0]])
        bar = StackBar100V(fig, ax).plot(_dim(), _mes(measures), _lgd())
        heights = [bar.bars[0].patches[0].get_height(), bar.bars[1].patches[0].get_height()]
        assert heights == [0.0, 0.0]

    def test_show_data_label_omits_total_by_default(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBar100V(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        bar.show_data_label()
        assert len(ax.texts) == 2 * len(DIMENSION)

    def test_show_data_label_can_still_show_total(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBar100V(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        bar.show_data_label(show_total=True)
        assert len(ax.texts) == 3 * len(DIMENSION)

    def test_format_measure_hash_fmt_renders_normalized_values_unchanged(self, fig_ax):
        fig, ax = fig_ax
        bar = StackBar100V(fig, ax).plot(_dim(), _mes(MEASURES_2D), _lgd())
        bar.format_measure(fmt="#")
        bar.show_data_label()
        expected = [f"{v:.0f}" for v in (MEASURES_2D / MEASURES_2D.sum(axis=1, keepdims=True) * 100).T.flatten()]
        assert [t.get_text() for t in ax.texts] == expected
