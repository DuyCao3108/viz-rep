from numpy.ma.extras import flatnotmasked_edges

import matplotlib.pyplot as plt
import numpy as np
from icecream import ic
# ── Data ──────────────────────────────────────────────────────────────────────
categories = [
    "Total battle force",
    "Principal surface combatants",
    "Aircraft-carriers",
    "Combat aircraft",
    "Helicopters",
]
china = np.array([370, 92, 2, 456, 116])
us    = np.array([291, 122, 11, 988, 689])


order = np.argsort(china + us)[::-1]          # ascending order of total
categories = np.array(categories)[order]
china = china[order]
us = us[order]
totals = china + us


china_pct = china / totals * 100
us_pct = us / totals * 100


# color
CHINA_COLOR = "#DD4A31"   # red-orange
US_COLOR    = "#B8B2A7"   # warm grey
BG_COLOR    = "#F2EFE9"   # off-white paper background

plt.rcParams['axes.prop_cycle'] = plt.cycler(color=[CHINA_COLOR, US_COLOR, BG_COLOR])

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6,6))

bars_china = ax.barh(categories, china_pct, label='China', height=0.5)
bars_us = ax.barh(categories, us_pct, left=china_pct, label='US', height=0.5)

ax.text(0,1,'text', ha='left', va='center')
ax.text(100-2,1,'val', ha='right', va='center')


# ── Labels and Title
ax.spines[['top', 'right', 'left','bottom']].set_visible(False)
ax.xaxis.set_visible(False)
ax.tick_params(axis='y', left=False)

ax.set_ylim(top=5.2)

ax.set_yticklabels([])

for bar in bars_china:
    x=bar.get_x()
    y=bar.get_y()
    width=bar.get_width()
    height=bar.get_height()

    ax.text(x,y+height+0.05,'cate', ha='left')


fig.savefig("../output/tmp/china_mili_bars/main.png", dpi=500, bbox_inches="tight")
print("Saved main.png")
