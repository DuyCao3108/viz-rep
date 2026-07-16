"""Shared base for every chart shape (Bar, Line, and future shapes). Owns
style construction, the common post-hoc mutator interface Artist delegates
to, and the shape-name registry."""

from __future__ import annotations

import matplotlib.pyplot as plt

from src import colors as cl
from src.styles import DefaultStyle


class ChartShape:
    """Base class for one chart shape drawn onto exactly one caller-supplied Axes.

    Construction only sets up styling (DefaultStyle) — no data is drawn yet.
    Concrete subclasses implement `plot(categories, values, legend_categories=None)`
    to actually draw, which Vizzy calls after querying the Dataset.
    """

    def __init__(self, fig: plt.Figure, ax: plt.Axes, theme: str = "cate-55") -> None:
        self.fig = fig
        self.ax = ax
        self.style = DefaultStyle(ax=self.ax, theme_colors=cl.get_theme_colors(theme))
        self._series_artists: dict = {}  # key -> matplotlib artist(s), set by .plot()

    def plot(self, categories: list, values, legend_categories: list | None = None):
        raise NotImplementedError

    # --- common mutator interface (called by Artist; geometry-agnostic parts
    # implemented here, geometry-specific parts delegate to subclass hooks) ---
    def set_theme(self, theme: str) -> "ChartShape":
        self.style.theme_colors = cl.get_theme_colors(theme)
        from cycler import cycler
        self.ax.set_prop_cycle(cycler(color=self.style.theme_colors))
        self._recolor_series()
        return self

    def set_series_color(self, key, color) -> "ChartShape":
        if key not in self._series_artists:
            raise KeyError(f"Unknown series {key!r}. Known: {sorted(self._series_artists, key=str)}")
        self._set_artist_color(self._series_artists[key], color)
        self.style._set_legends()
        return self

    def show_legend(self, show: bool = True) -> "ChartShape":
        self.style.show_legend = show
        self.style._set_legends()
        return self

    def set_title(self, text: str) -> "ChartShape":
        self.style._set_mes_axis_title(text)
        return self

    def show_data_label(self, fmt=None, show: bool = True) -> "ChartShape":
        if fmt is not None:
            self.style.data_label_fmt = fmt
        (self._draw_data_labels if show else self._clear_data_labels)()
        return self

    # --- subclass hooks (geometry-specific) ---
    def _recolor_series(self) -> None:
        for i, key in enumerate(self._series_artists):
            self._set_artist_color(self._series_artists[key], self._resolve_positional_color(i))

    def _resolve_positional_color(self, index: int) -> str:
        return self.style.theme_colors[index % len(self.style.theme_colors)]

    def _set_artist_color(self, artist, color) -> None:
        raise NotImplementedError

    def _draw_data_labels(self) -> None:
        raise NotImplementedError

    def _clear_data_labels(self) -> None:
        raise NotImplementedError


_SHAPE_REGISTRY: dict[str, type] = {}


def register_shape(name: str):
    """Class decorator: @register_shape("simple_bar") on a ChartShape subclass."""
    def decorator(cls):
        _SHAPE_REGISTRY[name] = cls
        return cls
    return decorator


def get_shape_class(name: str) -> type:
    if name not in _SHAPE_REGISTRY:
        raise ValueError(f"Unknown chart shape {name!r}. Registered: {sorted(_SHAPE_REGISTRY)}")
    return _SHAPE_REGISTRY[name]
