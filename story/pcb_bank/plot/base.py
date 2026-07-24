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

    FIG_SIZE convention: a chart meant to stand alone (a single-image row in
    an insight_outline.txt) should use FIG_SIZE width 16 (e.g. quest_1.py's
    FIG_SIZE=(16, 8)). A chart meant for an n-way "|"-split outline row
    should use width 16/n (e.g. quest_2_2.py/quest_2_3.py's
    FIG_SIZE=(16/2, ...)) — keeps font/line proportions visually consistent
    whether the chart is viewed standalone or side-by-side. Guidance only,
    not enforced: FIG_SIZE is chosen before a plot function is even
    registered, so this can't be checked here.
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
