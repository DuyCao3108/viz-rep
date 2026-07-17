
def _generate_mock_data(seed: int = 0):
    """1 main dimension (quarter), 1 legend dimension (sector, 7 values), 1 measure (allocation %)."""
    import polars as pl
    import numpy as np

    rng = np.random.default_rng(seed)

    periods = [f"Q{q} {y}" for y in (2024, 2025) for q in (1, 2, 3, 4)]  # main dimension, 8 values
    sectors = [
        "Technology", "Healthcare", "Financials", "Energy",
        "Consumer", "Industrials",
        "Utilities",
        # 'Education', 'Hospitality'
    ]  # legend dimension, 7 values

    base = rng.uniform(5, 20, size=len(sectors))
    walk = rng.normal(0, 1.2, size=(len(periods), len(sectors))).cumsum(axis=0)
    values = np.clip(base + walk, 1, None)  # rows=periods, cols=sectors

    df = pl.DataFrame(
        {
            "quarter": [p for p in periods for _ in sectors],
            "sector": [s for _ in periods for s in sectors],
            "allocation": values.flatten(),
        }
    )
    return df

def _simple_bar_basic(fig, ax):
    from src.dataset import Dataset, Dimension, Measure
    from src.vizzy import Vizzy

    df = _generate_mock_data()
    ds = Dataset(df,
            dimensions=[Dimension("quarter", "quarter")],
            measures=[Measure("allocation", "allocation")])
    bar = Vizzy(fig, ax, ds).bar(dim="quarter", measure="allocation")
    bar.show_data_label()

def _generate_mock_revenue_data():
    """Fixed (non-random) revenue-scale values chosen to visibly exercise
    both K-scaling/thousand-sep and threshold-hiding: 2 of 5 fall below the
    100K threshold, one scaled value (1,400K) is large enough to show comma
    grouping."""
    import polars as pl

    regions = ["North America", "Europe", "APAC", "LATAM", "MEA"]
    revenue = [45_000, 220_000, 1_400_000, 80_000, 960_000]
    return pl.DataFrame({"region": regions, "revenue": revenue})

def _simple_bar_fmt_threshold(fig, ax):
    from src.dataset import Dataset, Dimension, Measure
    from src.vizzy import Vizzy

    df = _generate_mock_revenue_data()
    ds = Dataset(df,
            dimensions=[Dimension("region", "region")],
            measures=[Measure("revenue", "revenue")])
    bar = Vizzy(fig, ax, ds).bar(dim="region", measure="revenue")
    bar.show_data_label(fmt="whole-k-thsep", thresh_hold=100_000)

def _simple_bar_theme_defaults(fig, ax):
    from src.dataset import Dataset, Dimension, Measure
    from src.vizzy import Vizzy

    df = _generate_mock_revenue_data()
    ds = Dataset(df,
            dimensions=[Dimension("region", "region")],
            measures=[Measure("revenue", "revenue")])
    bar = Vizzy(fig, ax, ds).bar(dim="region", measure="revenue")
    bar.set_theme()
    bar.show_data_label(fmt="whole-k-thsep")

def _simple_bar_theme_science(fig, ax):
    from src.dataset import Dataset, Dimension, Measure
    from src.vizzy import Vizzy

    df = _generate_mock_data()
    ds = Dataset(df,
            dimensions=[Dimension("quarter", "quarter")],
            measures=[Measure("allocation", "allocation")])
    bar = Vizzy(fig, ax, ds).bar(dim="quarter", measure="allocation")
    bar.set_theme(pal="gradient2-blue", tone="science")
    bar.show_data_label()

SCENARIOS = [
    ("bar/vertical/simple_bar_basic", _simple_bar_basic),
    ("bar/vertical/simple_bar_fmt_threshold", _simple_bar_fmt_threshold),
    ("bar/vertical/simple_bar_theme_defaults", _simple_bar_theme_defaults),
    ("bar/vertical/simple_bar_theme_science", _simple_bar_theme_science),
]
