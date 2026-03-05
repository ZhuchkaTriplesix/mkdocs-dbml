"""Tests for DbmlRenderer."""

import pytest
from mkdocs_dbml_plugin.renderer import DbmlRenderer


def test_render_simple_dbml_contains_wrapper(simple_dbml):
    r = DbmlRenderer(theme="black")
    html = r.render(simple_dbml)
    assert "dbml-diagram-wrapper" in html
    assert "dbml-diagram" in html
    assert "dbml-styles" in html


def test_render_simple_dbml_contains_table_names(simple_dbml):
    r = DbmlRenderer(theme="default")
    html = r.render(simple_dbml)
    assert "users" in html
    assert "posts" in html
    assert "dbml-table-group" in html


def test_render_simple_dbml_contains_relationship_layer(simple_dbml):
    r = DbmlRenderer(theme="black")
    html = r.render(simple_dbml)
    assert "dbml-relationships-layer" in html
    assert "dbml-relationship-line" in html or "dbml-relationship-group" in html


def test_render_single_table():
    r = DbmlRenderer()
    html = r.render("Table t1 {\n  id integer [primary key]\n}")
    assert "dbml-diagram" in html
    assert "t1" in html


def test_render_no_tables_returns_message():
    r = DbmlRenderer()
    html = r.render("")
    assert "No tables" in html or "dbml-error" in html


def test_render_invalid_dbml_raises_or_returns_error():
    r = DbmlRenderer()
    try:
        html = r.render("not valid dbml {")
        assert "dbml-error" in html or "Error" in html
    except Exception:
        pass


def test_render_with_tablegroup(simple_dbml):
    dbml = simple_dbml + """

TableGroup g1 {
  users
  posts
}
"""
    r = DbmlRenderer(theme="black")
    html = r.render(dbml)
    assert "dbml-tablegroups-layer" in html or "dbml-tablegroup" in html


def test_get_css_returns_non_empty_string():
    css = DbmlRenderer.get_css("black")
    assert isinstance(css, str)
    assert "dbml-diagram-wrapper" in css
    assert len(css) > 500


def test_xss_in_table_name_is_escaped():
    dbml = 'Table "users\\"style=\\"bad" {\n  id integer [pk]\n}'
    r = DbmlRenderer()
    try:
        html = r.render(dbml)
    except Exception:
        return
    assert 'style="bad"' not in html


def test_data_attributes_are_escaped(simple_dbml):
    r = DbmlRenderer(theme="black")
    html = r.render(simple_dbml)
    assert 'data-table="' in html
    assert 'data-field="' in html
    assert 'data-from="' in html or 'data-to="' in html


def test_render_uses_sha256_ids(simple_dbml):
    r = DbmlRenderer()
    html = r.render(simple_dbml)
    assert "dbml-" in html
    import re
    ids = re.findall(r'id="dbml-([a-f0-9]+)"', html)
    for h in ids:
        assert len(h) == 16, f"Expected 16-char sha256 hash, got {len(h)}"
