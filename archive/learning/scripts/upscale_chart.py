"""
Re-renders chart_output.png at higher resolution without touching the original.
Output: chart_output_hires.png
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import openpyxl

OUTPUT_FILE = "chart_output_hires.png"
DPI = 450        # 3x the original 150 dpi
FIGSIZE = (14, 8) # wider/taller canvas so labels have breathing room

# ── Data ──────────────────────────────────────────────────────────────────────
wb = openpyxl.load_workbook("../data/learning-excel.xlsx")
ws = wb.active
categories, values = [], []
for row in ws.iter_rows(values_only=True):
    if row[1] is not None and row[2] is not None:
        categories.append(row[1])
        values.append(float(row[2]))

# ── Colors ────────────────────────────────────────────────────────────────────
COLORS = {
    "first":    "#1A6B8A",
    "negative": "#F2AAAA",
    "positive": "#BEBEBE",
    "last":     "#C0392B",
}

def get_color(i, val):
    if i == 0:                    return COLORS["first"]
    if i == len(categories) - 1: return COLORS["last"]
    return COLORS["negative"] if val < 0 else COLORS["positive"]

# ── Waterfall geometry ────────────────────────────────────────────────────────
invisible_bottoms, bar_heights, tops = [], [], []
running = 0.0
for i, val in enumerate(values):
    if i == 0:
        invisible_bottoms.append(0); bar_heights.append(val); tops.append(val)
        running = val
    elif i == len(values) - 1:
        invisible_bottoms.append(0); bar_heights.append(val); tops.append(val)
    else:
        if val >= 0:
            invisible_bottoms.append(running)
            bar_heights.append(val)
            tops.append(running + val)
        else:
            invisible_bottoms.append(running + val)
            bar_heights.append(abs(val))
            tops.append(running + val)
        running += val

def fmt_label(i, val):
    if i == 0 or i == len(values) - 1:
        return f"{val:g}".replace(".", ",")
    sign = "+" if val > 0 else ""
    return f"{sign}{val:g}pp".replace(".", ",")

labels = [fmt_label(i, v) for i, v in enumerate(values)]

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=FIGSIZE)
x = np.arange(len(categories))

ax.bar(x, invisible_bottoms, color="none", edgecolor="none")
ax.bar(x, bar_heights, bottom=invisible_bottoms,
       color=[get_color(i, v) for i, v in enumerate(values)],
       edgecolor="white", linewidth=0.5)

for i, (label, val, top) in enumerate(zip(labels, values, tops)):
    if i == 0 or i == len(values) - 1:
        ax.text(i, top + 0.06, label, ha="center", va="bottom", fontsize=11)
    elif val < 0:
        ax.text(i, invisible_bottoms[i] - 0.06, label, ha="center", va="top", fontsize=10)
    else:
        ax.text(i, top + 0.06, label, ha="center", va="bottom", fontsize=10)

ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=10)
ax.set_yticks(range(0, 7))
ax.set_ylim(0, 6.5)
ax.set_title("this is chart title", fontsize=15, loc="left", pad=14)
ax.set_xlabel("Covid expectation", fontsize=10, labelpad=10)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", which="both", length=0)

plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=DPI, bbox_inches="tight")
print(f"Saved {OUTPUT_FILE}")

import os
orig = os.path.getsize("chart_output.png")
new  = os.path.getsize(OUTPUT_FILE)
print(f"chart_output.png  : {orig/1024:.0f} KB")
print(f"{OUTPUT_FILE}: {new/1024:.0f} KB  ({new/orig:.1f}x)")
