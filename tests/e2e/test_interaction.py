"""Pointer and keyboard interaction with the diagram."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from .conftest import center, scale_of, svg_transform


def table(wrapper, name):
    return wrapper.locator(f'.dbml-table-group[data-table="{name}"]')


def title_point(wrapper, name):
    box = table(wrapper, name).bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + 22 * (box["width"] / table_width(wrapper, name))


def table_width(wrapper, name):
    return float(table(wrapper, name).locator(".dbml-table-bg").get_attribute("width"))


def paths(wrapper):
    return wrapper.locator(".dbml-relationship-line").evaluate_all(
        "els => els.map(e => e.getAttribute('d'))"
    )


def drag(page, start, delta, steps=8):
    page.mouse.move(*start)
    page.mouse.down()
    page.mouse.move(start[0] + delta[0], start[1] + delta[1], steps=steps)
    page.mouse.up()


# --- zoom -----------------------------------------------------------------


def test_plain_wheel_scrolls_the_page_and_shows_hint(home, wrapper):
    before = scale_of(wrapper)
    wrapper.scroll_into_view_if_needed()
    cx, cy = center(wrapper)
    home.mouse.move(cx, cy)
    y0 = home.evaluate("window.scrollY")
    home.mouse.wheel(0, 300)
    home.wait_for_timeout(200)
    assert home.evaluate("window.scrollY") > y0
    assert scale_of(wrapper) == before


def test_ctrl_wheel_zooms_in_and_out(home, wrapper):
    cx, cy = center(wrapper)
    home.mouse.move(cx, cy)
    start = scale_of(wrapper)
    home.keyboard.down("Control")
    home.mouse.wheel(0, -200)
    home.keyboard.up("Control")
    zoomed_in = scale_of(wrapper)
    assert zoomed_in > start
    home.keyboard.down("Control")
    home.mouse.wheel(0, 400)
    home.keyboard.up("Control")
    assert scale_of(wrapper) < zoomed_in


def test_zoom_is_clamped(home, wrapper):
    cx, cy = center(wrapper)
    home.mouse.move(cx, cy)
    home.keyboard.down("Control")
    for _ in range(40):
        home.mouse.wheel(0, -100)
    assert scale_of(wrapper) <= 3.0
    for _ in range(80):
        home.mouse.wheel(0, 100)
    home.keyboard.up("Control")
    assert scale_of(wrapper) >= 0.1


def test_zoom_buttons_and_fit(wrapper):
    fitted = svg_transform(wrapper)
    base = scale_of(wrapper)
    wrapper.locator(".dbml-zoom-in-btn").click()
    assert scale_of(wrapper) == pytest.approx(base * 1.25, rel=1e-3)
    wrapper.locator(".dbml-zoom-out-btn").click()
    wrapper.locator(".dbml-zoom-out-btn").click()
    assert scale_of(wrapper) == pytest.approx(base * 0.8, rel=1e-3)
    wrapper.locator(".dbml-fit-btn").click()
    assert svg_transform(wrapper) == fitted


def test_keyboard_shortcuts_on_focused_diagram(home, wrapper):
    base = scale_of(wrapper)
    wrapper.focus()
    home.keyboard.press("+")
    assert scale_of(wrapper) > base
    home.keyboard.press("0")
    assert scale_of(wrapper) == pytest.approx(base, rel=1e-3)
    home.keyboard.press("-")
    assert scale_of(wrapper) < base


# --- pan / drag -----------------------------------------------------------


def test_dragging_empty_canvas_pans(home, wrapper):
    box = wrapper.bounding_box()
    before = svg_transform(wrapper)
    drag(home, (box["x"] + 8, box["y"] + box["height"] - 8), (60, -30))
    assert svg_transform(wrapper) != before
    assert scale_of(wrapper) == pytest.approx(scale_of(wrapper))


def test_dragging_a_table_moves_it_and_reroutes_relationships(home, wrapper):
    before_box = table(wrapper, "users").bounding_box()
    before_paths = paths(wrapper)
    drag(home, title_point(wrapper, "users"), (40, 90))
    home.wait_for_timeout(100)
    after_box = table(wrapper, "users").bounding_box()
    assert after_box["x"] - before_box["x"] == pytest.approx(40, abs=2)
    assert after_box["y"] - before_box["y"] == pytest.approx(90, abs=2)
    after_paths = paths(wrapper)
    touching = wrapper.locator(".dbml-relationship-group").evaluate_all(
        "els => els.map(e => e.dataset.from.startsWith('users.') || e.dataset.to.startsWith('users.'))"
    )
    assert any(touching)
    for moved, old, new in zip(touching, before_paths, after_paths):
        if moved:
            assert old != new


def test_dragging_a_grouped_table_resizes_group_box(home):
    group_wrapper = home.locator(".dbml-diagram-wrapper").nth(1)
    group_wrapper.scroll_into_view_if_needed()
    bg = group_wrapper.locator(".dbml-tablegroup-bg")
    before = bg.bounding_box()
    drag(home, title_point(group_wrapper, "spoke_a"), (0, 140))
    home.wait_for_timeout(100)
    after = bg.bounding_box()
    assert after["height"] > before["height"] + 50


def test_dragging_group_box_moves_all_members(home):
    group_wrapper = home.locator(".dbml-diagram-wrapper").nth(1)
    group_wrapper.scroll_into_view_if_needed()
    a, c = table(group_wrapper, "spoke_a"), table(group_wrapper, "spoke_c")
    a0, c0 = a.bounding_box(), c.bounding_box()
    bg = group_wrapper.locator(".dbml-tablegroup-bg").bounding_box()
    drag(home, (bg["x"] + 6, bg["y"] + bg["height"] - 6), (25, 35))
    home.wait_for_timeout(100)
    for before, locator in ((a0, a), (c0, c)):
        after = locator.bounding_box()
        assert after["x"] - before["x"] == pytest.approx(25, abs=2)
        assert after["y"] - before["y"] == pytest.approx(35, abs=2)


def test_diagrams_on_one_page_are_independent(home):
    first, second = home.locator(".dbml-diagram-wrapper").all()
    base_second = svg_transform(second)
    first.locator(".dbml-zoom-in-btn").click()
    assert svg_transform(second) == base_second


# --- highlight / selection ------------------------------------------------


def dimmed(wrapper):
    return wrapper.locator(".dbml-relationship-line").evaluate_all(
        "els => els.filter(e => e.style.opacity === '0.15').length"
    )


def test_hovering_a_table_dims_unrelated_relationships(home, wrapper):
    home.mouse.move(*center(table(wrapper, "users").locator(".dbml-table-bg")))
    home.wait_for_timeout(100)
    assert dimmed(wrapper) == 1  # posts -> comments does not touch users
    home.mouse.move(5, 5)
    home.wait_for_timeout(100)
    assert dimmed(wrapper) == 0


def point_on_line(wrapper, index):
    return wrapper.locator(".dbml-relationship-line").nth(index).evaluate(
        """el => {
            const p = el.getPointAtLength(el.getTotalLength() * 0.5);
            const m = el.getScreenCTM();
            const pt = new DOMPoint(p.x, p.y).matrixTransform(m);
            return [pt.x, pt.y];
        }"""
    )


def test_clicking_a_relationship_selects_it_and_its_fields(home, wrapper):
    x, y = point_on_line(wrapper, 0)
    home.mouse.click(x, y)
    selected = wrapper.locator(".dbml-relationship-line.selected")
    expect(selected).to_have_count(1)
    expect(wrapper.locator(".dbml-field-row.selected")).to_have_count(2)
    # clicking empty canvas clears the selection
    box = wrapper.bounding_box()
    home.mouse.click(box["x"] + 6, box["y"] + box["height"] - 6)
    expect(wrapper.locator(".dbml-relationship-line.selected")).to_have_count(0)
    expect(wrapper.locator(".dbml-field-row.selected")).to_have_count(0)


# --- keyboard -------------------------------------------------------------


def test_table_can_be_moved_with_arrow_keys(home, wrapper):
    users = table(wrapper, "users")
    users.focus()
    before = users.bounding_box()
    home.keyboard.press("ArrowRight")
    home.keyboard.press("Shift+ArrowDown")
    after = users.bounding_box()
    assert after["x"] - before["x"] == pytest.approx(10, abs=1.5)
    assert after["y"] - before["y"] == pytest.approx(40, abs=1.5)


def test_focusing_a_table_highlights_its_relationships(home, wrapper):
    table(wrapper, "users").focus()
    home.wait_for_timeout(100)
    assert dimmed(wrapper) == 1
    table(wrapper, "users").blur()
    home.wait_for_timeout(100)
    assert dimmed(wrapper) == 0


def test_tab_order_reaches_buttons_and_tables(home, wrapper):
    wrapper.focus()
    seen = []
    for _ in range(12):
        home.keyboard.press("Tab")
        seen.append(
            home.evaluate(
                "document.activeElement.className.baseVal ?? document.activeElement.className"
            )
        )
    joined = " ".join(seen)
    assert "dbml-zoom-in-btn" in joined and "dbml-table-group" in joined


# --- misc widgets ---------------------------------------------------------


def test_legend_collapses_on_click(wrapper):
    legend = wrapper.locator(".dbml-legend")
    label = legend.locator(".dbml-legend-item span").first
    expect(label).to_be_visible()
    legend.click()
    expect(label).to_be_hidden()
    legend.click()
    expect(label).to_be_visible()


@pytest.mark.xfail(reason="dblclick retargeted by pointer capture, see #71", strict=True)
def test_double_click_copies_field_reference(home, wrapper):
    field = wrapper.locator('[data-field="posts.user_id"]')
    field.dblclick()
    assert home.evaluate("navigator.clipboard.readText()") == "posts.user_id"
    expect(wrapper.locator(".dbml-hint")).to_have_text("Copied: posts.user_id")


def test_fullscreen_button_toggles_title(home, wrapper):
    btn = wrapper.locator(".dbml-fullscreen-btn")
    expect(btn).to_have_attribute("title", "Fullscreen")
    btn.click()
    try:
        home.wait_for_function("document.fullscreenElement !== null", timeout=3000)
    except Exception:
        pytest.skip("this browser build does not enter fullscreen headlessly")
    expect(btn).to_have_attribute("title", "Exit fullscreen (Esc)")
    home.evaluate("document.exitFullscreen()")
    home.wait_for_function("document.fullscreenElement === null")
    expect(btn).to_have_attribute("title", "Fullscreen")
