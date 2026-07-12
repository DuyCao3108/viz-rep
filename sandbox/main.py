"""Sandbox: same bar chart, same partial config override, two config styles side by side."""
import json
import matplotlib.pyplot as plt

from src.dataclass_approach import Bar as DataclassBar, BarConfig
from src.dict_approach import Bar as DictBar

categories = ["Q1", "Q2", "Q3", "Q4"]
values = [12, 19, 7, 15]

# Only override what we care about: title + hide top/right spines.
# Everything else should fall back to sane defaults.
partial_override = {
    "title": {"text": "Revenue by Quarter"},
    "bar_color": "#2E7D32",
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# --- dataclass approach ---
dc_config = BarConfig.from_dict(partial_override)
DataclassBar(ax1, dc_config).render(categories, values)
ax1.set_title(ax1.get_title() + "\n(dataclass config)")

# --- dict approach ---
DictBar(ax2, partial_override).render(categories, values)
ax2.set_title(ax2.get_title() + "\n(dict config)")

fig.tight_layout()
fig.savefig("sandbox/output/comparison.png")

# JSON round-trip check: dataclass config can serialize/deserialize like a dict config can.
dumped = json.dumps(dc_config.to_dict())
reloaded = BarConfig.from_dict(json.loads(dumped))
assert reloaded == dc_config

print("Saved sandbox/output/comparison.png")
print("dataclass config as dict:", dc_config.to_dict())
print("dict config as merged:", DictBar(ax2, partial_override).config)
