"""Import every chart shape module so their @register_shape decorators run
at package-import time. Adding a new shape family (new file in this dir)
requires exactly one new line here — this is the sole edit needed to make
Vizzy aware of a new shape without touching vizzy.py's dispatch logic."""

from src.charts import bar, line  # noqa: F401
