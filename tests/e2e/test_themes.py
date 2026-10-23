"""Colour schemes: plugin theme and site light/dark palettes."""

from __future__ import annotations

from playwright.sync_api import expect

PK_LIGHT_SCHEME = "rgb(185, 28, 28)"  # not used by `black` theme, see below
PK_DARK = "rgb(248, 113, 113)"


def fill(wrapper, selector):
    return wrapper.locator(selector).first.evaluate("el => getComputedStyle(el).fill")


def css(wrapper, selector, prop):
    return wrapper.locator(selector).first.evaluate(
        "(el, p) => getComputedStyle(el)[p]", prop
    )


def test_wrapper_background_follows_plugin_theme(wrapper):
    assert css(wrapper, ":scope", "backgroundColor") == "rgb(0, 0, 0)"


def test_light_scheme_controls_are_light(wrapper):
    assert css(wrapper, ".dbml-legend", "backgroundColor") == "rgb(255, 255, 255)"


def test_material_slate_scheme_switches_ui_to_dark(home, wrapper):
    home.evaluate("document.body.setAttribute('data-md-color-scheme', 'slate')")
    home.wait_for_timeout(350)  # button background transition
    assert css(wrapper, ".dbml-legend", "backgroundColor") == "rgba(31, 41, 55, 0.95)"
    assert css(wrapper, ".dbml-zoom-in-btn", "backgroundColor") == "rgba(31, 41, 55, 0.95)"
    assert fill(wrapper, ".dbml-field-name.is-pk") == PK_DARK
    assert fill(wrapper, ".dbml-field-name.is-fk") == "rgb(52, 211, 153)"
    assert fill(wrapper, ".dbml-field-type") == "rgb(165, 180, 252)"
    assert fill(wrapper, ".dbml-field-name:not(.is-pk):not(.is-fk)") == "rgb(229, 231, 235)"


def test_accent_colours_survive_dark_mode(home, wrapper):
    home.evaluate("document.body.setAttribute('data-md-color-scheme', 'slate')")
    colours = {
        fill(wrapper, ".dbml-field-name.is-pk"),
        fill(wrapper, ".dbml-field-name.is-fk"),
        fill(wrapper, ".dbml-field-name:not(.is-pk):not(.is-fk)"),
        fill(wrapper, ".dbml-field-type"),
    }
    assert len(colours) == 4  # distinct, not flattened to one grey


def test_table_hover_uses_accent(home, wrapper):
    table = wrapper.locator('.dbml-table-group[data-table="users"] .dbml-table-bg')
    box = table.bounding_box()
    home.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    stroke = table.evaluate("el => getComputedStyle(el).stroke")
    assert stroke == "rgb(99, 102, 241)"


def test_focus_ring_visible_on_buttons(home, wrapper):
    btn = wrapper.locator(".dbml-fit-btn")
    btn.focus()
    home.keyboard.press("Shift+Tab")
    home.keyboard.press("Tab")
    outline = btn.evaluate("el => getComputedStyle(el).outlineStyle")
    assert outline == "solid"


def test_reduced_motion_disables_transitions(page, site_url):
    page.emulate_media(reduced_motion="reduce")
    page.goto(site_url)
    page.wait_for_selector("[data-dbml-init]")
    duration = page.locator(".dbml-zoom-in-btn").first.evaluate(
        "el => getComputedStyle(el).transitionDuration"
    )
    assert set(duration.replace("s", "").split(", ")) == {"0"}
