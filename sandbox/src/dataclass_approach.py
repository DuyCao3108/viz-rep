"""Config-as-dataclass: typed, composable, still JSON-convertible via dataclasses.asdict."""
from dataclasses import dataclass, field, asdict


@dataclass
class SpinesConfig:
    top: bool = False
    right: bool = False
    left: bool = True
    bottom: bool = True


@dataclass
class TitleConfig:
    text: str = ""
    fontsize: int = 14
    color: str = "#222222"


@dataclass
class AxisConfig:
    label: str = ""
    color: str = "#444444"
    show_ticks: bool = True


@dataclass
class BarConfig:
    spines: SpinesConfig = field(default_factory=SpinesConfig)
    title: TitleConfig = field(default_factory=TitleConfig)
    xaxis: AxisConfig = field(default_factory=AxisConfig)
    yaxis: AxisConfig = field(default_factory=AxisConfig)
    bar_color: str = "#4C72B0"

    @classmethod
    def from_dict(cls, d: dict) -> "BarConfig":
        return cls(
            spines=SpinesConfig(**d.get("spines", {})),
            title=TitleConfig(**d.get("title", {})),
            xaxis=AxisConfig(**d.get("xaxis", {})),
            yaxis=AxisConfig(**d.get("yaxis", {})),
            bar_color=d.get("bar_color", "#4C72B0"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


class Bar:
    def __init__(self, ax, config: BarConfig | None = None):
        self.ax = ax
        self.config = config or BarConfig()

    def render(self, categories: list[str], values: list[float]) -> None:
        cfg = self.config
        self.ax.bar(categories, values, color=cfg.bar_color)

        for side, visible in asdict(cfg.spines).items():
            self.ax.spines[side].set_visible(visible)

        self.ax.set_title(cfg.title.text, fontsize=cfg.title.fontsize, color=cfg.title.color)
        self.ax.set_xlabel(cfg.xaxis.label, color=cfg.xaxis.color)
        self.ax.set_ylabel(cfg.yaxis.label, color=cfg.yaxis.color)
        if not cfg.xaxis.show_ticks:
            self.ax.set_xticks([])
        if not cfg.yaxis.show_ticks:
            self.ax.set_yticks([])
