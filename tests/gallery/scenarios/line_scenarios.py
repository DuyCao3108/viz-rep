"""Line-family gallery scenarios.

Each entry is (name, build_fn) where build_fn(fig, ax) -> None builds a
Dataset, constructs a Vizzy(fig, ax, dataset), and calls .line(...) (plus any
chained mutations) to draw one scenario."""

from src.dataset import Dimension, Measure
from src.vizzy import Vizzy
from tests.dataset_factory import _gen_orders, _gen_orders_smooth, dataset_from_df


def _orders_dataset():
    df = _gen_orders_smooth(scale='M')
    ds = dataset_from_df(df)
    ds.set_cal_col(
        Dimension(name="month", transform="date_trunc('month', date)", fmt="yy-mm")
    )
    ds.set_cal_col(
        Dimension(name="quarter", transform="date_trunc('quarter', date)", fmt="yy-qq")
    )
    ds.set_measures(
        [
            Measure("num_orders", "count(distinct order_id)"),
            Measure("amt_orders", "sum(price)"),
            Measure(
                "num_apple_orders",
                "count(distinct case when fruit='apple' then order_id else null end)",
            ),
            Measure(
                "num_banana_orders",
                "count(distinct case when fruit='banana' then order_id else null end)",
            ),
            Measure(
                "num_orange_orders",
                "count(distinct case when fruit='orange' then order_id else null end)",
            ),
            Measure(
                "num_pineapple_orders",
                "count(distinct case when fruit='pineapple' then order_id else null end)",
            ),
            Measure(
                "num_strawberry_orders",
                "count(distinct case when fruit='strawberry' then order_id else null end)",
            ),
            Measure("pct_apple", "{num_apple_orders}/{num_orders}", fmt="%.1"),
            Measure("pct_banana", "{num_banana_orders}/{num_orders}", fmt="%.1"),
            Measure("pct_orange", "{num_orange_orders}/{num_orders}", fmt="%.1"),
            Measure("pct_pineapple", "{num_pineapple_orders}/{num_orders}", fmt="%.1"),
            Measure(
                "pct_strawberry", "{num_strawberry_orders}/{num_orders}", fmt="%.1"
            ),
        ]
    )
    return ds


def _line_basic(fig, ax):
    ds = _orders_dataset()
    Vizzy(fig, ax, ds).line(dim="month", measure="amt_orders")


def _line_theme_defaults(fig, ax):
    ds = _orders_dataset()
    line = Vizzy(fig, ax, ds).line(dim="month", measure="amt_orders")
    line.set_theme()
    line.format_measure(fmt="#,K")
    line.show_data_label()


def _multi_measure_basic(fig, ax):
    ds = _orders_dataset()
    line = Vizzy(fig, ax, ds).line(
        dim="month", measure=["num_orders", "num_apple_orders"]
    )
    line.set_theme()
    line.show_data_label()


def _multi_measures_pct(fig, ax):
    ds = _orders_dataset()
    line = Vizzy(fig, ax, ds).line(
        dim="month",
        measure=[
            "pct_apple",
            "pct_banana",
            "pct_orange",
            "pct_pineapple",
            "pct_strawberry",
        ],
    )
    line.format_measure(fmt='%.1')
    line.set_theme()
    line.show_data_label()


def _legend_split_basic(fig, ax):
    ds = _orders_dataset()
    line = Vizzy(fig, ax, ds).line(dim="month", measure="num_orders", legend="status")
    line.set_theme()
    line.show_data_label()


def _format_measure_dedup(fig, ax):
    ds = _orders_dataset()
    line = Vizzy(fig, ax, ds).line(dim="month", measure="amt_orders")
    line.set_theme()
    line.format_measure(fmt="#,K", dedup_fmt=True)
    line.show_data_label()

def _smoothen_line(fig, ax):
    ds = _orders_dataset()
    line = Vizzy(fig, ax, ds).line(dim="month", measure="amt_orders")
    line.set_theme()
    line.format_measure(fmt="#,K", dedup_fmt=True)
    line.set_line_style(smooth=True)
    line.show_data_label()


def _format_measure_dedup_M(fig, ax):
    ds = _orders_dataset()
    line = Vizzy(fig, ax, ds).line(dim="month", measure="amt_orders")
    line.set_theme()
    line.format_measure(fmt="#,M", dedup_fmt=True)
    line.show_data_label()


SCENARIOS = [
    ("line/line_basic", _line_basic),
    ("line/line_theme_defaults", _line_theme_defaults),
    ("line/multi_measure_basic", _multi_measure_basic),
    ("line/multi_measures_pct", _multi_measures_pct),
    ("line/legend_split_basic", _legend_split_basic),
    ("line/format_measure_dedup", _format_measure_dedup),
    ("line/format_measure_dedup_M", _format_measure_dedup_M),
    ("line/smoothen_line", _smoothen_line),
]
