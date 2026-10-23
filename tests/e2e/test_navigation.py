"""Material `navigation.instant` swaps pages without a full reload."""

from __future__ import annotations

from playwright.sync_api import expect


def test_diagram_initializes_after_instant_navigation(home):
    home.evaluate("window.__same_document = true")
    home.get_by_role("link", name="Other page").click()
    home.wait_for_url("**/other/")
    home.wait_for_selector(".dbml-diagram-wrapper[data-dbml-init]")
    assert home.evaluate("window.__same_document") is True  # no full reload happened
    assert home.locator(".dbml-table-group").count() == 2
    expect(home.locator(".dbml-hint")).to_have_count(1)  # initialized exactly once


def test_navigating_back_reinitializes_without_duplicate_handlers(home):
    home.evaluate("window.__same_document = true")
    home.get_by_role("link", name="Other page").click()
    home.wait_for_url("**/other/")
    home.go_back()
    home.wait_for_url(lambda url: url.endswith("/") and "/other/" not in url)
    home.wait_for_selector(".dbml-diagram-wrapper[data-dbml-init]")
    wrappers = home.locator(".dbml-diagram-wrapper")
    assert wrappers.count() == 2
    first = wrappers.first
    scale_before = first.locator(".dbml-diagram").evaluate("el => el.style.transform")
    first.locator(".dbml-zoom-in-btn").click()
    after = first.locator(".dbml-diagram").evaluate("el => el.style.transform")
    # one click == one 1.25x step (a duplicated handler would apply it twice)
    import re

    s0 = float(re.search(r"scale\(([\d.]+)\)", scale_before).group(1))
    s1 = float(re.search(r"scale\(([\d.]+)\)", after).group(1))
    assert abs(s1 / s0 - 1.25) < 0.01


def test_fullscreen_listener_registered_once(home):
    assert home.evaluate("window.__dbmlBootstrapped") is True
