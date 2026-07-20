"""Dataset.query(): unfiltered, filtered, legend pivot, unknown dim/measure ->
ValueError, agg variants, sort_by ordering, calculated columns, cross-measure
formulas."""

import pytest

from src.dataset import Dimension, Measure


def test_default_sort_is_dim_ascending(sample_dataset):
    result = sample_dataset.query(dim="quarter", measure="allocation")
    assert result.categories.value == ["Q1 2024", "Q2 2024"]


def test_sort_by_dim_desc(sample_dataset):
    result = sample_dataset.query(dim="quarter", measure="allocation", sort_by={"dim": "desc"})
    assert result.categories.value == ["Q2 2024", "Q1 2024"]


def test_sort_by_mes_desc_no_legend(sample_dataset):
    result = sample_dataset.query(dim="sector", measure="allocation", sort_by={"mes": "desc"})
    # sector means across both quarters: Technology (12,14)->13, Healthcare (8,9)->8.5
    assert result.categories.value == ["Technology", "Healthcare"]
    assert list(result.values.value) == sorted(result.values.value, reverse=True)


def test_sort_by_mes_desc_with_legend_sums_across_segments(sample_dataset):
    result = sample_dataset.query(
        dim="quarter", measure="allocation", legend="sector", sort_by={"mes": "desc"}
    )
    # per-quarter totals summed across sector segments: Q1=12+8=20, Q2=14+9=23
    assert result.categories.value == ["Q2 2024", "Q1 2024"]


def test_sort_by_mes_then_dim_multi_key(sample_dataset):
    result = sample_dataset.query(
        dim="quarter", measure="allocation", sort_by={"mes": "desc", "dim": "asc"}
    )
    assert result.categories.value == ["Q2 2024", "Q1 2024"]


def test_sort_by_legend_desc_is_independent_of_category_order(sample_dataset):
    result = sample_dataset.query(
        dim="quarter", measure="allocation", legend="sector",
        sort_by={"dim": "asc", "legend": "desc"},
    )
    assert result.categories.value == ["Q1 2024", "Q2 2024"]
    assert result.legend_categories.value == ["Technology", "Healthcare"]


def test_unknown_dim_raises(sample_dataset):
    with pytest.raises(ValueError):
        sample_dataset.query(dim="not_a_dim", measure="allocation")


def test_auto_discovered_dimension_is_queryable(orders_dataset):
    # "fruit" was never explicitly declared — every parquet column is a
    # dimension by default.
    result = orders_dataset.query(
        dim="fruit", measure="num_orders", filters="status != 'cancelled'"
    )
    assert result.categories.value == ["apple", "banana"]
    assert list(result.values.value) == [3.0, 2.0]


def test_calculated_column_is_queryable_as_dim(orders_dataset):
    result = orders_dataset.query(dim="month", measure="num_orders")
    assert [d.month for d in result.categories.value] == [1, 2, 3]
    assert list(result.values.value) == [2.0, 3.0, 1.0]


def test_raw_sql_filter_narrows_results(orders_dataset):
    result = orders_dataset.query(
        dim="month", measure="num_orders", filters="status != 'cancelled'"
    )
    assert list(result.values.value) == [2.0, 2.0, 1.0]


def test_cross_measure_formula_resolves(orders_dataset):
    result = orders_dataset.query(
        dim="month", measure="pct_apple", filters="status != 'cancelled'"
    )
    assert list(result.values.value) == [0.5, 0.5, 1.0]


def test_circular_measure_reference_raises(orders_dataset):
    orders_dataset.add_measure(Measure("a", "{b}"))
    orders_dataset.add_measure(Measure("b", "{a}"))
    with pytest.raises(ValueError):
        orders_dataset.query(dim="month", measure="a")


def test_set_cal_col_requires_transform(orders_dataset):
    with pytest.raises(ValueError):
        orders_dataset.set_cal_col(Dimension(name="no_transform"))
