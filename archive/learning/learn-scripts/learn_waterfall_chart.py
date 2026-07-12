from pandas.core.arrays.interval import le

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import numpy as np
import pandas as pd
from icecream import ic
# SETTINGS

DPI = 1000
FIGSIZE = (12, 6)

# Hardcoded data
df = pd.DataFrame({
    "category": ["2023 GS expect", "covid base", "property", "export", "govern", "2024 GS expect"],
    "value": [5.3, -2, 0.3, 0.4, 0.5, 4.5],
})
categories = df["category"].tolist()
values = df["value"].tolist()

# --- Concept 1: Figure and Axes ---
# fig = the whole canvas. ax = one plot area inside it.
# We'll draw everything onto `ax` from here on.
fig, ax = plt.subplots(figsize=FIGSIZE)


# Compute waterfall bottoms
invisible_bottoms = []
bar_heights = []
running_total = 0.0

for i, val in enumerate(values):
    if i == 0 or i == len(values) - 1:
        invisible_bottoms.append(0)
        bar_heights.append(abs(val))
    else:
        if val >= 0:
            invisible_bottoms.append(running_total)
            bar_heights.append(val)
        else:
            invisible_bottoms.append(running_total + val)
            bar_heights.append(abs(val))
    if i < len(values) - 1 and i != len(values) - 1:
        if i == 0:
            running_total = val
        elif i != len(values) - 1:
            running_total += val

ic(invisible_bottoms, bar_heights)

# Invisible base (creates floating effect)
ax.bar(categories, invisible_bottoms, color="none", edgecolor="none")

# Actual bars
ax.bar(categories, bar_heights, bottom=invisible_bottoms
    , edgecolor="white", linewidth=0.5)

# customize plot
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.minorticks_on()

ax.yaxis.set_major_locator(MultipleLocator(0.5))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))

# labels
tops = [i+b+0.06 for i, b in zip(invisible_bottoms, bar_heights)]

for i, top, val in zip(categories, tops, bar_heights):
    ax.text(i, top, f"{val:.2f}", ha="center", va="bottom")

plt.savefig("../output/tmp/waterfall_chart/main.png", dpi=DPI)
print("Saved main.png")
