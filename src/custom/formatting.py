"""Data-label/tick formatting tokens/utilities. Pure functions — no chart-class
coupling, same convention as src/custom/colors.py and src/custom/fonts.py.

Scale computation (scale_factor) and string rendering (render_value) are
split apart so a chart can scale a whole array once (Bar.format_measure())
and reuse the exact same rendering logic per-label and per-tick (a
matplotlib FuncFormatter re-renders on every draw, given a raw axis
position — it can't reuse a precomputed array)."""

from __future__ import annotations

import datetime
from typing import Literal

DataLabelFormat = Literal[
    "#", "#,", "#,K", "#,M", "#,B",
    "#.", "#.1", "#.2", "#.3",
    "%.0", "%.1", "%.2", "%.3",
]

DimensionFormat = Literal[
    "yyyy", "yyyy-mm", "yyyy-mm-dd", "yy-mm", "yy-MM", "yy-qq", "yyyy-qq"
]

_SCALE_FACTORS: dict[str, float] = {"#,K": 1_000, "#,M": 1_000_000, "#,B": 1_000_000_000}
_SCALE_LETTERS: dict[str, str] = {"#,K": "K", "#,M": "M", "#,B": "B"}
_UNIT_WORDS: dict[str, str] = {"#,K": "Thousands", "#,M": "Millions", "#,B": "Billions"}


def scale_factor(fmt: DataLabelFormat | None) -> float:
    """Divisor implied by fmt — 1 for non-scaling fmts/None, else 1e3/1e6/1e9."""
    return _SCALE_FACTORS.get(fmt, 1)


def unit_word(fmt: DataLabelFormat | None) -> str | None:
    """"Thousands"/"Millions"/"Billions" for a scaling fmt, else None."""
    return _UNIT_WORDS.get(fmt)


def render_value(
    value: float, fmt: DataLabelFormat | None = None, dedup_unit: bool = False
) -> str:
    """Renders one value that's ALREADY scaled (caller divided by
    scale_factor(fmt) first, if fmt scales). dedup_unit=True omits the K/M/B
    suffix letter (still uses thousand-sep) — for charts that show the unit
    once as a subtitle instead of repeating it on every label/tick."""
    if fmt is None or fmt == "#":
        return f"{value:.0f}"

    if fmt == "#,":
        return f"{round(value):,}"

    if fmt in _SCALE_LETTERS:
        rendered = f"{round(value):,}"
        return rendered if dedup_unit else f"{rendered}{_SCALE_LETTERS[fmt]}"

    if fmt in ("#.", "#.1", "#.2", "#.3"):
        precision = 0 if fmt == "#." else int(fmt[-1])
        return f"{value:.{precision}f}"

    if fmt in ("%.0", "%.1", "%.2", "%.3"):
        precision = int(fmt[-1])
        return f"{value * 100:.{precision}f}%"

    raise ValueError(f"Unknown data label fmt {fmt!r}. Expected one of: {DataLabelFormat}")


def format_value(
    value: float, fmt: DataLabelFormat | None = None, dedup_unit: bool = False
) -> str:
    """One-shot convenience: scale a RAW value then render (scale_factor +
    render_value composed), for callers with no precomputed display array."""
    return render_value(value / scale_factor(fmt), fmt, dedup_unit)


def _format_dimension(value, fmt: DimensionFormat | None = None) -> str:
    """fmt=None: passthrough, str(value) — most dimensions won't declare a
    fmt. Otherwise fmt implies a date bucket; raises TypeError if value isn't
    a date/datetime."""
    if fmt is None:
        return str(value)

    if not isinstance(value, (datetime.date, datetime.datetime)):
        raise TypeError(
            f"format_dimension fmt={fmt!r} requires a date/datetime value, "
            f"got {type(value).__name__}: {value!r}."
        )

    if fmt == "yyyy":
        return value.strftime("%Y")
    if fmt == "yyyy-mm":
        return value.strftime("%Y-%m")
    if fmt == "yyyy-mm-dd":
        return value.strftime("%Y-%m-%d")
    if fmt == "yy-mm":
        return value.strftime("%y-%m")
    if fmt == "yy-MM":
        return value.strftime("%y-%b")
    if fmt == "yy-qq":
        quarter = (value.month - 1) // 3 + 1
        return f"{value.strftime('%y')}-Q{quarter}"
    if fmt == "yyyy-qq":
        quarter = (value.month - 1) // 3 + 1
        return f"{value.strftime('%Y')}-Q{quarter}"

    raise ValueError(f"Unknown dimension fmt {fmt!r}. Expected one of: {DimensionFormat}")
