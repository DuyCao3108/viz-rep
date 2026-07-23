"""Line plot() geometry, validation, and show_data_label/format_measure/
set_theme/set_line_style behavior. Assertion-based only — actual visual
correctness is judged by eye via tests/gallery/, not here."""

import matplotlib.colors as mcolors
import numpy as np
import pytest

from src.charts.line import AdjustPos, LegendLabelAdjustPos, Line
from src.custom.colors import get_theme_colors
from src.dataset import Dimension, Measure, ResultDimension, ResultLegend, ResultMeasure

DIMENSION = ["Jan", "Feb", "Mar"]
LEGENDS = ["North", "South"]
MEASURE_A = np.array([1.0, 2.0, 3.0])
MEASURE_B = np.array([10.0, 20.0, 30.0])
MEASURE_2D = np.array(
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


class TestValidation:
    def test_rejects_multi_measure_with_legend(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")], _lgd())

    def test_rejects_zero_measures(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            Line(fig, ax).plot(_dim(), [], None)

    def test_rejects_legend_with_zero_measures(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            Line(fig, ax).plot(_dim(), [], _lgd())

    def test_rejects_legend_with_two_measures(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")], _lgd())

    def test_accepts_single_measure_no_legend(self, fig_ax):
        fig, ax = fig_ax
        Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)], None)  # no raise

    def test_rejects_legend_with_1d_measure(self, fig_ax):
        fig, ax = fig_ax
        with pytest.raises(ValueError):
            Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)], _lgd())


class TestMultiMeasureGeometry:
    def test_each_series_ydata_matches_its_measure_array(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        assert list(line._mes_maps["a"]["line"].get_ydata()) == list(MEASURE_A)
        assert list(line._mes_maps["b"]["line"].get_ydata()) == list(MEASURE_B)

    def test_mes_maps_keyed_by_bare_measure_name(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        assert set(line._mes_maps.keys()) == {"a", "b"}

    def test_single_series_draws_no_legend(self, fig_ax):
        fig, ax = fig_ax
        Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        assert ax.get_legend() is None

    def test_multi_measure_draws_legend_with_measure_name_labels(self, fig_ax):
        fig, ax = fig_ax
        Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        legend = ax.get_legend()
        assert legend is not None
        assert [t.get_text() for t in legend.get_texts()] == ["a", "b"]


class TestLegendModeGeometry:
    def test_each_series_ydata_matches_its_legend_column(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_2D, "amt")], _lgd())
        assert list(line._mes_maps["amt_North"]["line"].get_ydata()) == list(MEASURE_2D[:, 0])
        assert list(line._mes_maps["amt_South"]["line"].get_ydata()) == list(MEASURE_2D[:, 1])

    def test_mes_maps_keyed_by_measure_and_legend_label(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_2D, "amt")], _lgd())
        assert set(line._mes_maps.keys()) == {"amt_North", "amt_South"}

    def test_legend_mode_draws_legend_with_legend_labels(self, fig_ax):
        fig, ax = fig_ax
        Line(fig, ax).plot(_dim(), [_mes(MEASURE_2D, "amt")], _lgd())
        legend = ax.get_legend()
        assert legend is not None
        assert [t.get_text() for t in legend.get_texts()] == ["North", "South"]


class TestShowDataLabel:
    def test_writes_one_label_per_point(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.show_data_label()
        assert [t.get_text() for t in ax.texts] == ["1", "2", "3"]

    def test_multi_series_writes_labels_for_every_series(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.show_data_label()
        assert len(ax.texts) == 6

    def test_label_color_matches_series_line_color(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.set_theme(pal="cate-55", tone=None)
        line.show_data_label()
        colors = get_theme_colors("cate-55")
        for i, t in enumerate(ax.texts[:3]):
            assert mcolors.to_rgba(t.get_color()) == mcolors.to_rgba(colors[0])
        for t in ax.texts[3:]:
            assert mcolors.to_rgba(t.get_color()) == mcolors.to_rgba(colors[1])

    def test_no_adjust_pos_uses_default_offset_for_every_label(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.show_data_label()
        assert [t.xyann for t in ax.texts] == [(0, 8), (0, 8), (0, 8)]

    def test_adjust_pos_matches_by_dimension_value_and_measure_name(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.show_data_label(
            adjust_pos=[AdjustPos(at_dimension_val="Feb", of_measure="a", pad_v=-20, pad_h=3)]
        )
        # texts are drawn a's Jan/Feb/Mar then b's Jan/Feb/Mar, in that order.
        assert ax.texts[1].xyann == (3, -12)  # a/Feb: the matched, adjusted label
        for t in [ax.texts[0], ax.texts[2], ax.texts[3], ax.texts[4], ax.texts[5]]:
            assert t.xyann == (0, 8)

    def test_adjust_pos_without_of_measure_matches_every_series_at_that_dim_val(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.show_data_label(adjust_pos=[AdjustPos(at_dimension_val="Jan", pad_h=7)])
        assert ax.texts[0].xyann == (7, 8)  # a/Jan
        assert ax.texts[3].xyann == (7, 8)  # b/Jan
        assert ax.texts[1].xyann == (0, 8)  # a/Feb untouched

    def test_adjust_pos_of_legend_scopes_to_one_legend_series(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_2D, "amt")], _lgd())
        line.show_data_label(
            adjust_pos=[AdjustPos(at_dimension_val="Jan", of_legend="South", pad_v=5)]
        )
        # texts drawn North's Jan/Feb/Mar then South's Jan/Feb/Mar.
        assert ax.texts[0].xyann == (0, 8)  # North/Jan untouched
        assert ax.texts[3].xyann == (0, 13)  # South/Jan matched

    def test_unmatched_at_dimension_val_raises(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a")])
        with pytest.raises(ValueError):
            line.show_data_label(adjust_pos=[AdjustPos(at_dimension_val="Nope")])

    def test_unmatched_of_measure_raises(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        with pytest.raises(ValueError):
            line.show_data_label(
                adjust_pos=[AdjustPos(at_dimension_val="Jan", of_measure="nope")]
            )

    def test_no_labels_drawn_when_adjust_pos_raises(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a")])
        with pytest.raises(ValueError):
            line.show_data_label(adjust_pos=[AdjustPos(at_dimension_val="Nope")])
        assert len(ax.texts) == 0


class TestResolvePctFmt:
    def test_declared_pct_fmt_renders_percent_labels(self, fig_ax):
        fig, ax = fig_ax
        measures = np.array([0.1, 0.25, 0.5])
        mes = ResultMeasure(
            name="share", value=measures,
            result_from=Measure(name="share", formula="sum(x)", fmt="%.1"),
        )
        line = Line(fig, ax).plot(_dim(), [mes])
        line.show_data_label()
        assert [t.get_text() for t in ax.texts] == ["10.0%", "25.0%", "50.0%"]

    def test_explicit_format_measure_overrides_declared_pct_fmt(self, fig_ax):
        fig, ax = fig_ax
        measures = np.array([0.1, 0.25, 0.5])
        mes = ResultMeasure(
            name="share", value=measures,
            result_from=Measure(name="share", formula="sum(x)", fmt="%.1"),
        )
        line = Line(fig, ax).plot(_dim(), [mes])
        line.format_measure(fmt="#.2")
        line.show_data_label()
        assert [t.get_text() for t in ax.texts] == ["0.10", "0.25", "0.50"]

    def test_no_declared_fmt_leaves_labels_as_plain_numbers(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.show_data_label()
        assert [t.get_text() for t in ax.texts] == ["1", "2", "3"]


class TestFormatMeasure:
    def test_scales_labels_and_strips_unit_suffix(self, fig_ax):
        fig, ax = fig_ax
        measures = np.array([1_000_000.0, 2_000_000.0, 3_000_000.0])
        line = Line(fig, ax).plot(_dim(), [_mes(measures)])
        line.format_measure(fmt="#,M", dedup_fmt=True)
        line.show_data_label()
        assert [t.get_text() for t in ax.texts[1:]] == ["1", "2", "3"]

    def test_draws_subtitle_with_single_measure_name(self, fig_ax):
        fig, ax = fig_ax
        measures = np.array([1_000_000.0, 2_000_000.0, 3_000_000.0])
        line = Line(fig, ax).plot(_dim(), [_mes(measures, name="Sales")])
        line.format_measure(fmt="#,M", dedup_fmt=True)
        line.show_data_label()
        assert ax.texts[0].get_text() == "Sales (in Millions)"

    def test_draws_subtitle_with_shared_name_in_legend_mode(self, fig_ax):
        fig, ax = fig_ax
        measures = MEASURE_2D * 1_000_000
        line = Line(fig, ax).plot(_dim(), [_mes(measures, name="Sales")], _lgd())
        line.format_measure(fmt="#,M", dedup_fmt=True)
        assert ax.texts[0].get_text() == "Sales (in Millions)"

    def test_draws_generic_subtitle_in_multi_measure_mode(self, fig_ax):
        fig, ax = fig_ax
        measures = np.array([1_000_000.0, 2_000_000.0, 3_000_000.0])
        line = Line(fig, ax).plot(
            _dim(), [_mes(measures, name="a"), _mes(measures, name="b")]
        )
        line.format_measure(fmt="#,M", dedup_fmt=True)
        assert ax.texts[0].get_text() == "Values (in Millions)"


class TestAutoTheme:
    def test_plot_applies_default_theme_with_no_explicit_set_theme_call(self, fig_ax):
        fig, ax = fig_ax
        colors = get_theme_colors("cate-30")
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        assert mcolors.to_rgba(line._mes_maps["measure"]["line"].get_color()) == mcolors.to_rgba(colors[0])

    def test_explicit_set_theme_overwrites_the_auto_default(self, fig_ax):
        fig, ax = fig_ax
        colors = get_theme_colors("cate-55")
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.set_theme(pal="cate-55", tone=None)
        assert mcolors.to_rgba(line._mes_maps["measure"]["line"].get_color()) == mcolors.to_rgba(colors[0])


class TestSetTheme:
    def test_colors_each_series_from_the_palette_in_order(self, fig_ax):
        fig, ax = fig_ax
        colors = get_theme_colors("cate-55")
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.set_theme(pal="cate-55", tone=None)
        assert mcolors.to_rgba(line._mes_maps["a"]["line"].get_color()) == mcolors.to_rgba(colors[0])
        assert mcolors.to_rgba(line._mes_maps["b"]["line"].get_color()) == mcolors.to_rgba(colors[1])

    def test_single_series_uses_first_palette_color(self, fig_ax):
        fig, ax = fig_ax
        colors = get_theme_colors("cate-55")
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.set_theme(pal="cate-55", tone=None)
        assert mcolors.to_rgba(line._mes_maps["measure"]["line"].get_color()) == mcolors.to_rgba(colors[0])

    def test_refreshes_legend_swatch_colors_after_recolor(self, fig_ax):
        fig, ax = fig_ax
        colors = get_theme_colors("cate-55")
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.set_theme(pal="cate-55", tone=None)
        legend_colors = [mcolors.to_rgba(h.get_color()) for h in ax.get_legend().legend_handles]
        assert legend_colors == [mcolors.to_rgba(c) for c in colors[:2]]

    def test_minimal_tone_shows_only_bottom_and_left_spines(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.set_theme(tone="minimal")
        assert ax.spines["bottom"].get_visible() is True
        assert ax.spines["left"].get_visible() is True
        assert ax.spines["top"].get_visible() is False
        assert ax.spines["right"].get_visible() is False

    def test_minimal_tone_enables_mes_axis_grid(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.set_theme(tone="minimal")
        assert any(gl.get_visible() for gl in ax.yaxis.get_gridlines())

    def test_science_tone_does_not_raise(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.set_theme(tone="science")  # no raise

    def test_unknown_tone_raises(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        with pytest.raises(ValueError):
            line.set_theme(tone="bogus")


class TestSetMesScale:
    def test_find_smart_scale_returns_min_max_across_all_series(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        assert line._find_smart_scale() == (1.0, 30.0)

    def test_plot_auto_zooms_ylim_to_smart_scale_with_default_padding(self, fig_ax):
        fig, ax = fig_ax
        Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        vmin, vmax = 1.0, 3.0
        pad = (vmax - vmin) * 0.05
        assert ax.get_ylim() == pytest.approx((vmin - pad, vmax + pad))

    def test_plot_sets_n_step_plus_one_ticks_by_default(self, fig_ax):
        fig, ax = fig_ax
        Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        assert len(ax.get_yticks()) == 6

    def test_set_mes_scale_overrides_with_explicit_ylim_and_n_step(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.set_mes_scale(ylim=(0.0, 100.0), n_step=4, std=0.0)
        assert ax.get_ylim() == pytest.approx((0.0, 100.0))
        assert len(ax.get_yticks()) == 5

    def test_set_mes_scale_is_chainable(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        assert line.set_mes_scale() is line

    def test_degenerate_equal_values_do_not_produce_zero_width_ylim(self, fig_ax):
        fig, ax = fig_ax
        flat = np.array([5.0, 5.0, 5.0])
        line = Line(fig, ax).plot(_dim(), [_mes(flat)])
        lo, hi = ax.get_ylim()
        assert lo < hi


class TestSetLineStyle:
    def test_default_style_sets_marker_and_width(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line._set_line_style()
        artist = line._mes_maps["measure"]["line"]
        assert artist.get_marker() == "o"
        assert artist.get_markersize() == 4.5
        assert artist.get_linewidth() == 2.2

    def test_smooth_true_replaces_line_with_denser_spline_curve(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line._set_line_style(smooth=True)
        artist = line._mes_maps["measure"]["line"]
        assert len(artist.get_xdata()) > len(DIMENSION)

    def test_smooth_true_keeps_markers_at_the_real_points(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line._set_line_style(smooth=True)
        marker_lines = [ln for ln in ax.get_lines() if ln.get_marker() == "o"]
        assert len(marker_lines) == 1
        assert list(marker_lines[0].get_ydata()) == list(MEASURE_A)


class TestSetLegend:
    def test_default_style_draws_standard_legend(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.set_legend()
        assert ax.get_legend() is not None
        assert ax.get_legend()._loc == 2  # "upper left"

    def test_unknown_style_raises(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        with pytest.raises(ValueError):
            line.set_legend(style="bogus")

    def test_line_pos_end_removes_standard_legend_and_labels_every_series(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.set_legend(line_pos="end")
        assert ax.get_legend() is None
        assert line._mes_maps["a"]["legend_annotation"] is not None
        assert line._mes_maps["b"]["legend_annotation"] is not None
        assert {a.get_text() for a in [line._mes_maps["a"]["legend_annotation"],
                                        line._mes_maps["b"]["legend_annotation"]]} == {"a", "b"}

    def test_line_pos_end_anchors_at_last_point_padded_right(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.set_legend(line_pos="end")
        ann = line._mes_maps["measure"]["legend_annotation"]
        assert ann.xy == (2, MEASURE_A[-1])
        assert ann.xyann == (8, 0)

    def test_line_pos_begin_anchors_at_first_point_padded_up(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A)])
        line.set_legend(line_pos="begin")
        ann = line._mes_maps["measure"]["legend_annotation"]
        assert ann.xy == (0, MEASURE_A[0])
        assert ann.xyann == (0, 8)

    def test_single_series_still_labeled_on_line(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "solo")])
        line.set_legend(line_pos="end")
        assert line._mes_maps["solo"]["legend_annotation"].get_text() == "solo"

    def test_label_color_matches_line_color(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.set_legend(line_pos="end")
        for name, entry in line._mes_maps.items():
            assert mcolors.to_rgba(entry["legend_annotation"].get_color()) == mcolors.to_rgba(
                entry["line"].get_color()
            )


class TestAdjustLegendLabelPos:
    def test_shifts_matched_series_additively(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a"), _mes(MEASURE_B, "b")])
        line.set_legend(line_pos="end")
        line.adjust_legend_label_pos([LegendLabelAdjustPos(of_measure="a", pad_h=3, pad_v=-2)])
        assert line._mes_maps["a"]["legend_annotation"].xyann == (11, -2)
        assert line._mes_maps["b"]["legend_annotation"].xyann == (8, 0)

    def test_unmatched_of_measure_raises(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a")])
        line.set_legend(line_pos="end")
        with pytest.raises(ValueError):
            line.adjust_legend_label_pos([LegendLabelAdjustPos(of_measure="nope")])

    def test_empty_list_is_noop(self, fig_ax):
        fig, ax = fig_ax
        line = Line(fig, ax).plot(_dim(), [_mes(MEASURE_A, "a")])
        line.set_legend(line_pos="end")
        assert line.adjust_legend_label_pos([]) is line
