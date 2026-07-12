"""Economist-style categorical heatmap grid.
Recreates: "Temperatures of 50°C will become more common around the
Mediterranean"
"""
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Verdana"

# ── Colors (4-step categorical scale) ────────────────────────────────────────
COLORS = {
    1: "#CFCBBF",  # Almost never
    2: "#DDD3C9",  # Extremely rare
    3: "#F0AFA4",  # Rare
    4: "#D6291C",  # Common
}
LABELS = ["Almost never", "Extremely rare*", "Rare†", "Common‡"]
BG_COLOR = "#F2EFE9"

# ── Data ──────────────────────────────────────────────────────────────────────
countries = ["Saudi Arabia", "Qatar", "Libya", "Tunisia",
             "Algeria", "Egypt", "Morocco", "Spain"]
columns = ["Without\nclimate\nchange", "Present\nday", "Mid-\ncentury", "Late\ncentury"]

# category codes: 1=Almost never, 2=Extremely rare, 3=Rare, 4=Common
grid = np.array([
    [3, 4, 4, 4],  # Saudi Arabia
    [1, 3, 4, 4],  # Qatar
    [1, 3, 4, 4],  # Libya
    [1, 2, 3, 4],  # Tunisia
    [1, 2, 3, 4],  # Algeria
    [1, 2, 3, 4],  # Egypt
    [1, 2, 3, 4],  # Morocco
    [1, 1, 1, 3],  # Spain
])

n_rows, n_cols = grid.shape

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.5, 8.5))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

cell_w, cell_h = 1.0, 1.0
gap = 0.22

for r in range(n_rows):
    y = n_rows - r  # top-to-bottom
    for c in range(n_cols):
        x = c * (cell_w + gap)
        color = COLORS[grid[r, c]]
        ax.add_patch(plt.Rectangle((x, y - cell_h / 2), cell_w, cell_h,
                                    facecolor=color, edgecolor="none"))

# ── Row labels (country names) ───────────────────────────────────────────────
for r, country in enumerate(countries):
    y = n_rows - r
    ax.text(-0.15, y, country, ha="right", va="center", fontsize=12, color="#222222")

# ── Column headers ────────────────────────────────────────────────────────────
for c, label in enumerate(columns):
    x = c * (cell_w + gap) + cell_w / 2
    ax.text(x, n_rows + 0.95, label, ha="center", va="bottom", fontsize=10.5, color="#222222")

# ── Axis cleanup ──────────────────────────────────────────────────────────────
ax.set_xlim(-2.3, n_cols * (cell_w + gap))
ax.set_ylim(0, n_rows + 0.95)
ax.axis("off")

# ── Source note ───────────────────────────────────────────────────────────────
ax.text(-2.3, -0.65,
        "*Once every 100 to 1,000 years   †Once every ten to 100 years\n"
        "‡At least once a decade\nSource: N. Christidis, D. Mitchell and P. A. Stott, May 2023",
        fontsize=8, color="#777777", va="top")

plt.subplots_adjust(top=0.58, bottom=0.06, left=0.28, right=0.95)

# ── Header block: red rule, titles, subtitle, legend (figure coords) ────────
fig.lines.append(plt.Line2D([0.045, 0.11], [0.965, 0.965], color="#E3120B",
                             linewidth=4, solid_capstyle="butt", transform=fig.transFigure))

fig.text(0.045, 0.935, "Temperatures of 50°C will become more", fontsize=15.5,
          fontweight="bold", color="#111111", ha="left", va="top")
fig.text(0.045, 0.895, "common around the Mediterranean", fontsize=15.5,
          fontweight="bold", color="#111111", ha="left", va="top")

fig.text(0.045, 0.835, "Estimated frequency of temperatures", fontsize=11,
          color="#333333", ha="left", va="top")
fig.text(0.045, 0.800, "exceeding 50°C on at least one day a year", fontsize=11,
          color="#333333", ha="left", va="top")

legend_y = 0.735
lx = 0.045
for i, label in enumerate(LABELS):
    fig.add_artist(plt.Rectangle((lx, legend_y - 0.012), 0.022, 0.022,
                                  transform=fig.transFigure, color=COLORS[i + 1]))
    fig.text(lx + 0.03, legend_y, label, fontsize=9.5, va="center", ha="left")
    lx += 0.03 + 0.012 * len(label) + 0.045

# ── "E" logo circle, bottom-right (as in reference) ─────────────────────────
logo = plt.Circle((0.93, 0.045), 0.028, transform=fig.transFigure,
                   color="#CFCBBF", clip_on=False)
fig.add_artist(logo)
fig.text(0.93, 0.045, "E", fontsize=13, color="white", fontweight="bold",
          ha="center", va="center")

plt.savefig("output/mediterranean_heat_grid.png", dpi=200, facecolor=BG_COLOR, bbox_inches="tight")
print("Saved output/mediterranean_heat_grid.png")
