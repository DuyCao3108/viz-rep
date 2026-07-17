"""Line-family gallery scenarios.

Each entry is (name, build_fn) where build_fn(fig, ax) -> None builds a
Dataset, constructs a Vizzy(fig, ax, dataset), and calls .line(...) (plus any
Artist mutations) to draw one scenario. Name scenarios after design.txt's
taxonomy, e.g. "line/simple_line_basic", "line/multi_line_with_legend".

Stub only — empty until the first line scenarios are written.
"""

SCENARIOS: list[tuple[str, object]] = []
