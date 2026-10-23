"""Static rendering: what a reader sees right after the page loads."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect


def test_every_diagram_is_initialized(home):
    wrappers = home.locator(".dbml-diagram-wrapper")
    assert wrappers.count() == 2
    for i in range(wrappers.count()):
        assert wrappers.nth(i).get_attribute("data-dbml-init") == "1"


def test_tables_and_relationships_rendered(wrapper):
    tables = wrapper.locator(".dbml-table-group")
    assert sorted(tables.evaluate_all("els => els.map(e => e.dataset.table)")) == [
        "comments",
        "posts",
        "users",
    ]
    assert wrapper.locator(".dbml-relationship-line").count() == 3
    expect(wrapper.locator(".dbml-field-name.is-pk")).to_have_count(3)
    expect(wrapper.locator(".dbml-field-name.is-fk")).to_have_count(3)


def test_diagram_is_fitted_into_the_viewport(wrapper):
    box = wrapper.bounding_box()
    for table in wrapper.locator(".dbml-table-group").all():
        t = table.bounding_box()
        assert t["x"] >= box["x"] - 1 and t["y"] >= box["y"] - 1
        assert t["x"] + t["width"] <= box["x"] + box["width"] + 1
        assert t["y"] + t["height"] <= box["y"] + box["height"] + 1


def test_configured_height_is_applied(wrapper):
    assert round(wrapper.bounding_box()["height"]) == 500


def test_svg_ids_are_unique_on_the_page(home):
    ids = home.evaluate("[...document.querySelectorAll('svg [id]')].map(e => e.id)")
    assert len(ids) == len(set(ids)) > 0


def test_every_url_reference_resolves(home):
    missing = home.evaluate(
        """() => {
            const html = document.querySelector('.dbml-diagram-wrapper').outerHTML;
            const refs = [...html.matchAll(/url\\(#([^)]+)\\)/g)].map(m => m[1]);
            return refs.filter(id => !document.getElementById(id));
        }"""
    )
    assert missing == []


def test_notes_and_indexes_tooltips(wrapper):
    users = wrapper.locator('.dbml-table-group[data-table="users"] > title')
    text = users.text_content()
    assert "NOTE: Application users" in text and "INDEX (email)" in text
    email = wrapper.locator('[data-field="users.email"] title')
    assert "NOTE: login email" in email.text_content()


def test_table_group_box_wraps_its_tables(home):
    group = home.locator(".dbml-tablegroup").first
    assert group.get_attribute("data-group-name") == "edge"
    box = group.locator(".dbml-tablegroup-bg").bounding_box()
    for name in ("spoke_a", "spoke_c"):
        t = home.locator(f'.dbml-table-group[data-table="{name}"]').bounding_box()
        assert box["x"] <= t["x"] and box["y"] <= t["y"]
        assert box["x"] + box["width"] >= t["x"] + t["width"] - 1


@pytest.mark.xfail(reason="layout can place non-members inside a group box, see #66", strict=True)
def test_table_group_box_does_not_cover_other_tables(home):
    box = home.locator(".dbml-tablegroup .dbml-tablegroup-bg").first.bounding_box()
    other = home.locator('.dbml-table-group[data-table="spoke_b"]').bounding_box()
    overlaps = (
        other["x"] < box["x"] + box["width"]
        and other["x"] + other["width"] > box["x"]
        and other["y"] < box["y"] + box["height"]
        and other["y"] + other["height"] > box["y"]
    )
    assert not overlaps


def test_file_include_renders(page, site_url):
    page.goto(site_url + "other/")
    page.wait_for_selector(".dbml-diagram-wrapper[data-dbml-init]")
    names = page.locator(".dbml-table-group").evaluate_all(
        "els => els.map(e => e.dataset.table).sort()"
    )
    assert names == ["categories", "products"]


def test_errors_are_shown_and_styled(page, site_url):
    page.goto(site_url + "broken/")
    errors = page.locator(".dbml-error")
    assert errors.count() == 3
    text = " | ".join(errors.all_text_contents())
    assert "Error parsing DBML" in text
    assert "DBML file not found" in text
    assert "outside docs" in text
    # stylesheet must be injected even though no diagram is on the page
    border = errors.first.evaluate("el => getComputedStyle(el).borderTopWidth")
    assert border == "2px"
    assert page.locator(".dbml-diagram-wrapper").count() == 0


def test_empty_block_message_is_styled(page, site_url):
    page.goto(site_url + "empty/")
    empty = page.locator(".dbml-empty")
    expect(empty).to_have_text("No tables found")
    assert empty.evaluate("el => getComputedStyle(el).borderTopStyle") == "dashed"
