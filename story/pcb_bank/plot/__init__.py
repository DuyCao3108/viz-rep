"""Import every plot topic module so their @register_plot decorators run at
package-import time. Adding a new topic (new file in this dir) requires
exactly one new line here — mirrors src/charts/__init__.py's pattern for
chart shapes."""

# from plot import client
from plot import (
    # quest_1_pt2,
    # quest_1,
    # quest_2_1,
    # quest_2_2,
    # quest_2_3,
    quest_3_1,
    quest_3_2,
)
