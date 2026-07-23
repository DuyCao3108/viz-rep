"""Client-count charts: # Client by DATE_REPORT_QUARTER."""

from __future__ import annotations

import matplotlib.pyplot as plt

from plot.base import register_plot
from src.dataset import Dataset
from src.vizzy import Vizzy


@register_plot("client")
def bar_by_quarter(ds: Dataset):
    fig, ax = plt.subplots(figsize=(12, 6))
    bar = Vizzy(fig, ax, ds).bar(dim="DATE_REPORT_QUARTER", measure="# Client")
    bar.set_theme()
    bar.format_measure(fmt="#,")
    bar.show_data_label()
    return fig


@register_plot("client")
def line_by_quarter(ds: Dataset):
    fig, ax = plt.subplots(figsize=(12, 6))
    line = Vizzy(fig, ax, ds).line(dim="DATE_REPORT_QUARTER", measure="# Client")
    line.set_theme()
    line.format_measure(fmt="#,")
    line.show_data_label()
    return fig
