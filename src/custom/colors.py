"""
The Economist Design System — colour + typography tokens.
"""

from __future__ import annotations

import colorsys
from typing import Literal

DS_VERSION = "7.42.1"

# ---------------------------------------------------------------------------
# 1. COLOUR — flat name -> {"code": hex, "default_step": int | None}
#
#    `code` is the reference hex a name's HSL step ladder is derived from.
#    `default_step`, if set, is the lightness step used when a theme
#    references the bare name (no "-NN" suffix). Names without a
#    `default_step` resolve to their raw `code` when referenced bare.
# ---------------------------------------------------------------------------

COLOR_DICTS: dict[str, dict] = {
    # steppable families — reference hex is that family's previous "50" tone
    "chicago": {"code": "#324DCD", "default_step": 50},
    "hong-kong": {"code": "#20DFB6", "default_step": 50},
    "tokyo": {"code": "#DF2049", "default_step": 50},
    "singapore": {"code": "#F86C07", "default_step": 50},
    "new-york": {"code": "#F8BC07", "default_step": 50},
    "london": {"code": "#808080", "default_step": 50},
    "los-angeles": {"code": "#9C9563", "default_step": 50},
    "paris": {"code": "#639C9C", "default_step": 50},
    # flat / brand colors — bare name returns raw code, "-NN" still steppable on demand
    "economist-red": {"code": "#E3120B"},
    "dark-pink": {"code": "#A6438B"},
    "dark-orange": {"code": "#B02F30"},
    "dark-purple": {"code": "#7537AD"},
    "red": {"code": "#E3120B"},
    "blue": {"code": "#141F52"},
    "mint": {'code':'#A5D7E8'},
    "yellow": {'code':'#FEC260'},
    # hcvn set
    "hcvn-red1": {"code": "#FF204E"},
    "hcvn-red2": {"code": "#A0153E"},
    "hcvn-red3": {"code": "#5D0E41"},
    "hcvn-dark-grey": {"code": "#00224D"},
    # bar
    "bar1": {"code": "#121358"},
    "bar2": {"code": "#232F72"},
    "bar3": {"code": "#2F578A"},
    "bar4": {"code": "#36ADA3"},
    # tableau
    "tab1": {"code": "#C81D25"},
    "tab2": {"code": "#FF5A5F"},
    "tab3": {"code": "#381859"},
    "tab4": {"code": "#087E8D"},
    "tab5": {"code": "#0B3954"},
    # PowerBI Default by Ken Flerlage
    "verditer": {"code": "#01B8AA"},
    "gale-force": {"code": "#374649"},
    "pineapple-salmon": {"code": "#FD625E"},
    "egg-toast": {"code": "#F2C80F"},
    "king-creek-falls": {"code": "#5F6B6D"},
    "anakiwa": {"code": "#8AD4EB"},
    "atomic-tangerine": {"code": "#FE9666"},
    "iris-orchid": {"code": "#A66999"},
    "sports-blue": {"code": "#3599B8"},
    "soft-blush": {"code": "#DFBDBF"},
    # GoodDashBoard by Anil Sidhwani
    "smudged-lips": {"code": "#EE4266"},
    "lamplight": {"code": "#FFD23F"},
    "resonant-blue": {"code": "#00A5CF"},
    "jadeite": {"code": "#3BCEAC"},
    "secret-garden": {"code": "#0EAD69"},
    "god-of-nights": {"code": "#540D6E"},
}

Pal = Literal[
    "cate-55",
    "cate-30",
    "cate-25",
    "gradient2-blue",
    "gradient2-red",
    "diverse-blue-mint",
    "diverse-red-mint",
    "step5-red",
    "step5-blue",
    "bar",
    "tab",
    "powerbi",
    "powerbi-2",
    "gooddashboard",
]

COLOR_THEMES: dict[str, list[str]] = {
    "tab": [
        "tab1",
        "tab2",
        "tab3",
        "tab4",
        "tab5",
    ],
    "bar": [
        "bar1",
        "bar2",
        "bar3",
        "bar4",
    ],
    "cate-55": [
        "chicago-55",
        "yellow-55",
        "hcvn-red2-55",
        'hong-kong-55',
        "mint-55",
        "hcvn-dark-grey-55"
    ],
    "cate-30": [
        "chicago-40",
        "hcvn-red2-40",
        "yellow-40",
        'hong-kong-40',
        "mint-40",
        "hcvn-dark-grey-40"
    ],
    "cate-25": [
        "chicago-35",
        "hcvn-red2-35",
        "yellow-35",
        'hong-kong-35',
        "mint-35",
        "hcvn-dark-grey-35"
    ],
    "cate-55-old": [
        "chicago-20",
        "chicago-50",
        "chicago-80",
        "dark-purple",
        "hong-kong-35",
        "singapore-45",
        "tokyo-35",
        "red",
        "new-york-50",
        "dark-pink",
    ],
    "step5-blue": [
        "chicago-50",
        "chicago-20",
        "chicago-80",
        "hong-kong-30",
    ],
    "step5-red": [
        "hcvn-red1",
        "hcvn-red2",
        "hcvn-red3",
        "hcvn-dark-grey",
    ],
    "gradient2-blue": ["chicago-30", "chicago-90"],
    "gradient2-red": ["tokyo-45", "tokyo-90"],
    "diverse-blue-mint": ["chicago-30", "hong-kong-45"],
    "diverse-red-mint": ["tokyo-45", "hong-kong-45"],
    "powerbi": [
        "verditer-35",
        "gale-force",
        "pineapple-salmon-40",
        "hcvn-dark-grey",
        # "chicago-55",
        "iris-orchid-40",
        "egg-toast-40",
        "king-creek-falls-40",
        "atomic-tangerine-40",
        "sports-blue-40",
        "soft-blush-40",
    ],
    "powerbi-2": [
        "chicago-30",
        "verditer-35",
        "egg-toast-40",
        "gale-force",
        "iris-orchid-40",
        "king-creek-falls-40",
        "pineapple-salmon-40",
        "hcvn-dark-grey",
        "atomic-tangerine-40",
        "sports-blue-40",
        "soft-blush-40",
    ],
    "gooddashboard": [
        "smudged-lips",
        "lamplight",
        "resonant-blue",
        "jadeite",
        "secret-garden",
        "god-of-nights",
    ],
}


def _parse_flexible_name(flexible_name: str) -> tuple[str, int | None]:
    """Split a flexible-color-name into (base_name, step).

    A trailing "-NN" is treated as a step only if NN is all-digits and a
    multiple of 5 in [5, 90]; otherwise the whole string is the base name.
    """
    base_name, sep, tail = flexible_name.rpartition("-")
    if sep and tail.isdigit():
        step = int(tail)
        if step % 5 == 0 and 5 <= step <= 90:
            return base_name, step
    return flexible_name, None


def _step_color(reference_hex: str, lightness: int) -> str:
    """Regenerate `reference_hex` at an arbitrary HSL lightness (0-100).

    Hue and saturation are read off `reference_hex` and held fixed; only
    lightness changes.
    """
    r, g, b = (int(reference_hex.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))
    h, _, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, lightness / 100, s)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def get_color_code(flexible_name: str) -> str:
    """Resolve a flexible-color-name (e.g. 'chicago-55', 'dark-pink') to its hex code."""
    base_name, step = _parse_flexible_name(flexible_name)
    entry = COLOR_DICTS.get(base_name)
    if entry is None:
        raise KeyError(f"unknown color name: {flexible_name!r}")

    step = step if step is not None else entry.get("default_step")
    return entry["code"] if step is None else _step_color(entry["code"], step)


def get_theme_colors(theme_name: str) -> list[str]:
    """Resolve every color name in a COLOR_THEMES entry to its hex code."""
    return [get_color_code(name) for name in COLOR_THEMES[theme_name]]


def describe_theme(theme_name: str) -> list[tuple[str, int | None]]:
    """List each theme entry's (base_name, effective step) — None means raw code, no stepping."""
    result = []
    for name in COLOR_THEMES[theme_name]:
        base_name, step = _parse_flexible_name(name)
        if step is None:
            step = COLOR_DICTS[base_name].get("default_step")
        result.append((base_name, step))
    return result


def make_step(name: str, lightness: int) -> str:
    """Regenerate `name`'s color at an arbitrary HSL lightness (0-100)."""
    entry = COLOR_DICTS.get(name)
    if entry is None:
        raise KeyError(f"unknown color name: {name!r}")
    return _step_color(entry["code"], lightness)


def generate_steps(
    name: str, start: int = 5, stop: int = 95, step: int = 5
) -> dict[int, str]:
    """Full lightness ladder for `name`, stepping by `step` from `start` to `stop` (inclusive)."""
    return {l: make_step(name, l) for l in range(start, stop + 1, step)}


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
        ax.text(
            i + 0.5, -0.26, hex_code, ha="center", va="top", fontsize=7, color="0.4"
        )

    ax.set_xlim(0, len(hexes))
    ax.set_ylim(-0.4, 1)
    ax.axis("off")
    ax.set_title(theme_key, fontsize=10, loc="left")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300)
    return fig


def plot_step_palette(
    name: str,
    start: int = 5,
    stop: int = 95,
    step: int = 5,
    save_path: str | None = None,
):
    """Render `name`'s full lightness ladder as a row of labelled swatches."""
    import matplotlib.pyplot as plt

    ladder = generate_steps(name, start, stop, step)

    fig, ax = plt.subplots(figsize=(1.1 * len(ladder), 1.6))
    for i, (lightness, hex_code) in enumerate(ladder.items()):
        ax.add_patch(
            plt.Rectangle(
                (i, 0), 1, 1, facecolor=hex_code, edgecolor="white", linewidth=0.5
            )
        )
        text_color = "white" if lightness < 50 else "black"
        ax.text(
            i + 0.5,
            0.5,
            str(lightness),
            ha="center",
            va="center",
            fontsize=7,
            color=text_color,
        )

    ax.set_xlim(0, len(ladder))
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(name, fontsize=10, loc="left")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300)
    return fig


if __name__ == "__main__":
    pass
