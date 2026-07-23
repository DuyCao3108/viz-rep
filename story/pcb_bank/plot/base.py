"""Topic-name registry: every plot function registers against this so main.py
can discover and call all of them without knowing their names in advance."""

from __future__ import annotations

from typing import Callable

from matplotlib.figure import Figure

_PLOT_REGISTRY: dict[str, dict[str, Callable[..., Figure]]] = {}


def register_plot(topic: str):
    """Function decorator: @register_plot("client") on a plot function.

    Registers under `topic`, keyed by the function's own name — main.py uses
    that name as the output filename: output/<topic>/<func_name>.png.
    """
    def decorator(func):
        topic_funcs = _PLOT_REGISTRY.setdefault(topic, {})
        if func.__name__ in topic_funcs:
            raise ValueError(f"Duplicate plot {func.__name__!r} under topic {topic!r}")
        topic_funcs[func.__name__] = func
        return func
    return decorator


def get_registered_plots() -> dict[str, dict[str, Callable[..., Figure]]]:
    return _PLOT_REGISTRY
