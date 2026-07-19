"""register_shape/get_shape_class round-trip, unknown name -> ValueError."""

import pytest

import src.charts  # noqa: F401 — runs every @register_shape decorator
from src.charts.bar import SimpleBarH, SimpleBarV, StackBarH, StackBarV
from src.charts.base import get_shape_class


@pytest.mark.parametrize(
    "name, expected_cls",
    [
        ("simple_bar", SimpleBarV),
        ("h_simple_bar", SimpleBarH),
        ("stack_bar", StackBarV),
        ("h_stack_bar", StackBarH),
    ],
)
def test_get_shape_class_resolves_registered_name(name, expected_cls):
    assert get_shape_class(name) is expected_cls


def test_get_shape_class_unknown_name_raises_value_error():
    with pytest.raises(ValueError):
        get_shape_class("not_a_real_shape")
