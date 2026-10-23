"""Semantics and keyboard reachability."""

from __future__ import annotations


def test_svg_has_role_and_label(wrapper):
    svg = wrapper.locator(".dbml-diagram")
    assert svg.get_attribute("role") == "img"
    assert svg.get_attribute("aria-label") == "Database diagram with 3 tables"


def test_tables_are_focusable_and_named(wrapper):
    tables = wrapper.locator(".dbml-table-group")
    for i in range(tables.count()):
        t = tables.nth(i)
        assert t.get_attribute("tabindex") == "0"
        assert t.get_attribute("aria-label").startswith("Table ")


def test_all_buttons_have_accessible_names(wrapper):
    buttons = wrapper.locator("button")
    assert buttons.count() == 6
    for i in range(buttons.count()):
        assert buttons.nth(i).get_attribute("aria-label")


def test_wrapper_is_keyboard_focusable(wrapper):
    assert wrapper.get_attribute("tabindex") == "0"


def test_text_contrast_of_table_titles_is_sufficient(wrapper):
    # `black` theme: white title on a near-black gradient
    ratio = wrapper.locator(".dbml-table-group").first.evaluate(
        """el => {
            const rgb = s => s.match(/\\d+/g).slice(0, 3).map(Number);
            const lum = c => { const [r, g, b] = c.map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
            const title = rgb(getComputedStyle(el.querySelector('.dbml-table-title')).fill);
            const stop = rgb(getComputedStyle(el.querySelector('stop')).stopColor);
            const [a, b] = [lum(title), lum(stop)].sort((x, y) => y - x);
            return (a + 0.05) / (b + 0.05);
        }"""
    )
    assert ratio >= 4.5
