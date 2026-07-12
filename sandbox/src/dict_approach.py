"""Config-as-dict: raw JSON-shaped config, merged over a default. No schema to maintain."""

DEFAULT_CONFIG = {
    "spines": {"top": False, "right": False, "left": True, "bottom": True},
    "title": {"text": "", "fontsize": 14, "color": "#222222"},
    "xaxis": {"label": "", "color": "#444444", "show_ticks": True},
    "yaxis": {"label": "", "color": "#444444", "show_ticks": True},
    "bar_color": "#4C72B0",
}


def deep_merge(base: dict, overrides: dict) -> dict:
    merged = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class Bar:
    def __init__(self, ax, config: dict | None = None):
        self.ax = ax
        self.config = deep_merge(DEFAULT_CONFIG, config or {})

    def render(self, categories: list[str], values: list[float]) -> None:
        cfg = self.config
        self.ax.bar(categories, values, color=cfg["bar_color"])

        for side, visible in cfg["spines"].items():
            self.ax.spines[side].set_visible(visible)

        title = cfg["title"]
        self.ax.set_title(title["text"], fontsize=title["fontsize"], color=title["color"])
        self.ax.set_xlabel(cfg["xaxis"]["label"], color=cfg["xaxis"]["color"])
        self.ax.set_ylabel(cfg["yaxis"]["label"], color=cfg["yaxis"]["color"])
        if not cfg["xaxis"]["show_ticks"]:
            self.ax.set_xticks([])
        if not cfg["yaxis"]["show_ticks"]:
            self.ax.set_yticks([])
