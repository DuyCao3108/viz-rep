import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np

# Data
years  = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
shares = [   8,    4,    3,    5,    7,   15,   14,   11,   14,   31,   29,   23,   57]

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# --- Shaded annotation regions ---
regions = [
    (2012, 2016,  "Leveraged\nlending\nguidelines\n(2013)"),
    (2017, 2020.5,"Recession\nfears/trade\nwars"),
    (2021, 2022.8,"COVID –\npresent"),
]
for x0, x1, label in regions:
    ax.axvspan(x0, x1, color="#e8e8e8", alpha=0.7, zorder=1)
    ax.text((x0 + x1) / 2, 74, label,
            fontsize=8.5, color="#222222", ha="center", va="top",
            linespacing=1.4)

# --- Line + markers (open circles) ---
ax.plot(years, shares, color="#1a4f8a", linewidth=1.6, zorder=3,
        marker="o", markersize=6, markerfacecolor="white", markeredgecolor="#1a4f8a",
        markeredgewidth=1.5)

# Highlight last point filled dark red
ax.plot(2022, 57, "o", markersize=8, color="#8b1a1a", zorder=4,
        markerfacecolor="#8b1a1a", markeredgecolor="#8b1a1a")

# --- Data labels ---
offsets = {
    2010: ( 0,  8), 2011: ( 0, 8), 2012: ( 0, 8),  2013: ( 0, 8),
    2014: ( 0,  8), 2015: ( 0, 8), 2016: ( 0, 8),  2017: ( 0, 8),
    2018: ( 0,  8), 2019: ( 0, 8), 2020: (-18, 4), 2021: (-18, 4),
    2022: ( 6,  4),
}
for yr, val in zip(years, shares):
    dx, dy = offsets[yr]
    ax.annotate(f"{val}%", xy=(yr, val),
                xytext=(dx, dy), textcoords="offset points",
                fontsize=8, color="#333333", ha="center", va="bottom")


# --- Axes formatting ---
ax.set_xlim(2009.3, 2022.8)
ax.set_ylim(0, 82)

ax.set_xticks(range(2010, 2023, 2))
ax.set_xticklabels([str(y) for y in range(2010, 2023, 2)], fontsize=9)

ax.set_yticks(range(0, 90, 10))
ax.set_yticklabels([f"{y}%" for y in range(0, 90, 10)], fontsize=9)

# Light horizontal gridlines only
ax.yaxis.grid(True, color="#dddddd", linewidth=0.7, linestyle="-")
ax.set_axisbelow(True)
ax.xaxis.grid(False)

# Remove top/right spines; keep bottom/left thin
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["bottom", "left"]:
    ax.spines[spine].set_color("#aaaaaa")
    ax.spines[spine].set_linewidth(0.8)

ax.tick_params(axis="both", which="both", length=0)

# --- Title & source ---
ax.set_title(
    "Estimated direct lending market share, sponsor M&A financing",
    fontsize=11, fontweight="bold", color="#111111", loc="left", pad=12
)
fig.text(0.01, 0.01,
         "Source: Preqin, PitchBook LCD, Thomson Reuters Eikon, Goldman Sachs GBM",
         fontsize=7.5, color="#666666")

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig("gs_line_chart.png", dpi=450, bbox_inches="tight")
print("Saved gs_line_chart.png")
plt.show()
