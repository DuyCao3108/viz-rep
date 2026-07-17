"""
The Economist Design System — colour + typography tokens.
"""

from __future__ import annotations

DS_VERSION = "7.42.1"

# ---------------------------------------------------------------------------
# 3. TYPOGRAPHY
# ---------------------------------------------------------------------------

# Font stacks — var() references resolved. Keys map to --ds-type-system-*
FONT_STACKS: dict[str, str] = {
    "serif": "'EconomistSerifOsF', ui-serif, Georgia, Times, 'Times New Roman', serif",
    "serif_smallcaps": "'EconomistSerifSC', 'EconomistSerifOsF', ui-serif, Georgia, Times, 'Times New Roman', serif",
    "serif_lining": "'EconomistSerifLF', 'EconomistSerifOsF', ui-serif, Georgia, Times, 'Times New Roman', serif",
    "sans": "'EconomistSansOsF', system-ui, 'Segoe UI', Helvetica, Arial, sans-serif",
    "sans_smallcaps": "'EconomistSansSC', 'EconomistSansOsF', system-ui, 'Segoe UI', Helvetica, Arial, sans-serif",
    "sans_lining": "'EconomistSansLF', 'EconomistSansOsF', system-ui, 'Segoe UI', Helvetica, Arial, sans-serif",
    "sans_condensed": "'EconomistSansLF', 'EconomistSansOsF', system-ui, 'Segoe UI', Helvetica, Arial, sans-serif",
    "sans_headline": "'EconomistSansHeadline', Impact, Haettenschweiler, 'Franklin Gothic Bold', Charcoal, 'Helvetica Inserat', 'Arial Black', sans-serif",
    "twa": "'TWANeue', Impact, Haettenschweiler, 'Franklin Gothic Bold', Charcoal, 'Helvetica Inserat', 'Arial Black', sans-serif",
    "twa_alt": "'TWANeueAlt', 'TWANeue', Impact, Haettenschweiler, 'Arial Black', sans-serif",
    "twa_rounded": "'TWANeueRounded', 'TWANeue', Impact, Haettenschweiler, 'Arial Black', sans-serif",
    "display": "'Narrowfat', 'TWANeue', Impact, Haettenschweiler, 'Arial Black', sans-serif",
    "display_stencil": "'NarrowfatStencil', 'Narrowfat', 'TWANeue', Impact, 'Arial Black', sans-serif",
    "simplified_chinese": "'PingFang SC', 'Heiti SC', 'Noto Sans CJK', 'DengXian', 'Microsoft JhengHei UI', system-ui, sans-serif",
    "symbols": "'EcoPict'",
    # 1843 sub-brand
    "slab_serif_1843": "'ClarendonSunday', 'ITC Lubalin Graph', Rockwell, serif",
    "slab_serif_lining_1843": "'ClarendonSundayLN', 'ClarendonSunday', 'ITC Lubalin Graph', Rockwell, serif",
}

# Every @font-face shipped: family -> {styles, weights, note}
FONT_FACES: dict[str, dict] = {
    "EconomistSerifOsF": {"styles": ["normal", "italic"], "weights": (300, 900), "note": "body serif, oldstyle figures"},
    "EconomistSerifSC":  {"styles": ["normal", "italic"], "weights": (300, 900), "note": "serif, small caps"},
    "EconomistSerifLF":  {"styles": ["normal", "italic"], "weights": (300, 900), "note": "serif, lining figures (tables/charts)"},
    "EconomistSansOsF":  {"styles": ["normal", "italic"], "weights": (300, 900), "note": "UI sans, oldstyle figures"},
    "EconomistSansSC":   {"styles": ["normal", "italic"], "weights": (300, 900), "note": "sans, small caps"},
    "EconomistSansLF":   {"styles": ["normal", "italic"], "weights": (300, 900), "note": "sans, lining figures (tables/charts)"},
    "EconomistSansHeadline": {"styles": ["normal"], "weights": (400, 900), "note": "headline sans"},
    "TWANeue":        {"styles": ["normal"], "weights": [400, 900], "note": "The World Ahead"},
    "TWANeueAlt":     {"styles": ["normal"], "weights": [400], "note": "The World Ahead, alt"},
    "TWANeueRounded": {"styles": ["normal"], "weights": [400], "note": "The World Ahead, rounded"},
    "Narrowfat":         {"styles": ["normal"], "weights": [400], "note": "display"},
    "NarrowfatStencil":  {"styles": ["normal"], "weights": [400], "note": "display, stencil"},
    "EcoPict":           {"styles": ["normal"], "weights": [400], "note": "pictograms / symbols"},
    "ClarendonSunday":   {"styles": ["normal"], "weights": [300, 500, 700], "note": "1843 slab serif"},
    "ClarendonSundayLN": {"styles": ["normal"], "weights": [300, 500, 700], "note": "1843 slab, lining figures"},
}
# NB: all Economist* faces are variable fonts (weight is a 300–900 range).

# Modular type scale: token index -> (rem, px)
TYPE_SCALE: dict[int, tuple[float, int]] = {
    -2: (0.8125, 13), -1: (0.9375, 15), 0: (1.0625, 17), 1: (1.25, 20),
    2: (1.4375, 23), 3: (1.625, 26), 4: (1.875, 30), 5: (2.125, 34),
    6: (2.5, 40), 7: (2.875, 46), 8: (3.25, 52), 9: (3.75, 60),
    10: (4.25, 68), 11: (5.0, 80), 12: (5.75, 92),
}
TYPE_SCALE_PX: list[int] = [px for _, px in TYPE_SCALE.values()]

LEADING: dict[str, float] = {
    "lower": 1.4,          # body copy
    "upper": 1.18,         # headlines
    "border_link": 1.125,  # non-wrapping links w/ bottom border
    "upper_1843": 1.1,
}

# Practical substitutes — the real webfonts are licensed and not installable
# in Power BI / matplotlib. These are the closest freely available matches.
FONT_FALLBACK_POWERBI: dict[str, str] = {
    "serif": "Georgia",
    "sans": "Segoe UI",
    "sans_lining": "Segoe UI",     # use for axis/data labels (lining figures)
    "sans_headline": "Impact",
    "mono_numbers": "Consolas",
}


def resolve_installed_font(*names: str) -> str:
    """Return the first font in `names` actually installed on this machine.

    `FONT_FALLBACK_POWERBI` targets Windows/Power BI (e.g. "Segoe UI"), which
    isn't installed on macOS/Linux. Passing that name straight to matplotlib
    per-draw (e.g. via `tick_params(labelfontfamily=...)`) makes it re-probe
    and warn ("findfont: ... not found") on every text artist it rasterizes.
    Resolving once here, at import time, avoids that: matplotlib's own
    multi-name fallback search is silent, it's only single missing names
    handed to a live draw call that warn.
    """
    import matplotlib.font_manager as fm

    path = fm.findfont(fm.FontProperties(family=list(names)))
    return fm.get_font(path).family_name


if __name__ == "__main__":
    pass
