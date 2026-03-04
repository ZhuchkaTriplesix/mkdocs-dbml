"""Tests for theme config."""

import pytest
from mkdocs_dbml_plugin.config import get_theme_colors, THEMES


def test_get_theme_colors_returns_dict():
    colors = get_theme_colors("default")
    assert isinstance(colors, dict)
    assert "gradient_start" in colors
    assert "gradient_end" in colors
    assert "line_color" in colors
    assert "bg_color" in colors
    assert "border_color" in colors


def test_all_themes_have_required_keys():
    required = {"gradient_start", "gradient_end", "line_color", "bg_color", "border_color"}
    for name, theme in THEMES.items():
        assert set(theme.keys()) == required, f"Theme {name!r} missing keys"


def test_black_theme_is_dark():
    colors = get_theme_colors("black")
    assert colors["bg_color"] == "#000000"
    assert colors["line_color"] == "#ffffff"


def test_unknown_theme_falls_back_to_default():
    colors = get_theme_colors("nonexistent")
    assert colors == THEMES["default"]
