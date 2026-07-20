from typing import Literal

from icecream import ic

from src.dataset import Measure, Dimension
from src.vizzy import Vizzy
from tests.dataset_factory import dataset_from_df, _gen_data_2dim, _gen_data_3dim, _gen_orders



def _simple_bar_basic(fig, ax):
    df = _gen_data_3dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).bar(dim="quarter", measure="allocation")
    bar.show_data_label()


def _simple_bar_fmt_threshold(fig, ax):
    df = _gen_data_2dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("revenue", "sum(revenue)"))
    bar = Vizzy(fig, ax, ds).bar(dim="region", measure="revenue")
    bar.format_measure(fmt="#,K", dedup_fmt=False)
    bar.show_data_label(thresh_hold=100_000)


def _simple_bar_theme_defaults(fig, ax):
    df = _gen_data_2dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("revenue", "sum(revenue)"))
    bar = Vizzy(fig, ax, ds).bar(dim="region", measure="revenue")
    bar.set_theme()
    bar.format_measure(fmt="#,K", dedup_fmt=False)
    bar.show_data_label()


def _simple_bar_theme_science(fig, ax):
    df = _gen_data_3dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).bar(dim="quarter", measure="allocation")
    bar.set_theme(pal="gradient2-blue", tone="science")
    bar.show_data_label()


def _horizontal_bar_theme_defaults(fig, ax):
    df = _gen_data_2dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("revenue", "sum(revenue)"))
    bar = Vizzy(fig, ax, ds).barh(dim="region", measure="revenue")
    bar.set_theme()
    bar.format_measure(fmt="#,K", dedup_fmt=False)
    bar.show_data_label()


def _stack_bar_basic(fig, ax):
    df = _gen_data_3dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).stack_bar(
        dim="quarter", measure="allocation", legend="sector"
    )
    bar.show_data_label()


def _stack_bar_theme(fig, ax):
    df = _gen_data_3dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).stack_bar(
        dim="quarter", measure="allocation", legend="sector"
    )
    bar.set_theme()
    bar.format_measure(fmt="#,", dedup_fmt=False)
    bar.show_data_label()


def _h_stack_bar_basic(fig, ax):
    df = _gen_data_3dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).h_stack_bar(
        dim="quarter", measure="allocation", legend="sector"
    )
    bar.show_data_label()


def _h_stack_bar_theme(fig, ax):
    df = _gen_data_3dim(scale="M")
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).h_stack_bar(
        dim="quarter", measure="allocation", legend="sector"
    )
    bar.set_theme()
    bar.format_measure(fmt="#,M", dedup_fmt=False)
    bar.show_data_label()


def _h_stack_bar_threshold(fig, ax):
    df = _gen_data_3dim(scale="M")
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).h_stack_bar(
        dim="quarter", measure="allocation", legend="sector"
    )
    bar.set_theme()
    bar.format_measure(fmt="#,M", dedup_fmt=False)
    bar.show_data_label(thresh_hold=5_000_000)


def _simple_bar_dedup_label(fig, ax):
    df = _gen_data_2dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("revenue", "sum(revenue)"))
    bar = Vizzy(fig, ax, ds).bar(dim="region", measure="revenue")
    bar.set_theme()
    bar.format_measure(fmt="#,K", dedup_fmt=True)
    bar.show_data_label()


def _stack_bar_dedup_label(fig, ax):
    df = _gen_data_3dim(scale="M")
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).stack_bar(
        dim="quarter", measure="allocation", legend="sector"
    )
    bar.set_theme()
    bar.format_measure(fmt="#,M", dedup_fmt=True)
    bar.show_data_label()


def _stack_bar_sorted(fig, ax):
    df = _gen_data_3dim(scale="M")
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).stack_bar(
        dim="quarter", measure="allocation", legend="sector", sort_by={"dim": "asc"}
    )
    bar.set_theme()
    bar.format_measure(fmt="#,M", dedup_fmt=True)
    bar.show_data_label()

def _stack_bar_science_theme(fig, ax):
    df = _gen_data_3dim(scale="M")
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).stack_bar(
        dim="quarter", measure="allocation", legend="sector", sort_by={"dim": "asc"}
    )
    bar.set_theme(tone='science')
    bar.format_measure(fmt="#,M", dedup_fmt=True)
    bar.show_data_label()



def _stack_bar_theme_red(fig, ax):
    df = _gen_data_3dim(scale="M", ndim=4)
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).stack_bar(
        dim="quarter", measure="allocation", legend="sector", sort_by={"dim": "asc"}
    )
    bar.set_theme(pal="step5-red")
    bar.format_measure(fmt="#,M", dedup_fmt=True)
    bar.show_data_label(thresh_hold=2e6)

def _stack_bar_100_basic(fig, ax):
    df = _gen_data_3dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).stack_bar_100(
        dim="quarter", measure="allocation", legend="sector"
    )
    bar.set_theme()
    bar.format_measure(fmt="#.1")
    bar.show_data_label()


def _h_stack_bar_100_basic(fig, ax):
    df = _gen_data_3dim()
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).h_stack_bar_100(
        dim="quarter", measure="allocation", legend="sector"
    )
    bar.set_theme()
    bar.format_measure(fmt="#.1")
    bar.show_data_label()


def _stack_bar_100_pct_default(fig, ax):
    """Demonstrates thresh_hold_pct + the automatic percent formatter with
    zero extra config: StackBar100's default thresh_hold_pct (3.5%) hides
    sector segments under 3.5% of their quarter's total (e.g. Financials in
    2025-Q3/Q4, which sit around 2.6-2.9%), and every visible label is
    rendered straight from _before_plot()'s percent formatter (e.g.
    "24.3%") — no format_measure() call needed at all."""
    df = _gen_data_3dim(ndim=4)
    ds = dataset_from_df(df)
    ds.add_measure(Measure("allocation", "sum(allocation)"))
    bar = Vizzy(fig, ax, ds).stack_bar_100(
        dim="quarter", measure="allocation", legend="sector", sort_by={"dim": "asc"}
    )
    bar.set_theme()
    bar.show_data_label()


def _orders_stack_bar(fig, ax):
    df = _gen_orders(n=1000)
    ds = dataset_from_df(df)
    ds.set_cal_col(Dimension(name="month", transform="date_trunc('month', date)"))
    ds.set_cal_col(Dimension(name="quarter", transform="date_trunc('quarter', date)"))
    ds.set_measures([
        Measure("num_orders", "count(distinct order_id)"),
        Measure("num_apple_orders", "count(distinct case when fruit='apple' then order_id else null end)"),
        Measure("pct_apple", "{num_apple_orders}/{num_orders}"),
    ])
    # visual part
    bar = Vizzy(fig, ax, ds).stack_bar(
        dim="month", measure="num_orders", legend="fruit", sort_by={"dim": "asc"}, filters="status='delivered'"
    )
    bar.set_theme(pal="cate-55")
    bar.show_data_label()

def _orders_stack_bar_science_theme(fig, ax):
    df = _gen_orders(n=1000)
    ds = dataset_from_df(df)
    ds.set_cal_col(Dimension(name="month", transform="date_trunc('month', date)", fmt='yy-mm'))
    ds.set_cal_col(Dimension(name="quarter", transform="date_trunc('quarter', date)", fmt='yy-qq'))
    ds.set_measures([
        Measure("num_orders", "count(distinct order_id)"),
        Measure("num_apple_orders", "count(distinct case when fruit='apple' then order_id else null end)"),
        Measure("pct_apple", "{num_apple_orders}/{num_orders}"),
    ])
    # visual part
    bar = Vizzy(fig, ax, ds).stack_bar(
        dim="month", measure="num_orders", legend="fruit", sort_by={"dim": "asc"}, filters="status='delivered'"
    )
    bar.set_theme(pal="cate-55", tone='science')
    bar.show_data_label()



SCENARIOS = [
    ("bar/vertical/simple_bar_theme_defaults", _simple_bar_theme_defaults),
    ("bar/horizontal/h_simple_bar_theme_defaults", _horizontal_bar_theme_defaults),
    ("bar/vertical/stack_bar_theme", _stack_bar_theme),
    ("bar/horizontal/_h_stack_bar_threshold", _h_stack_bar_threshold),
    ("bar/vertical/stack_bar_dedup_label", _stack_bar_dedup_label),
    ("bar/vertical/stack_bar_sorted", _stack_bar_sorted),
    ("bar/vertical/stack_bar_theme_red", _stack_bar_theme_red),
    ("bar/vertical/stack_bar_science_theme", _stack_bar_science_theme),
    ("bar/vertical/orders_stack_bar", _orders_stack_bar),
    ("bar/vertical/orders_stack_bar_science_theme", _orders_stack_bar_science_theme),
    ("bar/vertical/stack_bar_100_basic", _stack_bar_100_basic),
    ("bar/horizontal/h_stack_bar_100_basic", _h_stack_bar_100_basic),
    ("bar/vertical/stack_bar_100_pct_default", _stack_bar_100_pct_default),
]
