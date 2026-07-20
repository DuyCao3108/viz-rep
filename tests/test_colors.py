import pytest

from src.custom.colors import (
    COLOR_DICTS,
    _parse_flexible_name,
    describe_theme,
    get_color_code,
    get_theme_colors,
)


def test_parse_flexible_name_with_valid_step():
    assert _parse_flexible_name("chicago-20") == ("chicago", 20)
    assert _parse_flexible_name("chicago-90") == ("chicago", 90)


def test_parse_flexible_name_without_suffix():
    assert _parse_flexible_name("dark-pink") == ("dark-pink", None)


@pytest.mark.parametrize(
    "name",
    [
        "chicago-23",  # not a multiple of 5
        "chicago-95",  # out of range
        "chicago-0",  # out of range
        "hcvn-red1",  # trailing digits aren't a standalone step token
    ],
)
def test_parse_flexible_name_invalid_suffix_falls_back_to_whole_name(name):
    assert _parse_flexible_name(name) == (name, None)


def test_get_color_code_bare_name_with_default_step_is_regenerated():
    assert get_color_code("chicago") == get_color_code("chicago-50")
    assert COLOR_DICTS["chicago"]["default_step"] == 50


def test_get_color_code_bare_name_without_default_step_is_raw_code():
    assert get_color_code("dark-pink") == COLOR_DICTS["dark-pink"]["code"]


def test_get_color_code_explicit_step_overrides_default():
    assert get_color_code("chicago-20") != get_color_code("chicago-50")
    assert get_color_code("chicago-20") == get_color_code("chicago-20")


def test_get_color_code_unknown_name_raises_key_error():
    with pytest.raises(KeyError):
        get_color_code("not-a-real-color")


def test_get_theme_colors_resolves_full_theme():
    colors = get_theme_colors("cate-55")
    assert len(colors) == 10
    assert all(c.startswith("#") for c in colors)


def test_describe_theme_reports_base_name_and_effective_step():
    described = describe_theme("cate-55")
    assert ("chicago", 20) in described
    assert ("dark-purple", None) in described  # flat color, no default_step
    assert ("new-york", 50) in described  # explicit -50 suffix
