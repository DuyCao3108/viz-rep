"""Economist-style dumbbell (lollipop) chart.
Recreates: "Retirement has become much longer across the rich world"
"""
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Verdana"

# ── Colors ────────────────────────────────────────────────────────────────────
COLOR_1970 = "#B8B2A7"   # warm grey
COLOR_2020 = "#E3120B"   # red
BG_COLOR   = "#F2EFE9"   # off-white paper background
LINE_COLOR = "#8C8C8C"

# ── Data ──────────────────────────────────────────────────────────────────────
countries = ["France", "Britain", "Netherlands", "Denmark",
             "United States", "Japan", "Mexico"]
y1970 = [12.5, 11.5, 13.5, 12.5, 12.5, 10.0, 8.5]
y2020 = [23.5, 19.5, 11.0, 17.5, 16.5, 15.0, 13.5]

# Order top-to-bottom as in reference
y = list(range(len(countries)))[::-1]

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 7))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# Gridlines
for xv in range(5, 31, 5):
    ax.axvline(xv, color="white", linewidth=1.4, zorder=1)

# Dumbbell lines + points
for yi, v70, v20 in zip(y, y1970, y2020):
    ax.plot([v70, v20], [yi, yi], color=LINE_COLOR, linewidth=2, zorder=2)
    ax.scatter(v70, yi, s=180, color=COLOR_1970, zorder=3, edgecolor=BG_COLOR, linewidth=1)
    ax.scatter(v20, yi, s=180, color=COLOR_2020, zorder=3, edgecolor=BG_COLOR, linewidth=1)

# ── Labels for 1970 / 2020 next to the Britain row (as in reference) ─────────
britain_idx = countries.index("Britain")
yi = y[britain_idx]
ax.text(y1970[britain_idx] - 1.5, yi, "1970", ha="right", va="center",
        fontsize=13, color=COLOR_1970, fontweight="bold")
ax.text(y2020[britain_idx] + 1.5, yi, "2020", ha="left", va="center",
        fontsize=13, color=COLOR_2020, fontweight="bold")

# ── Y-axis: country names ─────────────────────────────────────────────────────
ax.set_yticks(y)
ax.set_yticklabels(countries, fontsize=13, color="#222222")
ax.tick_params(axis="y", length=0)

# ── X-axis ────────────────────────────────────────────────────────────────────
ax.set_xlim(3, 32)
ax.set_xticks(range(5, 31, 5))
ax.set_xticklabels(range(5, 31, 5), fontsize=11, color="#555555")
ax.xaxis.tick_top()
ax.tick_params(axis="x", length=0, pad=6)

# Small squiggle marking the truncated (non-zero) axis start, left of "5"
ax.plot([0.005, 0.018, 0.032, 0.045], [1.025, 1.065, 1.005, 1.055],
        color="#555555", linewidth=1.3, solid_capstyle="round",
        clip_on=False, transform=ax.transAxes)

ax.set_ylim(-0.7, len(countries) + 0.3)

# ── Spines ────────────────────────────────────────────────────────────────────
for side in ["top", "right", "left", "bottom"]:
    ax.spines[side].set_visible(False)

# ── Red accent rule + titles ──────────────────────────────────────────────────
ax.plot([0.0, 0.09], [1.11, 1.11], transform=fig.transFigure,
        color="#E3120B", linewidth=4, solid_capstyle="butt", clip_on=False)

fig.text(0.075, 0.97, "Retirement has become much\nlonger across the rich world",
          fontsize=19, fontweight="bold", color="#111111", va="top")
fig.text(0.075, 0.855, "Men's life expectancy at average age of retirement",
          fontsize=13, fontweight="bold", color="#222222", va="top")
fig.text(0.18, 0.795, "Years", fontsize=11, color="#555555", va="top", ha="left")

plt.subplots_adjust(top=0.72, bottom=0.05, left=0.18, right=0.95)
plt.savefig("output/retirement_dumbbell.png", dpi=200, facecolor=BG_COLOR, bbox_inches="tight")
print("Saved output/retirement_dumbbell.png")
