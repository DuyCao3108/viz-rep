"""Data-label formatting tokens/utilities. Pure functions — no chart-class
coupling, same convention as src/custom/colors.py and src/custom/fonts.py."""

from __future__ import annotations

from typing import Literal

DataLabelFormat = Literal[
    "whole-k", "whole-m", "whole-b",
    "whole-k-thsep", "whole-m-thsep", "whole-b-thsep",
    "whole-thsep",
    "%.2", "%.3",
]

_SCALE_SUFFIXES: dict[str, float] = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}


def format_value(value: float, fmt: DataLabelFormat | None = None) -> str:
    """Format one data-label value per the `DataLabelFormat` token set.

    fmt=None: whole number, no scaling, no separator (f"{value:.0f}").
    """
    if fmt is None:
        return f"{value:.0f}"

    if fmt == "whole-thsep":
        return f"{round(value):,}"

    if fmt in ("%.2", "%.3"):
        precision = int(fmt[-1])
        return f"{value * 100:.{precision}f}%"

    suffix, _, rest = fmt.removeprefix("whole-").partition("-")
    if suffix in _SCALE_SUFFIXES:
        scaled = round(value / _SCALE_SUFFIXES[suffix])
        rendered_suffix = suffix.upper()
        return f"{scaled:,}{rendered_suffix}" if rest == "thsep" else f"{scaled}{rendered_suffix}"

    raise ValueError(f"Unknown data label fmt {fmt!r}. Expected one of: {DataLabelFormat}")
