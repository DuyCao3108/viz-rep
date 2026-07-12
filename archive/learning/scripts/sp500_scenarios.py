import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ── Palette ───────────────────────────────────────────────────────────────────
BLUE_DARK  = "#1F3864"   # Baseline header
BLUE_LIGHT = "#d0e8f8"   # S&P 500 row highlight
GRAY_LINE  = "#b8b8b8"
C_TEXT     = "#111111"
C_DIM      = "#555555"

# ── Data ──────────────────────────────────────────────────────────────────────
SUB_HDRS = [
    "Faster growth\nlower yields",
    "Slower growth\nhigher yields",
    "Recession",
]

ROWS = [
    dict(lbl="2024 EPS growth",              v=["5 %",   "9 %",   "1 %",   "(15)%"]),
    dict(gap=True),
    dict(lbl="Equal-weight P/E",             v=["14 x",  "15 x",  "13 x",  "13 x"]),
    dict(lbl="   %ile rank vs. history",     v=["65%",   "77%",   "58%",   "53%"],   sm=True),
    dict(lbl="Aggregate P/E",                v=["18 x",  "19 x",  "16 x",  "15 x"]),
    dict(lbl="   %ile rank vs. history",     v=["83%",   "86%",   "71%",   "64%"],   sm=True),
    dict(gap=True),
    dict(lbl="Real 10-yr UST yield",         v=["2.3 %", "1.8 %", "3.0 %", "1.3 %"]),
    dict(sep=True),
    dict(lbl="S&P 500 level",                v=["4700",  "5000",  "4150",  "3700"],  bold=True, hl=True),
    dict(lbl="% total return vs. current",   v=["6 %",   "13 %",  "(6)%",  "(16)%"], bold=True, italic=True),
    dict(lbl="   %ile rank since 1976",      v=["29%",   "47%",   "13%",   "5%"],    sm=True),
    dict(gap=True),
    dict(lbl="GS subjective probability",    v=["50%",   "25%",   "10%",   "15%"]),
]

# ── Layout ────────────────────────────────────────────────────────────────────
ROW_H, GAP_H, SEP_H = 0.42, 0.18, 0.10
TITLE_H, HDR_H, FOOTER_H = 0.40, 0.60, 0.56

total_row_h = sum(
    GAP_H if r.get("gap") else SEP_H if r.get("sep") else ROW_H
    for r in ROWS
)

T_L, T_R = 0.25, 9.75
T_TOP     = 6.85
T_BOT     = T_TOP - TITLE_H - HDR_H - total_row_h - FOOTER_H

# Value column layout: label col ends at VAL_START, 4 equal cols to T_R
VAL_START = 3.85
COL_W     = (T_R - VAL_START) / 4
CX        = [VAL_START + (i + 0.5) * COL_W for i in range(4)]

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(10, 7))
ax  = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis("off")
fig.patch.set_facecolor("white")

# ── Outer rounded border ──────────────────────────────────────────────────────
ax.add_patch(FancyBboxPatch(
    (T_L - 0.08, T_BOT - 0.08),
    T_R - T_L + 0.16, T_TOP - T_BOT + 0.16,
    boxstyle="round,pad=0.06",
    edgecolor="#999999", facecolor="white", linewidth=1.3, zorder=0))

# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(T_L + 0.12, T_TOP - TITLE_H / 2,
        "Exhibit 19: S&P 500 index scenarios at year-end 2024",
        fontsize=10.5, fontweight="bold", va="center", ha="left", color=C_TEXT)

# ── Column headers ────────────────────────────────────────────────────────────
HDR_TOP = T_TOP - TITLE_H
HDR_BOT = HDR_TOP - HDR_H
HDR_MID = (HDR_TOP + HDR_BOT) / 2

# Baseline: dark blue filled box
ax.add_patch(Rectangle(
    (CX[0] - COL_W / 2 + 0.08, HDR_BOT + 0.05),
    COL_W - 0.16, HDR_H - 0.06,
    facecolor=BLUE_DARK, edgecolor="none", zorder=2))
ax.text(CX[0], HDR_MID, "Baseline",
        fontsize=9.5, fontweight="bold", color="white",
        ha="center", va="center", zorder=3)

for hdr, cx in zip(SUB_HDRS, CX[1:]):
    ax.text(cx, HDR_MID, hdr,
            fontsize=8.2, ha="center", va="center",
            color=C_TEXT, linespacing=1.35)

ax.plot([T_L, T_R], [HDR_BOT] * 2, color=GRAY_LINE, lw=1.0)

# ── Data rows ─────────────────────────────────────────────────────────────────
y = HDR_BOT
for r in ROWS:
    is_gap = r.get("gap", False)
    is_sep = r.get("sep", False)
    h      = GAP_H if is_gap else SEP_H if is_sep else ROW_H
    y_top, y_bot = y, y - h
    y_mid  = (y_top + y_bot) / 2

    if is_sep:
        ax.plot([T_L, T_R], [y_top] * 2, color=GRAY_LINE, lw=1.6)
        ax.plot([T_L, T_R], [y_bot] * 2, color=GRAY_LINE, lw=1.6)
        y = y_bot
        continue

    if is_gap:
        ax.plot([T_L, T_R], [y_top] * 2, color=GRAY_LINE, lw=0.5)
        y = y_bot
        continue

    # Row highlight (S&P 500 level)
    if r.get("hl"):
        ax.add_patch(Rectangle(
            (T_L, y_bot), T_R - T_L, h,
            facecolor=BLUE_LIGHT, edgecolor="none", zorder=0))

    kw = {}
    if r.get("bold"):   kw["fontweight"] = "bold"
    if r.get("italic"): kw["fontstyle"]  = "italic"
    fs = 8.0 if r.get("sm") else 9.0

    ax.text(T_L + 0.16, y_mid, r["lbl"],
            fontsize=fs, va="center", ha="left", color=C_TEXT, **kw)

    for i, (val, cx) in enumerate(zip(r["v"], CX)):
        vkw = dict(kw)
        if i == 0:
            vkw["fontweight"] = "bold"
        ax.text(cx, y_mid, val,
                fontsize=fs, va="center", ha="center", color=C_TEXT, **vkw)

    y = y_bot

# Vertical border lines flanking Baseline column (from header bottom to last row)
rows_bot = y
BL_X_L = CX[0] - COL_W / 2 + 0.04
BL_X_R = CX[0] + COL_W / 2 - 0.04
ax.plot([BL_X_L, BL_X_L], [rows_bot, HDR_BOT], color=GRAY_LINE, lw=0.7, zorder=1)
ax.plot([BL_X_R, BL_X_R], [rows_bot, HDR_BOT], color=GRAY_LINE, lw=0.7, zorder=1)

# ── Footer ────────────────────────────────────────────────────────────────────
ax.plot([T_L, T_R], [rows_bot - 0.05] * 2, color=GRAY_LINE, lw=0.8)
ax.text(T_L + 0.12, rows_bot - 0.20,
        "GS baseline and scenarios reflect total return including dividends.",
        fontsize=7.5, va="center", ha="left", color=C_DIM)
ax.text(T_L + 0.12, rows_bot - 0.40,
        "Source: Goldman Sachs Global Investment Research",
        fontsize=7.5, va="center", ha="left", color=C_DIM, fontstyle="italic")

plt.savefig("sp500_scenarios.png", dpi=200, bbox_inches="tight")
print("Saved sp500_scenarios.png")
plt.show()
