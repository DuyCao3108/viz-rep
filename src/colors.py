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
            5: "#050814",
            10: "#0A0F29",
            15: "#0F173E",
            20: "#141F52",
            25: "#192766",
            30: "#1F2E7A",
            35: "#233690",
            40: "#283EA4",
            45: "#2E45B8",
            50: "#324DCD",
            55: "#475ED1",
            60: "#5B71D7",
            65: "#7083DC",
            70: "#8494E1",
            75: "#98A6E6",
            80: "#ADB8EB",
            85: "#C1CAF0",
            90: "#D6DBF5",
            95: "#EBEDFA",
        },
    },
    "accent_secondary": {
        "hong-kong": {
            5: "#031612",
            10: "#062D24",
            15: "#0A4337",
            20: "#0D5949",
            25: "#106F5B",
            30: "#13866D",
            35: "#179C7F",
            40: "#1AB291",
            45: "#1DC9A4",
            50: "#20DFB6",
            55: "#36E2BD",
            60: "#4DE5C4",
            65: "#63E8CC",
            70: "#79ECD3",
            75: "#90EFDA",
            80: "#A6F2E2",
            85: "#BCF5E9",
            90: "#D2F9F0",
            95: "#E9FCF8",
        },
        "tokyo": {
            5: "#160307",
            10: "#2D060F",
            15: "#430A16",
            20: "#590D1D",
            25: "#6F1025",
            30: "#86132C",
            35: "#9C1733",
            40: "#B21A3B",
            45: "#C91D42",
            50: "#DF2049",
            55: "#E2365B",
            60: "#E54D6E",
            65: "#E86380",
            70: "#EC7992",
            75: "#EF90A4",
            80: "#F2A6B6",
            85: "#F5BCC8",
            90: "#F9D2DB",
            95: "#FCE9ED",
        },
    },
    "accent_tertiary": {
        "singapore": {
            5: "#190B01",
            10: "#321601",
            15: "#4B2002",
            20: "#632B03",
            25: "#7C3603",
            30: "#954104",
            35: "#AE4B05",
            40: "#C75605",
            45: "#E06106",
            50: "#F86C07",
            55: "#F97A1F",
            60: "#FA8938",
            65: "#FB9851",
            70: "#FBA76A",
            75: "#FCB583",
            80: "#FCC49C",
            85: "#FDD3B4",
            90: "#FEE1CD",
            95: "#FEF0E6",
        },
        "new-york": {
            5: "#191301",
            10: "#322601",
            15: "#4B3902",
            20: "#634B03",
            25: "#7C5E03",
            30: "#957104",
            35: "#AE8405",
            40: "#C79705",
            45: "#E0AA06",
            50: "#F8BC07",
            55: "#F9C31F",
            60: "#FACA38",
            65: "#FBD051",
            70: "#FBD76A",
            75: "#FCDE83",
            80: "#FCE49C",
            85: "#FDEBB4",
            90: "#FEF2CD",
            95: "#FEF8E6",
        },
    },
    "greyscale": {
        "london": {
            5: "#0D0D0D",
            10: "#1A1A1A",
            15: "#262626",
            20: "#333333",
            25: "#404040",
            30: "#4C4C4C",
            35: "#595959",
            40: "#666666",
            45: "#737373",
            50: "#808080",
            55: "#8C8C8C",
            60: "#999999",
            65: "#A6A6A6",
            70: "#B3B3B3",
            75: "#BFBFBF",
            80: "#CCCCCC",
            85: "#D9D9D9",
            90: "#E6E6E6",
            95: "#F2F2F2",
            100: "#FFFFFF",
        },
    },
    "canvas": {
        "los-angeles": {
            5: "#100F0A",
            10: "#1F1E14",
            15: "#2F2D1E",
            20: "#3E3C28",
            25: "#4E4B32",
            30: "#5D593C",
            35: "#6D6846",
            40: "#7D774F",
            45: "#8C8659",
            50: "#9C9563",
            55: "#A6A073",
            60: "#B0AA82",
            65: "#B9B592",
            70: "#C3BFA2",
            75: "#CDCAB1",
            80: "#D7D5C1",
            85: "#E1DFD0",
            90: "#EBE9E0",
            95: "#F5F4EF",
        },
        "paris": {
            5: "#0A1010",
            10: "#141F1F",
            15: "#1E2F2F",
            20: "#283E3E",
            25: "#324E4E",
            30: "#3C5D5D",
            35: "#466D6D",
            40: "#4F7D7D",
            45: "#598C8C",
            50: "#639C9C",
            55: "#73A6A6",
            60: "#82B0B0",
            65: "#92B9B9",
            70: "#A2C3C3",
            75: "#B1CDCD",
            80: "#C1D7D7",
            85: "#D0E1E1",
            90: "#E0EBEB",
            95: "#EFF5F5",
        },
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
        "chicago-55",
        "chicago-20",
        "dark-purple",
        "hong-kong-35",
        "singapore-45",
        "tokyo-35",
        "red",
        "new-york-50",
        "dark-pink",
    ],
    "gradient2-blue": ["chicago-20", "chicago-90"],
    "gradient2-red": ["tokyo-45", "tokyo-90"],
    "diverse-blue-mint": ["chicago-45", "hong-kong-45"],
    "diverse-red-mint": ["tokyo-45", "hong-kong-45"],
}

def get_theme_colors(theme_name: str) -> list[str]:
    """Resolve every color name in a COLOR_THEMES entry to its hex code."""
    return [get_color_code(name) for name in COLOR_THEMES[theme_name]]

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

if __name__ == "__main__":
    pass
