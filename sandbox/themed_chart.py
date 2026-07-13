import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from main import generate_mock_data
from src.themes import COLOR_COLLECTIONS, COLOR_THEMES


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


def get_theme_colors(theme_name: str) -> list[str]:
    """Resolve every color name in a COLOR_THEMES entry to its hex code."""
    return [get_color_code(name) for name in COLOR_THEMES[theme_name]]


periods, sectors, values = generate_mock_data()

theme = get_theme_colors("cate-55")

fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(periods))
x_smooth = np.linspace(x.min(), x.max(), 300)
for i, sector in enumerate(sectors):
    spline = make_interp_spline(x, values[:, i], k=3)
    ax.plot(x_smooth, spline(x_smooth), color=theme[i], label=sector, linewidth=2.5)



ax.set_xticks(x, periods)
ax.legend(loc='upper left')
fig.savefig("output/main.png", dpi=500)
