"""Shape-name registry: every concrete chart class registers against this so
Vizzy can turn a shape name (e.g. "simple_bar") into a class to instantiate."""

from __future__ import annotations

_SHAPE_REGISTRY: dict[str, type] = {}


def register_shape(name: str):
    """Class decorator: @register_shape("simple_bar") on a chart class."""
    def decorator(cls):
        _SHAPE_REGISTRY[name] = cls
        return cls
    return decorator


def get_shape_class(name: str) -> type:
    if name not in _SHAPE_REGISTRY:
        raise ValueError(f"Unknown chart shape {name!r}. Registered: {sorted(_SHAPE_REGISTRY)}")
    return _SHAPE_REGISTRY[name]
