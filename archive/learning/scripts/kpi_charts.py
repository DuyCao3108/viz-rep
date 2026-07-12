import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

# ── Colors ────────────────────────────────────────────────────────────────────
TG_COLOR = "#2E75B6"   # blue
CG_COLOR = "#FFC000"   # gold/orange

# ── Data ──────────────────────────────────────────────────────────────────────
D12 = ["25-03","25-04","25-05","25-06","25-07","25-08",
       "25-09","25-10","25-11","25-12","26-01","26-02"]
D11 = D12[1:]   # avg. amt balance starts at 25-04

CHARTS = [
    dict(
        title="% transaction rate",
        dates=D12,
        TG=[82, 76, 69, 65, 62, 60, 58, 56, 54, 52, 50, 48],
        CG=[70, 68, 65, 60, 57, 54, 52, 50, 49, 50, 52, 53],
        fmt=lambda v: f"{v}%",
    ),
    dict(
        title="% limit util rate",
        dates=D12,
        TG=[25, 29, 29, 29, 29, 28, 28, 28, 28, 27, 26, 26],
        CG=[33, 36, 36, 38, 39, 38, 40, 40, 40, 40, 39, 39],
        fmt=lambda v: f"{v}%",
    ),
    dict(
        title="avg. amt balance",
        dates=D11,
        TG=[9, 10, 10, 11, 11, 11, 11, 11, 12, 12, 11],
        CG=[6,  7,  7,  7,  7,  7,  7,  7,  7,  7,  6],
        fmt=lambda v: f"{v}M",
    ),
    dict(
        title="% active (KPI card logic)",
        dates=D12,
        TG=[87, 81, 81, 79, 77, 76, 75, 74, 74, 72, 72, 72],
        CG=[78, 82, 75, 73, 71, 69, 67, 65, 63, 61, 59, 59],
        fmt=lambda v: f"{v}%",
    ),
]

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.patch.set_facecolor("white")
plt.subplots_adjust(hspace=0.55, wspace=0.12)

LEGEND_HANDLES = [
    Line2D([0], [0], color=TG_COLOR, marker="o", markersize=5, linewidth=1.2, label="TG"),
    Line2D([0], [0], color=CG_COLOR, marker="o", markersize=5, linewidth=1.2, label="CG"),
]

for ax, ch in zip(axes.flat, CHARTS):
    tg, cg = ch["TG"], ch["CG"]
    fmt    = ch["fmt"]
    x      = np.arange(len(ch["dates"]))

    # ── Background + grid ─────────────────────────────────────────────────────
    ax.set_facecolor("#f5f5f5")
    ax.yaxis.grid(True, color="white", linewidth=1.2, zorder=0)
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)

    # ── Lines ─────────────────────────────────────────────────────────────────
    ax.plot(x, tg, color=TG_COLOR, linewidth=1.5,
            marker="o", markersize=4, markeredgewidth=0, zorder=3)
    ax.plot(x, cg, color=CG_COLOR, linewidth=1.5,
            marker="o", markersize=4, markeredgewidth=0, zorder=3)

    # ── Data labels (smart: higher line → label above, lower → below) ─────────
    spread = max(max(tg), max(cg)) - min(min(tg), min(cg))
    pad    = max(spread * 0.065, 0.3)

    for i, (t, c) in enumerate(zip(tg, cg)):
        if t >= c:
            ax.text(i, t + pad, fmt(t), ha="center", va="bottom",
                    fontsize=6.8, color="#222222")
            ax.text(i, c - pad, fmt(c), ha="center", va="top",
                    fontsize=6.8, color="#222222")
        else:
            ax.text(i, t - pad, fmt(t), ha="center", va="top",
                    fontsize=6.8, color="#222222")
            ax.text(i, c + pad, fmt(c), ha="center", va="bottom",
                    fontsize=6.8, color="#222222")

    # ── Y-axis limits (extra top margin for legend) ────────────────────────────
    all_v = tg + cg
    ax.set_ylim(min(all_v) - spread * 0.28,
                max(all_v) + spread * 0.48)

    # ── X-axis ────────────────────────────────────────────────────────────────
    ax.set_xticks(x)
    ax.set_xticklabels(ch["dates"], fontsize=7, color="#555555")
    ax.tick_params(axis="x", length=0, pad=2)

    # ── Y-axis: hide ──────────────────────────────────────────────────────────
    ax.tick_params(axis="y", left=False, labelleft=False)
    ax.yaxis.set_visible(False)

    # ── Spines ────────────────────────────────────────────────────────────────
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#cccccc")
    ax.spines["bottom"].set_linewidth(0.8)

    # ── Title ─────────────────────────────────────────────────────────────────
    ax.set_title(ch["title"], fontsize=8.5, loc="left", color="#333333", pad=20)

    # ── Legend (anchored just above the axes, below the title) ────────────────
    ax.legend(handles=LEGEND_HANDLES,
              loc="lower left", bbox_to_anchor=(0, 1.0),
              fontsize=7.5, frameon=False, ncol=2,
              handlelength=1.2, handleheight=0.8,
              columnspacing=0.6, handletextpad=0.3,
              borderaxespad=0)

plt.savefig("kpi_charts.png", dpi=150, bbox_inches="tight")
print("Saved kpi_charts.png")
plt.show()
