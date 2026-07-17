"""Aggregates every chart family's scenario list into one registry that
tests/gallery/run.py iterates. Add a new chart family (e.g. special.py
shapes) by importing its SCENARIOS list here and folding it into
ALL_SCENARIOS."""

from .bar_scenarios import SCENARIOS as _BAR_SCENARIOS
from .line_scenarios import SCENARIOS as _LINE_SCENARIOS

ALL_SCENARIOS: list[tuple[str, object]] = [*_BAR_SCENARIOS, *_LINE_SCENARIOS]
