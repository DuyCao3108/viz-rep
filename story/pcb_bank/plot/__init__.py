"""Import every plot topic module so their @register_plot decorators run at
package-import time. Adding a new topic (new file in this dir) requires
exactly one new line here — mirrors src/charts/__init__.py's pattern for
chart shapes."""

from plot import pcb
