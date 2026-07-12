"""Recreates the think-cell marketing chart: cumulative working time,
PowerPoint+templates/macros (black, jagged) vs PowerPoint+think-cell (green,
smooth), split into "Creation" and "Alteration" phases, with a "70% working
time saved" bracket annotation.
"""
import matplotlib.pyplot as plt
import numpy as np

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK_COLOR = "#1a1a1a"
GREEN_COLOR = "#8CA83E"

# ── Data: synthetic cumulative curves matching the reference shapes ─────────
np.random.seed(7)
n = 120  # points across the whole test set (Creation + Alteration)
x = np.linspace(0, 10, n)

# Black line: rises to ~4h at midpoint (Creation), then ~10h by the end,
# with a jagged (noisy) monotonic increase.
black_target_mid = 4.0
black_target_end = 10.0
black = np.concatenate([
    np.linspace(0, black_target_mid, n // 2),
    np.linspace(black_target_mid, black_target_end, n - n // 2),
])
black += np.cumsum(np.random.uniform(-0.05, 0.09, n))
black = np.maximum.accumulate(black)
black[0] = 0
black *= black_target_end / black[-1]  # rescale so it lands exactly on target

# Green line: smoother, rises to ~1.7h at midpoint, ~3.1h by the end.
green_target_mid = 1.7
green_target_end = 3.1
green = np.concatenate([
    np.linspace(0, green_target_mid, n // 2),
    np.linspace(green_target_mid, green_target_end, n - n // 2),
])
green += np.cumsum(np.random.uniform(-0.01, 0.02, n))
green = np.maximum.accumulate(green)
green[0] = 0
green *= green_target_end / green[-1]  # rescale so it lands exactly on target

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6.5))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

ax.plot(x, black, color=BLACK_COLOR, linewidth=1.8, zorder=3)
ax.plot(x, green, color=GREEN_COLOR, linewidth=2.2, zorder=3)

# Midpoint divider between Creation and Alteration
ax.axvline(5, color="#555555", linewidth=1)

# ── Y-axis as HH:MM ────────────────────────────────────────────────────────
ax.set_ylim(0, 11)
yticks = np.arange(0, 12, 1)
ax.set_yticks(yticks)
ax.set_yticklabels([f"{int(t)}:00" for t in yticks], fontsize=10)
ax.set_ylabel("Total working time (hours)", fontsize=11)

# ── X-axis ────────────────────────────────────────────────────────────────
ax.set_xlim(0, 10)
ax.set_xticks([])

ax.grid(axis="y", color="#dddddd", linewidth=0.8, zorder=0)

# Full box border, as in the reference
for side in ["top", "right", "left", "bottom"]:
    ax.spines[side].set_visible(True)
    ax.spines[side].set_color("#1a1a1a")
    ax.spines[side].set_linewidth(1.2)

# ── Creation / Alteration phase brackets under the x-axis ───────────────────
y_line, y_text = -0.09, -0.12
ax.annotate("", xy=(4.85, y_line), xytext=(0.15, y_line),
            xycoords=("data", "axes fraction"), textcoords=("data", "axes fraction"),
            annotation_clip=False,
            arrowprops=dict(arrowstyle="-", color="#333333", linewidth=1))
ax.text(2.5, y_text, "Creation", ha="center", va="top", fontsize=11,
        transform=ax.get_xaxis_transform())

ax.annotate("", xy=(9.85, y_line), xytext=(5.15, y_line),
            xycoords=("data", "axes fraction"), textcoords=("data", "axes fraction"),
            annotation_clip=False,
            arrowprops=dict(arrowstyle="-", color="#333333", linewidth=1))
ax.text(7.5, y_text, "Alteration", ha="center", va="top", fontsize=11,
        transform=ax.get_xaxis_transform())

ax.text(5, -0.20, "Progress in test set", ha="center", va="top", fontsize=11,
        transform=ax.get_xaxis_transform())

# ── Right-side annotations: labels + double-headed arrow + "70% saved" ──────
ax.annotate("", xy=(10, black[-1]), xytext=(10, green[-1]),
            xycoords="data", annotation_clip=False,
            arrowprops=dict(arrowstyle="<->", color="black", linewidth=2))

ax.text(10.3, black[-1], "PowerPoint with\ntemplates & macros",
        fontsize=11, va="center", ha="left")
ax.text(10.3, green[-1], "PowerPoint with\nthink-cell",
        fontsize=11, va="center", ha="left")
ax.text(10.55, (black[-1] + green[-1]) / 2, "70% working\ntime saved",
        fontsize=12, va="center", ha="left", fontweight="bold")

plt.subplots_adjust(right=0.72, bottom=0.24, left=0.08, top=0.95)
plt.savefig("output/thinkcell_time_saved.png", dpi=200, facecolor="white", bbox_inches="tight")
print("Saved output/thinkcell_time_saved.png")
