"""Pure-function formatting tokens: render_value/_format_dimension. Only the
newly-added tokens are covered here — the rest of DataLabelFormat/
DimensionFormat is exercised indirectly through tests/test_charts_bar.py and
tests/test_charts_line.py."""

import datetime

import pytest

from src.custom.formatting import _format_dimension, render_value


class TestPercentZeroPrecision:
    def test_renders_zero_decimal_percent(self):
        assert render_value(0.5, "%.0") == "50%"

    def test_rounds_like_other_percent_precisions(self):
        assert render_value(0.256, "%.0") == "26%"


class TestYyyyQq:
    def test_renders_four_digit_year_quarter(self):
        assert _format_dimension(datetime.date(2026, 5, 1), "yyyy-qq") == "2026-Q2"

    def test_matches_yy_qq_quarter_number(self):
        value = datetime.date(2026, 11, 1)
        assert _format_dimension(value, "yy-qq") == "26-Q4"
        assert _format_dimension(value, "yyyy-qq") == "2026-Q4"

    def test_non_date_value_raises_type_error(self):
        with pytest.raises(TypeError):
            _format_dimension("not-a-date", "yyyy-qq")
