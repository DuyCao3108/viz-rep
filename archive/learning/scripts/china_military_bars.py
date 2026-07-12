"""Economist-style opposing (back-to-back) horizontal bar chart.
Recreates: "China's military tech still lags the West"
"""
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Verdana"

# ── Colors ────────────────────────────────────────────────────────────────────
CHINA_COLOR = "#DD4A31"   # red-orange
US_COLOR    = "#B8B2A7"   # warm grey
BG_COLOR    = "#F2EFE9"   # off-white paper background

# ── Data ──────────────────────────────────────────────────────────────────────
categories = [
    "Total battle force",
    "Principal surface combatants",
    "Aircraft-carriers",
    "Combat aircraft",
    "Helicopters",
]
china = [370, 92, 2, 456, 116]
us    = [291, 122, 11, 988, 689]

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 6.5))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

n = len(categories)
y = np.arange(n)[::-1]  # top-to-bottom order
bar_h = 0.55

# Normalize each row's bars against a shared per-row max so both bars fill
# the plot width proportionally (values on each side are independent scales,
# mirroring the reference chart's per-row bar sizing).
totals = [c+u for c, u in zip(china, us)]

china_frac = [c / t for c, t in zip(china, totals)]
us_frac    = [u / t for u, t in zip(us, totals)]

for yi, cf, uf, cval, uval in zip(y, china_frac, us_frac, china, us):
    # China bar grows leftward from center (x=0)
    ax.barh(yi, -cf, height=bar_h, left=0, color=CHINA_COLOR, zorder=3)
    # US bar grows rightward from center (x=0)
    ax.barh(yi, uf, height=bar_h, left=0, color=US_COLOR, zorder=3)

    # Value labels
    ax.text(-cf + 0.02, yi, str(cval), ha="left", va="center",
             fontsize=10, color="white", fontweight="bold", zorder=4)
    ax.text(uf - 0.02, yi, str(uval), ha="right", va="center",
             fontsize=10, color="#333333", fontweight="bold", zorder=4)

# ── Category labels above each row pair ─────────────────────────────────────
for yi, cat in zip(y, categories):
    ax.text(-1.02, yi + bar_h / 2 + 0.18, cat, ha="left", va="bottom",
             fontsize=10.5, color="#222222", fontweight="bold")

# ── Legend, inline on the first category row (as in reference) ─────────────
first_y = y[0] + bar_h / 2 + 0.18
ax.add_patch(plt.Rectangle((0.30, first_y - 0.01), 0.045, 0.16,
                            clip_on=False, color=CHINA_COLOR))
ax.text(0.36, first_y + 0.07, "China", ha="left", va="bottom",
        fontsize=10, color="#555555")
ax.add_patch(plt.Rectangle((0.62, first_y - 0.01), 0.045, 0.16,
                            clip_on=False, color=US_COLOR))
ax.text(0.68, first_y + 0.07, "United States", ha="left", va="bottom",
        fontsize=10, color="#555555")

# ── Axis limits / cleanup ────────────────────────────────────────────────────
ax.set_xlim(-1.05, 1.05)
ax.set_ylim(-0.6, n - 0.2)
ax.axis("off")

# ── Source note (bottom, in data coords) ─────────────────────────────────────
ax.text(-1.02, -0.55, "Sources: IISS; US Department of Defence",
        fontsize=8, color="#777777", va="top")

plt.subplots_adjust(top=0.68, bottom=0.05, left=0.03, right=0.97)

# ── Header block: red rule, titles, subtitle, legend (figure coords) ────────
fig.lines.append(plt.Line2D([0.045, 0.11], [0.965, 0.965], color=CHINA_COLOR,
                             linewidth=4, solid_capstyle="butt", transform=fig.transFigure))

fig.text(0.045, 0.94, "China's military tech", fontsize=17, fontweight="bold",
          color="#111111", ha="left", va="top")
fig.text(0.045, 0.885, "still lags the West", fontsize=17, fontweight="bold",
          color="#111111", ha="left", va="top")

fig.text(0.045, 0.815, "Navy balance, December 2022 or latest available",
          fontsize=10.5, color="#333333", ha="left", va="top")

# ── "E" logo circle, bottom-right (as in reference) ─────────────────────────
logo = plt.Circle((0.965, 0.045), 0.022, transform=fig.transFigure,
                   color="#CFCBBF", clip_on=False)
fig.add_artist(logo)
fig.text(0.965, 0.045, "E", fontsize=11, color="white", fontweight="bold",
          ha="center", va="center")

plt.show()
