import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import openpyxl

# Read data from Excel
wb = openpyxl.load_workbook("../data/learning-excel.xlsx")
ws = wb.active
categories = []
values = []
for row in ws.iter_rows(values_only=True):
    if row[1] is not None and row[2] is not None:
        categories.append(row[1])
        values.append(float(row[2]))

# Colors matching the Excel chart
COLORS = {
    "first": "#1A6B8A",   # teal for 2023 GS expect
    "negative": "#F2AAAA", # pink for covid base (negative)
    "positive": "#BEBEBE", # gray for small positive bars
    "last": "#C0392B",    # dark red for 2024 GS expect
}

def get_color(i, val):
    if i == 0:
        return COLORS["first"]
    if i == len(categories) - 1:
        return COLORS["last"]
    return COLORS["negative"] if val < 0 else COLORS["positive"]

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

# Recompute running totals cleanly
running = 0.0
invisible_bottoms = []
bar_heights = []
tops = []  # top of each bar (for label positioning)

for i, val in enumerate(values):
    if i == 0:
        invisible_bottoms.append(0)
        bar_heights.append(val)
        tops.append(val)
        running = val
    elif i == len(values) - 1:
        invisible_bottoms.append(0)
        bar_heights.append(val)
        tops.append(val)
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

# Build label strings
def fmt_label(i, val):
    if i == 0 or i == len(values) - 1:
        return f"{val:g}".replace(".", ",")
    sign = "+" if val > 0 else ""
    return f"{sign}{val:g}pp".replace(".", ",")

labels = [fmt_label(i, v) for i, v in enumerate(values)]

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(categories))

bar_colors = [get_color(i, v) for i, v in enumerate(values)]

# Invisible base (creates floating effect)
ax.bar(x, invisible_bottoms, color="none", edgecolor="none")

# Actual bars
ax.bar(x, bar_heights, bottom=invisible_bottoms,
       color=bar_colors, edgecolor="white", linewidth=0.5)

# Labels
running = 0.0
for i, (label, val, top) in enumerate(zip(labels, values, tops)):
    if i == 0 or i == len(values) - 1:
        # Value inside/above full bar
        ax.text(i, top + 0.06, label, ha="center", va="bottom", fontsize=10)
    elif val < 0:
        # Negative: label below the floating bar
        ax.text(i, invisible_bottoms[i] - 0.06, label, ha="center", va="top", fontsize=9)
    else:
        # Positive increment: label above the floating bar
        ax.text(i, top + 0.06, label, ha="center", va="bottom", fontsize=9)

# Formatting
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=9)
ax.set_yticks(range(0, 7))
ax.set_ylim(0, 6.5)
ax.set_title("this is chart title", fontsize=13, loc="left", pad=12)
ax.set_xlabel("Covid expectation", fontsize=9, labelpad=8)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", which="both", length=0)

plt.tight_layout()
plt.savefig("chart_output.png", dpi=150, bbox_inches="tight")
print("Saved chart_output.png")
plt.show()
