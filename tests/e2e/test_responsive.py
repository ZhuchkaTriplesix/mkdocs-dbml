"""Small screens and touch."""

from __future__ import annotations

import pytest


@pytest.fixture
def mobile(page, site_url):
    page.set_viewport_size({"width": 375, "height": 700})
    page.goto(site_url)
    page.wait_for_selector("[data-dbml-init]")
    return page


def test_diagram_height_is_capped_on_phones(mobile):
    box = mobile.locator(".dbml-diagram-wrapper").first.bounding_box()
    assert box["height"] <= 400.5


def test_legend_stays_inside_the_diagram(mobile):
    wrapper = mobile.locator(".dbml-diagram-wrapper").first
    box = wrapper.bounding_box()
    legend = wrapper.locator(".dbml-legend").bounding_box()
    assert legend["x"] >= box["x"] - 1
    assert legend["x"] + legend["width"] <= box["x"] + box["width"] + 1


def test_controls_do_not_overflow_the_diagram(mobile):
    wrapper = mobile.locator(".dbml-diagram-wrapper").first
    box = wrapper.bounding_box()
    controls = wrapper.locator(".dbml-controls").bounding_box()
    assert controls["x"] >= box["x"] - 1
    assert controls["x"] + controls["width"] <= box["x"] + box["width"] + 1


def test_diagram_is_fitted_on_small_viewports(mobile):
    wrapper = mobile.locator(".dbml-diagram-wrapper").first
    box = wrapper.bounding_box()
    for table in wrapper.locator(".dbml-table-group").all():
        t = table.bounding_box()
        assert t["x"] >= box["x"] - 1 and t["x"] + t["width"] <= box["x"] + box["width"] + 1


def test_touch_actions_allow_page_scroll_but_not_table_drag(mobile):
    wrapper = mobile.locator(".dbml-diagram-wrapper").first
    assert wrapper.evaluate("el => getComputedStyle(el).touchAction") == "pan-y"
    table = wrapper.locator(".dbml-table-group").first
    assert table.evaluate("el => getComputedStyle(el).touchAction") == "none"


def test_wheel_over_diagram_scrolls_page_on_small_screens(mobile):
    wrapper = mobile.locator(".dbml-diagram-wrapper").first
    box = wrapper.bounding_box()
    mobile.mouse.move(box["x"] + box["width"] / 2, box["y"] + 20)
    y0 = mobile.evaluate("window.scrollY")
    mobile.mouse.wheel(0, 200)
    mobile.wait_for_timeout(200)
    assert mobile.evaluate("window.scrollY") > y0
