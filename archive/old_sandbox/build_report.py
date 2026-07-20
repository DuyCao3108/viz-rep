#!/usr/bin/env python3
"""
Recreate the Power BI report "Insight_CVM_PCB_Card_Analysis" using matplotlib.

What this script does
---------------------
1. Renders the 8 Power BI chart images (each a composite of several sub-charts)
   from scratch with matplotlib, at high resolution, matching the originals as
   closely as possible in layout, colours, fonts, data and data-labels.
2. Rebuilds the .xlsx file: an exact byte-for-byte copy of the original
   (same sheet, same text, same layout, same drawing anchors) with ONLY the 8
   embedded chart PNGs swapped for the freshly rendered matplotlib versions.

Everything (chart PNGs + rebuilt workbook) is written to sandbox/output/.

The whole point is to test how faithfully — and at what resolution — matplotlib
can reproduce polished Power BI visuals.  Power BI uses the "Segoe UI" font,
which is not present on macOS; "Arial" is used as the closest installed
substitute (change FONT below if a better match is installed).
"""

import os
import zipfile

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# --------------------------------------------------------------------------- #
#  Paths
# --------------------------------------------------------------------------- #
HERE = os.path.dirname(os.path.abspath(__file__))
REF_XLSX = os.path.join(HERE, "refs", "Insight_CVM_PCB_Card_Analysis.xlsx")
OUT_DIR = os.path.join(HERE, "output")
OUT_XLSX = os.path.join(OUT_DIR, "Insight_CVM_PCB_Card_Analysis.xlsx")
os.makedirs(OUT_DIR, exist_ok=True)

# --------------------------------------------------------------------------- #
#  Global style
# --------------------------------------------------------------------------- #
FONT = "Arial"                # closest widely-installed stand-in for "Segoe UI"
DPI = 300                     # high resolution output
PXPERIN = 110.0              # orig_px / PXPERIN -> figure inches (keeps text size consistent)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [FONT, "Helvetica", "DejaVu Sans"],
    "svg.fonttype": "none",
    "axes.linewidth": 0.8,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})

# Power BI palette (measured from the originals) ---------------------------- #
BLUE = "#1985D9"
GOLD = "#F5A91B"
RED = "#E23555"
TEAL = "#3F9C8A"

TITLE_C = "#605E5C"          # Power BI muted title colour
TEXT_C = "#252423"           # data-label colour
AXIS_C = "#3B3B3B"           # category-axis label colour

# font sizes (points) ------------------------------------------------------- #
FS_TITLE = 12
FS_LEG = 10
FS_DATA = 10.5
FS_AXIS = 9.5

MONTHS = ["25-03", "25-04", "25-05", "25-06", "25-07", "25-08",
          "25-09", "25-10", "25-11", "25-12", "26-01", "26-02"]
N = len(MONTHS)


def light(color, a=0.40):
    """Power BI bar fill = saturated colour drawn at ~40% alpha over white."""
    r, g, b = matplotlib.colors.to_rgb(color)
    return (r * a + (1 - a), g * a + (1 - a), b * a + (1 - a))


# --------------------------------------------------------------------------- #
#  Low level building blocks
# --------------------------------------------------------------------------- #
def new_fig(orig_w, orig_h):
    """Figure whose aspect matches the original image, at high DPI."""
    w_in = orig_w / PXPERIN
    h_in = orig_h / PXPERIN
    fig = plt.figure(figsize=(w_in, h_in), dpi=DPI)
    return fig


def bare(ax):
    """Strip an axes down to Power BI style: no spines, no ticks, no y axis."""
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_yticks([])
    ax.tick_params(axis="x", length=0)


def cat_axis(ax, labels, fs=FS_AXIS):
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=fs, color=AXIS_C)
    ax.set_xlim(-0.6, len(labels) - 0.4)


def title(ax, text, y=1.16, fs=FS_TITLE, color=TITLE_C, weight="normal"):
    ax.text(0.0, y, text, transform=ax.transAxes, ha="left", va="baseline",
            fontsize=fs, color=color, fontweight=weight, clip_on=False)


def hlegend(ax, tokens, y=1.05, x0=0.0, fs=FS_LEG):
    """Draw a horizontal Power-BI style legend in axes coords, left to right.

    tokens: list of
        ("bold", str, color)        bold text (e.g. field name)
        ("text", str, color)        normal text
        ("dot",  color, "bar"/"line")  a category marker (circle)
    """
    fig = ax.figure
    r = fig.canvas.get_renderer()
    axw = ax.get_window_extent(r).width
    dppx = fig.dpi / 72.0                     # points -> px

    def to_ax(px):
        return px / axw

    x = x0
    for tok in tokens:
        kind = tok[0]
        if kind in ("text", "bold"):
            t = ax.text(x, y, tok[1], transform=ax.transAxes, ha="left",
                        va="center", fontsize=fs, color=tok[2],
                        fontweight=("bold" if kind == "bold" else "normal"),
                        clip_on=False)
            w = t.get_window_extent(r).width
            x += to_ax(w) + to_ax(6 * dppx)
        elif kind == "dot":
            color, style = tok[1], tok[2]
            face = light(color) if style == "bar" else color
            d = to_ax(6 * dppx)               # half advance
            ax.scatter([x + d], [y], transform=ax.transAxes,
                       s=(fs * 0.95) ** 2, facecolor=face, edgecolor=color,
                       linewidths=1.4, clip_on=False, zorder=6)
            x += to_ax(13 * dppx) + to_ax(3 * dppx)
    return x


# --------------------------------------------------------------------------- #
#  Chart types
# --------------------------------------------------------------------------- #
def pct_stacked(ax, series, colors, months=MONTHS, thresh=3.0, width=0.60):
    """100% stacked column chart with centered % labels."""
    n = len(months)
    x = np.arange(n)
    data = np.array(series, dtype=float)              # (segments, n)
    totals = data.sum(axis=0)
    norm = data / totals * 100.0
    bottom = np.zeros(n)
    for seg, col in enumerate(colors):
        vals = norm[seg]
        ax.bar(x, vals, width, bottom=bottom, facecolor=light(col),
               edgecolor=col, linewidth=1.1)
        for i in range(n):
            if vals[i] >= thresh:
                ax.text(i, bottom[i] + vals[i] / 2, f"{vals[i]:.0f}%",
                        ha="center", va="center", fontsize=FS_DATA, color=TEXT_C)
        bottom += vals
    bare(ax)
    cat_axis(ax, months)
    ax.set_ylim(0, 100)


def abs_stacked(ax, blue, gold, totals, tot_fmt, seg_fmt,
                blue_show=None, gold_show=None, months=MONTHS, width=0.56):
    """Absolute 2-segment stacked column with inner labels + bold total on top."""
    n = len(months)
    x = np.arange(n)
    blue = np.array(blue, float)
    gold = np.array(gold, float)
    if blue_show is None:
        blue_show = [True] * n
    if gold_show is None:
        gold_show = [True] * n
    ax.bar(x, blue, width, facecolor=light(BLUE), edgecolor=BLUE, linewidth=1.1)
    ax.bar(x, gold, width, bottom=blue, facecolor=light(GOLD), edgecolor=GOLD,
           linewidth=1.1)
    ymax = (blue + gold).max()
    for i in range(n):
        if blue_show[i]:
            ax.text(i, blue[i] / 2, seg_fmt(blue[i]), ha="center", va="center",
                    fontsize=FS_DATA, color=TEXT_C)
        if gold_show[i]:
            ax.text(i, blue[i] + gold[i] / 2, seg_fmt(gold[i]), ha="center",
                    va="center", fontsize=FS_DATA, color=TEXT_C)
        ax.text(i, blue[i] + gold[i] + ymax * 0.02, tot_fmt(totals[i]),
                ha="center", va="bottom", fontsize=FS_DATA, color=TEXT_C,
                fontweight="bold")
    bare(ax)
    cat_axis(ax, months)
    ax.set_ylim(0, ymax * 1.22)


def grouped_bars(ax, blue, gold, fmt, blue_show=None, gold_show=None,
                 months=MONTHS, width=0.34):
    """Two columns per category (blue / gold) with value labels above each."""
    n = len(months)
    x = np.arange(n)
    blue = np.array(blue, float)
    gold = np.array(gold, float)
    if blue_show is None:
        blue_show = [True] * n
    if gold_show is None:
        gold_show = [True] * n
    ax.bar(x - width / 2 - 0.02, blue, width, facecolor=light(BLUE),
           edgecolor=BLUE, linewidth=1.1)
    ax.bar(x + width / 2 + 0.02, gold, width, facecolor=light(GOLD),
           edgecolor=GOLD, linewidth=1.1)
    ymax = max(blue.max(), gold.max())
    for i in range(n):
        if blue_show[i]:
            ax.text(i - width / 2 - 0.02, blue[i] + ymax * 0.015, fmt(blue[i]),
                    ha="center", va="bottom", fontsize=FS_DATA, color=TEXT_C)
        if gold_show[i]:
            ax.text(i + width / 2 + 0.02, gold[i] + ymax * 0.015, fmt(gold[i]),
                    ha="center", va="bottom", fontsize=FS_DATA, color=TEXT_C)
    bare(ax)
    cat_axis(ax, months)
    ax.set_ylim(0, ymax * 1.18)


def _label_side(series_list, i):
    """For multi-series lines: highest point labels above, others below."""
    vals = [s[i] for s in series_list]
    hi = max(range(len(vals)), key=lambda k: vals[k])
    return hi


def line_panel(ax, series_list, colors, fmt, months=MONTHS, ymin=None, ymax=None):
    """1 or 2 line series with round markers and a data label at every point."""
    n = len(months)
    x = np.arange(n)
    for s, col in zip(series_list, colors):
        ax.plot(x, s, color=col, linewidth=2.2, marker="o", markersize=4.5,
                markerfacecolor=col, markeredgecolor=col, zorder=3,
                solid_capstyle="round", clip_on=False)

    allv = np.concatenate([np.array(s, float) for s in series_list])
    lo = allv.min() if ymin is None else ymin
    hi = allv.max() if ymax is None else ymax
    span = (hi - lo) or 1.0
    pad = span * 0.20
    ax.set_ylim(lo - pad, hi + pad)
    off = span * 0.10

    if len(series_list) == 2:
        for i in range(n):
            hiidx = _label_side(series_list, i)
            for k, s in enumerate(series_list):
                dy = off if k == hiidx else -off
                va = "bottom" if dy > 0 else "top"
                ax.text(i, s[i] + dy, fmt(s[i]), ha="center", va=va,
                        fontsize=FS_DATA, color=TEXT_C)
    else:
        s = series_list[0]
        for i in range(n):
            local_min = (0 < i < n - 1 and s[i] <= s[i - 1] and s[i] <= s[i + 1])
            dy = -off if local_min else off
            va = "top" if local_min else "bottom"
            ax.text(i, s[i] + dy, fmt(s[i]), ha="center", va=va,
                    fontsize=FS_DATA, color=TEXT_C)
    bare(ax)
    cat_axis(ax, months)


def multi_stacked(ax, mat, colors, months, thresh=4.0, width=0.68):
    """100% stacked column with many segments (image6). mat: (n_cat, n_col)."""
    x = np.arange(len(months))
    data = np.array(mat, float)                       # (cat, col)
    totals = data.sum(axis=0)
    totals[totals == 0] = 1
    norm = data / totals * 100.0
    bottom = np.zeros(len(months))
    for seg, col in enumerate(colors):
        vals = norm[seg]                              # normalized heights (fill to 100%)
        raw = data[seg]                               # transcribed values (shown as labels)
        ax.bar(x, vals, width, bottom=bottom, facecolor=light(col),
               edgecolor=col, linewidth=1.0)
        for i in range(len(months)):
            if raw[i] >= thresh:
                ax.text(i, bottom[i] + vals[i] / 2, f"{raw[i]:.0f}%",
                        ha="center", va="center", fontsize=FS_DATA - 1.5,
                        color=TEXT_C)
        bottom += vals
    bare(ax)
    cat_axis(ax, months)
    ax.set_ylim(0, 100)


# formatters ---------------------------------------------------------------- #
def f_pct(v):
    return f"{v:.0f}%"


def f_k0(v):
    return f"{v:.0f}K"


def f_k1(v):
    return f"{v:.1f}K"


def f_bn(v):
    return f"{v:.0f}bn"


def f_m(v):
    return f"{v:.0f}M"


def f_int(v):
    return f"{v:.0f}"


# --------------------------------------------------------------------------- #
#  Data
# --------------------------------------------------------------------------- #
# image 1 -- rival-at-sign / rival-within-month, % and # ----
I1A = ([86, 87, 87, 87, 87, 88, 87, 86, 85, 86, 87, 88],
       [14, 13, 13, 13, 13, 12, 13, 14, 15, 14, 13, 12])
I1C = ([86, 86, 87, 87, 87, 87, 87, 87, 87, 86, 86, 87],
       [14, 14, 13, 13, 13, 13, 13, 13, 13, 14, 14, 13])
I1B_BLUE = [11.7, 12.4, 12.9, 12.5, 12.3, 12.5, 13.3, 13.3, 12.9, 13.6, 14.0, 10.9]
I1B_GOLD = [1.9, 1.9, 2.0, 1.8, 1.9, 1.8, 2.0, 2.2, 2.3, 2.2, 2.2, 1.6]
I1B_TOT = [14, 14, 15, 14, 14, 14, 15, 16, 15, 16, 16, 12]
I1D_BLUE = [12, 24, 37, 49, 62, 74, 88, 101, 114, 127, 141, 152]
I1D_GOLD = [2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 22, 24]
I1D_TOT = [14, 28, 43, 57, 71, 85, 101, 116, 131, 147, 163, 176]
I1D_GOLD_SHOW = [i >= 4 for i in range(N)]

# image 2 -- TG vs CG lines ----
I2A = ([78, 74, 69, 65, 62, 60, 58, 58, 56, 56, 53, 48],
       [87, 72, 62, 55, 50, 47, 45, 43, 41, 40, 38, 33])
I2B = ([26, 33, 36, 36, 38, 38, 38, 39, 40, 40, 40, 39],
       [25, 29, 29, 29, 29, 29, 28, 28, 28, 28, 27, 26])
I2C = ([7, 9, 10, 10, 11, 11, 11, 11, 11, 12, 12, 11],
       [6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6])
I2D = ([78, 82, 81, 79, 78, 77, 76, 75, 74, 74, 72, 71],
       [87, 81, 78, 75, 73, 71, 69, 67, 65, 63, 61, 59])

# image 3 -- 6M-before-sign (3 months) ----
M3 = ["25-10", "25-11", "25-12"]
I3A = ([57, 55, 50], [88, 59, 88])
I3B = ([20, 19, 18], [29, 25, 27])

# image 4 -- application channel ----
I4CG = dict(happy=[8, 8, 8, 8, 8, 8, 8, 8, 10, 9, 9, 8],
            sa=[80, 80, 80, 79, 80, 80, 81, 81, 78, 79, 80, 83],
            tls=[12, 11, 12, 13, 12, 12, 11, 11, 12, 12, 12, 10])
I4TG = dict(happy=[21, 17, 17, 18, 18, 17, 18, 18, 22, 16, 16, 13],
            sa=[57, 63, 63, 61, 63, 61, 62, 61, 60, 63, 63, 69],
            tls=[21, 19, 20, 21, 18, 21, 20, 21, 18, 20, 21, 18])


def happy_sa(d):
    return [max(0.0, 100 - a - b - c) for a, b, c in zip(d["happy"], d["sa"], d["tls"])]


# image 5 -- PCB data-request analysis ----
I5A_BLUE = [12, 21, 33, 44, 55, 66, 76, 88, 99, 109, 121, 131]
I5A_GOLD = [2, 7, 10, 13, 16, 20, 24, 28, 32, 38, 42, 45]
I5A_TOT = [14, 28, 43, 57, 71, 85, 101, 116, 131, 147, 163, 176]
I5A_BLUE_SHOW = [i >= 1 for i in range(N)]
I5A_GOLD_SHOW = [i >= 3 for i in range(N)]
I5ML_BLUE = [9, 16, 30, 49, 64, 77, 96, 110, 136, 167, 198, 203]
I5ML_GOLD = [26, 46, 66, 78, 96, 116, 131, 163, 177, 216, 227, 203]
I5ML_GOLD_SHOW = [i != 8 for i in range(N)]
I5BL_BLUE = [32, 59, 91, 132, 173, 205, 267, 311, 385, 458, 526, 539]
I5BL_GOLD = [26, 52, 89, 126, 160, 196, 248, 290, 339, 403, 451, 459]
I5BL_GOLD_SHOW = [i >= 8 for i in range(N)]
I5TR = [25, 23, 23, 23, 23, 23, 24, 24, 24, 26, 26, 26]
I5MR = [66, 65, 54, 37, 33, 34, 26, 32, 23, 23, 13, -0.3]
I5BR = [28, 7, -1, 7, 5, 2, 8, 7, 12, 12, 14, 15]

# image 6 -- segment distribution through MOB (0..9 bottom->top) ----
SEG_COLORS = ["#EB6B30", "#6E64A0", "#25C0BE", "#256B82", "#B76B6B",
              "#2D9187", "#F71411", "#3EB6DC", "#FA5A16", "#199D5A"]
SEG_LABELS = ["0-Not Ready to Use", "1-EMOB", "2-Inactive", "3-Silent Attrition",
              "4-Hard Transactor", "5-EPP Transactor", "6-Low Utilization Revolver",
              "7-High Utilization Revolver", "8-Light Cash Revolver",
              "9-Heavy Cash Revolver"]
MOB = [str(i) for i in range(12)]
# rows = MOB 0..11 ; cols = seg 0..9
CG6 = [
    [16, 84, 0, 0, 0, 0, 0, 0, 0, 0],
    [15, 85, 0, 0, 0, 0, 0, 0, 0, 0],
    [16, 84, 0, 0, 0, 0, 0, 0, 0, 0],
    [17, 0, 13, 12, 26, 26, 1, 0.5, 2, 1],
    [17, 0, 14, 13, 20, 25, 1, 0.5, 5, 1.5],
    [18, 0, 12, 15, 16, 24, 5, 0.5, 6, 1.5],
    [19, 0, 12, 14, 21, 16, 6, 1, 7, 2],
    [20, 0, 9, 14, 21, 16, 7, 1, 8, 2],
    [20, 0, 8, 13, 21, 16, 8, 1, 8, 2],
    [19, 0, 8, 11, 21, 17, 9, 1, 9, 2],
    [19, 0, 7, 10, 22, 17, 9, 4, 9, 2],
    [19, 0, 6, 9, 23, 17, 9, 4, 9, 5],
]
TG6 = [
    [20, 80, 0, 0, 0, 0, 0, 0, 0, 0],
    [13, 87, 0, 0, 0, 0, 0, 0, 0, 0],
    [13, 87, 0, 0, 0, 0, 0, 0, 0, 0],
    [14, 0, 8, 6, 37, 28, 1, 0.5, 4, 1.5],
    [14, 0, 7, 6, 30, 27, 5, 1, 6, 1.5],
    [14, 0, 6, 7, 26, 26, 7, 1, 8, 2],
    [14, 0, 7, 7, 28, 20, 8, 4, 8, 2],
    [14, 0, 6, 7, 28, 20, 9, 5, 8, 4],
    [15, 0, 4, 6, 28, 19, 9, 6, 8, 4],
    [14, 0, 5, 5, 29, 20, 10, 6, 8, 5],
    [15, 0, 4, 4, 28, 19, 10, 7, 8, 5],
    [14, 0, 4, 4, 29, 19, 9, 7, 6, 7],
]

# image 7 -- number of active rival cards at sign ----
CAT8_COLORS = [BLUE, GOLD, RED, TEAL, "#CBD64B", "#EA6C2F", "#6E64A0", "#25C0BE"]
T7 = [
    [1497, 347, 47, 4, 0, 0, 0, 0],
    [1505, 299, 58, 1, 0, 0, 0, 0],
    [1595, 325, 42, 1, 0, 0, 0, 0],
    [1529, 239, 44, 4, 0, 0, 0, 0],
    [1570, 281, 43, 4, 1, 0, 0, 0],
    [1448, 261, 46, 2, 1, 0, 0, 0],
    [1589, 310, 58, 8, 4, 4, 1, 0],
    [1768, 331, 86, 15, 11, 4, 3, 2],
    [1815, 371, 84, 24, 8, 7, 5, 2],
    [1822, 342, 38, 1, 1, 1, 0, 1],
    [1797, 313, 56, 4, 3, 1, 0, 0],
    [1310, 203, 39, 3, 3, 1, 0, 0],
]

# image 8 -- BANK vs OTHERFIN ----
I8L = ([76, 75, 71, 68, 66, 64, 62, 62, 60, 60, 58, 52],
       [82, 74, 66, 61, 57, 53, 52, 52, 50, 50, 46, 41])
I8R = ([7, 10, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13],
       [7, 8, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10])


# --------------------------------------------------------------------------- #
#  Panel layout helper
# --------------------------------------------------------------------------- #
def panels(fig, nrows, ncols, left=0.045, right=0.99, top=0.885, bottom=0.075,
           wgap=0.085, hgap=0.20):
    pw = (right - left - (ncols - 1) * wgap) / ncols
    ph = (top - bottom - (nrows - 1) * hgap) / nrows
    axs = []
    for r in range(nrows):
        for c in range(ncols):
            x = left + c * (pw + wgap)
            y = top - (r + 1) * ph - r * hgap
            axs.append(fig.add_axes([x, y, pw, ph]))
    return axs


# --------------------------------------------------------------------------- #
#  The 8 composite renderers
# --------------------------------------------------------------------------- #
def render_image1(path):
    fig = new_fig(1491, 767)
    tl, tr, bl, br = panels(fig, 2, 2, top=0.86, bottom=0.07, hgap=0.24)

    field1 = "F_ACT_RIVAL_AT_SIGN"
    field2 = "F_ACT_RIVAL_WI_MONTH"

    pct_stacked(tl, [I1A[0], I1A[1]], [BLUE, GOLD])
    title(tl, "% Client active card rival at sign month (TG) / new card signed")
    hlegend(tl, [("bold", field1, TEXT_C), ("dot", BLUE, "bar"), ("text", "0", TEXT_C),
                 ("dot", GOLD, "bar"), ("text", "1", TEXT_C)])

    abs_stacked(tr, I1B_BLUE, I1B_GOLD, I1B_TOT, f_k0, f_k1)
    title(tr, "# Client active card rival at sign month, # new card signed")
    hlegend(tr, [("bold", field1, TEXT_C), ("dot", BLUE, "bar"), ("text", "0", TEXT_C),
                 ("dot", GOLD, "bar"), ("text", "1", TEXT_C)])

    pct_stacked(bl, [I1C[0], I1C[1]], [BLUE, GOLD])
    title(bl, "% Client active card rival wi month/ card active wi month")
    hlegend(bl, [("bold", field2, TEXT_C), ("dot", BLUE, "bar"), ("text", "0", TEXT_C),
                 ("dot", GOLD, "bar"), ("text", "1", TEXT_C)])

    abs_stacked(br, I1D_BLUE, I1D_GOLD, I1D_TOT, f_k0, f_k0,
                gold_show=I1D_GOLD_SHOW)
    title(br, "# Client active card rival wi month, # card active wi month")
    hlegend(br, [("bold", field2, TEXT_C), ("dot", BLUE, "bar"), ("text", "0", TEXT_C),
                 ("dot", GOLD, "bar"), ("text", "1", TEXT_C)])

    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def render_image2(path):
    fig = new_fig(1492, 736)
    tl, tr, bl, br = panels(fig, 2, 2, top=0.87, bottom=0.07, hgap=0.24)
    leg = [("dot", BLUE, "line"), ("text", "TG", TEXT_C),
           ("dot", GOLD, "line"), ("text", "CG", TEXT_C)]
    for ax, (data, ttl) in zip(
            [tl, tr, bl, br],
            [(I2A, "% transaction rate"), (I2B, "% limit util rate"),
             (I2C, "avg. amt balance"), (I2D, "% active (KPI card logic)")]):
        fmt = f_m if ttl.startswith("avg") else f_pct
        line_panel(ax, [data[0], data[1]], [BLUE, GOLD], fmt)
        title(ax, ttl)
        hlegend(ax, leg)
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def render_image3(path):
    fig = new_fig(747, 751)
    top, bot = panels(fig, 2, 1, left=0.06, right=0.98, top=0.90, bottom=0.07,
                      hgap=0.30)
    leg = [("dot", BLUE, "line"), ("text", "Clients sign HCVN card wi month (GR1)", TEXT_C),
           ("dot", GOLD, "line"), ("text", "All active card users any lender - GR1", TEXT_C)]
    line_panel(top, [I3A[0], I3A[1]], [BLUE, GOLD], f_pct, months=M3)
    title(top, "% Limit util rate 6M before sign (OB/ Credit limit)")
    hlegend(top, leg, fs=FS_LEG - 1.5)
    line_panel(bot, [I3B[0], I3B[1]], [BLUE, GOLD], f_m, months=M3)
    title(bot, "Avg. outstanding balance 6M before sign")
    hlegend(bot, leg, fs=FS_LEG - 1.5)
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def render_image4(path):
    fig = new_fig(748, 743)
    # super title + legend at top, two stacked panels below
    top, bot = panels(fig, 2, 1, left=0.06, right=0.98, top=0.80, bottom=0.07,
                      hgap=0.14)
    colors = [BLUE, GOLD, RED, TEAL]
    fig.text(0.06, 0.955, "Compare application channel between TG and CG",
             fontsize=FS_TITLE, color=TITLE_C, ha="left", va="center")
    # legend row on a helper axes
    lax = fig.add_axes([0.06, 0.885, 0.92, 0.04])
    lax.axis("off")
    hlegend(lax, [("dot", BLUE, "bar"), ("text", "HAPPY", TEXT_C),
                  ("dot", GOLD, "bar"), ("text", "HAPPY_SA", TEXT_C),
                  ("dot", RED, "bar"), ("text", "SA", TEXT_C),
                  ("dot", TEAL, "bar"), ("text", "TLS", TEXT_C)], y=0.5)

    for ax, d, tag in [(top, I4CG, "CG"), (bot, I4TG, "TG")]:
        series = [d["happy"], happy_sa(d), d["sa"], d["tls"]]
        pct_stacked(ax, series, colors, thresh=3.0)
        ax.text(0.0, 1.06, tag, transform=ax.transAxes, fontsize=FS_TITLE,
                color=TITLE_C, ha="left", va="baseline")
    # separator line between the two groups
    fig.add_artist(Line2D([0.02, 0.99], [0.455, 0.455], color="#7F7F7F",
                          linewidth=1.0, transform=fig.transFigure))
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def render_image5(path):
    fig = new_fig(1368, 1020)
    axs = panels(fig, 3, 2, left=0.05, right=0.985, top=0.90, bottom=0.05,
                 hgap=0.20, wgap=0.11)
    tl, tr, ml, mr, bl, br = axs

    abs_stacked(tl, I5A_BLUE, I5A_GOLD, I5A_TOT, f_k0, f_k0,
                blue_show=I5A_BLUE_SHOW, gold_show=I5A_GOLD_SHOW)
    title(tl, "# Client has PCB data request")
    hlegend(tl, [("bold", "F_HAS_PCB_REQUEST", TEXT_C), ("dot", BLUE, "bar"),
                 ("text", "0", TEXT_C), ("dot", GOLD, "bar"), ("text", "1", TEXT_C)])

    line_panel(tr, [I5TR], [BLUE], f_pct)
    title(tr, "% Client has PCB data request")

    grouped_bars(ml, I5ML_BLUE, I5ML_GOLD, f_bn, gold_show=I5ML_GOLD_SHOW)
    title(ml, "Comparing Amount transaction")
    hlegend(ml, [("dot", BLUE, "bar"), ("text", "Amt charged PCB", TEXT_C),
                 ("dot", GOLD, "bar"), ("text", "Amt transaction HCVN", TEXT_C)])

    line_panel(mr, [I5MR], [BLUE], f_pct)
    title(mr, "%. 1 - (Amt transaction HCVN/ Amt charged PCB)")

    grouped_bars(bl, I5BL_BLUE, I5BL_GOLD, f_bn, gold_show=I5BL_GOLD_SHOW)
    title(bl, "Comparing Balance")
    hlegend(bl, [("dot", BLUE, "bar"), ("text", "Amt residual PCB", TEXT_C),
                 ("dot", GOLD, "bar"), ("text", "Amt principal balance HCVN", TEXT_C)])

    line_panel(br, [I5BR], [BLUE], f_pct)
    title(br, "%. 1 - (Amt prin. balance HCVN/ Amt residual PCB)")

    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def render_image6(path):
    fig = new_fig(1642, 883)
    # left legend column, two stacked panels on the right
    lax = fig.add_axes([0.005, 0.06, 0.16, 0.80])
    lax.axis("off")
    for k, (col, lab) in enumerate(zip(SEG_COLORS, SEG_LABELS)):
        yy = 0.92 - k * 0.092
        lax.scatter([0.03], [yy], s=150, facecolor=light(col), edgecolor=col,
                    linewidths=1.4, transform=lax.transAxes, clip_on=False)
        lax.text(0.08, yy, lab, transform=lax.transAxes, va="center", ha="left",
                 fontsize=FS_LEG - 2.0, color=TEXT_C)

    fig.text(0.17, 0.965, "Compare segment distribution between TG and CG through MOBs",
             fontsize=FS_TITLE, color=TITLE_C, ha="left", va="center")

    top = fig.add_axes([0.19, 0.55, 0.79, 0.34])
    bot = fig.add_axes([0.19, 0.09, 0.79, 0.34])
    cols_bt = list(zip(*CG6))          # transpose -> (seg, mob)
    multi_stacked(top, cols_bt, SEG_COLORS, MOB)
    top.set_xticklabels([])
    top.text(0.0, 1.04, "CG", transform=top.transAxes, fontsize=FS_TITLE,
             color=TITLE_C, ha="left", va="baseline")
    cols_bt = list(zip(*TG6))
    multi_stacked(bot, cols_bt, SEG_COLORS, MOB)
    bot.text(0.0, 1.04, "TG", transform=bot.transAxes, fontsize=FS_TITLE,
             color=TITLE_C, ha="left", va="baseline")
    fig.add_artist(Line2D([0.19, 0.98], [0.49, 0.49], color="#7F7F7F",
                          linewidth=1.0, transform=fig.transFigure))
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def render_image7(path):
    fig = new_fig(1637, 421)
    # left: 100% stacked bar (cat 1..8) ; right: matrix table
    ax = fig.add_axes([0.035, 0.14, 0.44, 0.68])
    mat = np.array(T7, float)                          # (month, cat)
    series = [mat[:, c] for c in range(8)]             # cat as segments
    pct_stacked(ax, series, CAT8_COLORS, thresh=5.0, width=0.72)
    title(ax, "%. Number of active card rival each client had when signing for HCVN card",
          y=1.22, fs=FS_TITLE - 1)
    toks = []
    for c in range(8):
        toks += [("dot", CAT8_COLORS[c], "bar"), ("text", str(c + 1), TEXT_C)]
    hlegend(ax, toks, y=1.08)

    # ---- table ----
    tax = fig.add_axes([0.50, 0.02, 0.49, 0.96])
    tax.axis("off")
    tax.set_xlim(0, 1)
    tax.set_ylim(0, 1)
    ncol = 8
    x_lab0 = 0.0                       # month label column left
    x_num0 = 0.42                      # first numeric column
    x_numw = (1.0 - x_num0) / ncol
    top_y = 0.93
    row_h = (top_y - 0.02) / (N + 1)   # +1 header row

    def col_center(c):
        return x_num0 + (c + 0.5) * x_numw

    # header
    hy = top_y - row_h / 2
    tax.text(x_lab0, hy, "DATE_CON_SIGNED_MONTH", va="center", ha="left",
             fontsize=FS_DATA - 2.5, color=TEXT_C, fontweight="bold")
    for c in range(ncol):
        tax.text(col_center(c), hy, str(c + 1), va="center", ha="center",
                 fontsize=FS_DATA - 1.0, color=TEXT_C, fontweight="bold")
    # sort arrow under header label
    tax.text(x_lab0 + 0.02, top_y - row_h * 0.98, "▲", va="top", ha="left",
             fontsize=FS_DATA - 5, color="#888888")
    tax.plot([0, 1], [top_y - row_h, top_y - row_h], color="#C8C6C4", lw=1.0)

    for r in range(N):
        ry = top_y - row_h * (r + 1) - row_h / 2
        if r % 2 == 1:
            tax.add_patch(plt.Rectangle((0, ry - row_h / 2), 1, row_h,
                                        facecolor="#F3F2F1", edgecolor="none",
                                        zorder=0))
        tax.text(x_lab0, ry, MONTHS[r], va="center", ha="left",
                 fontsize=FS_DATA - 2.5, color=TEXT_C)
        for c in range(ncol):
            v = T7[r][c]
            if v:
                tax.text(col_center(c) + x_numw * 0.42, ry, f"{v:,}",
                         va="center", ha="right", fontsize=FS_DATA - 2.5,
                         color=TEXT_C)
    fig.text(0.50, 0.965, "Number of active card rival each client had when signing for HCVN card",
             fontsize=FS_TITLE - 1, color=TITLE_C, ha="left", va="center")
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def render_image8(path):
    fig = new_fig(1643, 397)
    left, right = panels(fig, 1, 2, left=0.035, right=0.99, top=0.74,
                         bottom=0.12, wgap=0.10)
    leg = [("dot", BLUE, "line"), ("text", "active BANK card at sign month", TEXT_C),
           ("dot", GOLD, "line"), ("text", "active OTHERFIN card at sign month", TEXT_C)]
    line_panel(left, [I8L[0], I8L[1]], [BLUE, GOLD], f_pct)
    title(left, "% transaction rate", y=1.30)
    hlegend(left, leg, y=1.12)
    line_panel(right, [I8R[0], I8R[1]], [BLUE, GOLD], f_int)
    title(right, "avg. amt balance (mil.)", y=1.30)
    hlegend(right, leg, y=1.12)
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


RENDERERS = {
    "image1.png": render_image1,
    "image2.png": render_image2,
    "image3.png": render_image3,
    "image4.png": render_image4,
    "image5.png": render_image5,
    "image6.png": render_image6,
    "image7.png": render_image7,
    "image8.png": render_image8,
}


# --------------------------------------------------------------------------- #
#  xlsx rebuild : copy original, swap only the media images
# --------------------------------------------------------------------------- #
def build_xlsx(chart_paths):
    with zipfile.ZipFile(REF_XLSX, "r") as zin:
        infos = zin.infolist()
        with zipfile.ZipFile(OUT_XLSX, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in infos:
                data = zin.read(info.filename)
                base = info.filename.rsplit("/", 1)[-1]
                if info.filename.startswith("xl/media/") and base in chart_paths:
                    with open(chart_paths[base], "rb") as fh:
                        data = fh.read()
                zout.writestr(info, data)


# --------------------------------------------------------------------------- #
def main():
    chart_paths = {}
    for name, fn in RENDERERS.items():
        out = os.path.join(OUT_DIR, name)
        print(f"rendering {name} ...")
        fn(out)
        chart_paths[name] = out
    print("rebuilding xlsx ...")
    build_xlsx(chart_paths)
    print(f"done -> {OUT_XLSX}")


if __name__ == "__main__":
    main()
