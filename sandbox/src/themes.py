"""
The Economist Design System — colour + typography tokens.
"""

from __future__ import annotations

import colorsys

DS_VERSION = "7.42.1"

# ---------------------------------------------------------------------------
# 1. COLOUR — grouped by collection (as documented under Foundations > Colour)
# ---------------------------------------------------------------------------

COLOR_COLLECTIONS = {
    "brand": {
        "economist-red": {100: "#E3120B", 60: "#F6423C"},  # base has no suffix
    },
    "accent_primary": {
        "chicago": {
            20: "#141F52",
            30: "#1F2E7A",
            45: "#2E45B8",
            55: "#475ED1",
            90: "#D6DBF5",
            95: "#EBEDFA",
        },
    },
    "accent_secondary": {
        "hong-kong": {45: "#1DC9A4", 55: "#36E2BD", 90: "#D2F9F0", 95: "#E9FCF8"},
        "tokyo": {45: "#C91D42", 55: "#E2365B", 90: "#F9D2DB", 95: "#FCE9ED"},
    },
    "accent_tertiary": {
        "singapore": {55: "#F97A1F", 65: "#FB9851", 75: "#FCB583", 90: "#FEE1CD"},
        "new-york": {55: "#F9C31F", 65: "#FBD051", 75: "#FCDE83", 90: "#FEF2CD"},
    },
    "greyscale": {
        "london": {
            5: "#0D0D0D",
            10: "#1A1A1A",
            20: "#333333",
            35: "#595959",
            70: "#B3B3B3",
            85: "#D9D9D9",
            95: "#F2F2F2",
            100: "#FFFFFF",
        },
    },
    "canvas": {
        "los-angeles": {85: "#E1DFD0", 90: "#EBE9E0", 95: "#F5F4EF"},
        "paris": {85: "#D0E1E1", 90: "#E0EBEB", 95: "#EFF5F5"},
    },
    "others": {
        "dark-pink": '#A6438B',
        'dark-orange': '#B02F30',
        'dark-purple': '#7537AD'
    },
    "high-light": {
        "red":"#E3120B",
        "blue":"#141F52"
    }
}


COLOR_THEMES: dict[str, list[str]] = {
    "cate-55": [
        "chicago-20",
        "chicago-55",
        "dark-purple",
        "hong-kong-45",
        "singapore-55",
        "dark-pink",
        "tokyo-45",
        "new-york-55",
        "red",
    ],
    "gradient2-blue": ["chicago-20", "chicago-90"],
    "gradient2-red": ["tokyo-45", "tokyo-90"],
    "diverse-blue-mint": ["chicago-45", "hong-kong-45"],
    "diverse-red-mint": ["tokyo-45", "hong-kong-45"],
}


def get_color_code(name: str) -> str:
    """Resolve a color name (e.g. 'chicago-55', 'dark-pink') to its hex code via COLOR_COLLECTIONS."""
    for collection in COLOR_COLLECTIONS.values():
        value = collection.get(name)
        if isinstance(value, str):
            return value

    family, _, tone = name.rpartition("-")
    if tone.isdigit():
        for collection in COLOR_COLLECTIONS.values():
            shades = collection.get(family)
            if isinstance(shades, dict) and int(tone) in shades:
                return shades[int(tone)]

    raise KeyError(f"unknown color name: {name!r}")


def plot_theme_palette(theme_key: str, save_path: str | None = None):
    """Render a theme's colors as an ordered band of swatches, for checking palette harmony.

    Each swatch is labelled with its token name and hex code, left-to-right in
    the exact order the colors appear in COLOR_THEMES[theme_key].
    """
    import matplotlib.pyplot as plt

    names = COLOR_THEMES[theme_key]
    hexes = [get_color_code(name) for name in names]

    fig, ax = plt.subplots(figsize=(1.4 * len(hexes), 2.2))
    for i, (name, hex_code) in enumerate(zip(names, hexes)):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, facecolor=hex_code, edgecolor="none"))
        ax.text(i + 0.5, -0.12, name, ha="center", va="top", fontsize=8, rotation=0)
        ax.text(i + 0.5, -0.26, hex_code, ha="center", va="top", fontsize=7, color="0.4")

    ax.set_xlim(0, len(hexes))
    ax.set_ylim(-0.4, 1)
    ax.axis("off")
    ax.set_title(theme_key, fontsize=10, loc="left")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300)
    return fig


def make_step(family: str, lightness: int) -> str:
    """Regenerate `family`'s color at an arbitrary HSL lightness (0-100).

    Hue and saturation are read off any one known tone of `family` (they're
    ~constant across a family's published tones) and held fixed; only
    lightness changes. Lets us fill in lightness values the design system
    doesn't publish (e.g. hong-kong only ships 45/55/90/95).
    """
    reference_hex = None
    for collection in COLOR_COLLECTIONS.values():
        value = collection.get(family)
        if isinstance(value, str):
            reference_hex = value
            break
        if isinstance(value, dict) and value:
            reference_hex = next(iter(value.values()))
            break

    if reference_hex is None:
        raise KeyError(f"unknown color family: {family!r}")

    r, g, b = (int(reference_hex.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))
    h, _, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, lightness / 100, s)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def generate_steps(family: str, start: int = 5, stop: int = 95, step: int = 5) -> dict[int, str]:
    """Full lightness ladder for `family`, stepping by `step` from `start` to `stop` (inclusive)."""
    return {l: make_step(family, l) for l in range(start, stop + 1, step)}


def plot_step_palette(family: str, start: int = 5, stop: int = 95, step: int = 5, save_path: str | None = None):
    """Render `family`'s full lightness ladder as a row of labelled swatches."""
    import matplotlib.pyplot as plt

    ladder = generate_steps(family, start, stop, step)

    fig, ax = plt.subplots(figsize=(1.1 * len(ladder), 1.6))
    for i, (lightness, hex_code) in enumerate(ladder.items()):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, facecolor=hex_code, edgecolor="white", linewidth=0.5))
        text_color = "white" if lightness < 50 else "black"
        ax.text(i + 0.5, 0.5, str(lightness), ha="center", va="center", fontsize=7, color=text_color)

    ax.set_xlim(0, len(ladder))
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(family, fontsize=10, loc="left")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300)
    return fig

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


if __name__ == "__main__":
    plot_theme_palette("cate-55",'/Users/caovanduy/dev/libs/viz/sandbox/output/pal.png')
