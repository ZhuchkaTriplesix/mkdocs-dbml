"""Tests for DbmlPlugin (markdown replacement, file include)."""

import os
import tempfile
import pytest
from mkdocs_dbml_plugin.plugin import DbmlPlugin


@pytest.fixture
def plugin():
    p = DbmlPlugin()
    p.config = {"theme": "black", "show_indexes": True, "show_notes": True}
    return p


def test_plugin_replaces_dbml_block(plugin):
    md = """# Page

```dbml
Table users { id integer [pk] }
```
"""
    config = {"docs_dir": os.path.join(os.path.dirname(__file__), "..", "example", "docs")}
    result = plugin.on_page_markdown(md, None, config, None)
    assert "dbml-diagram-wrapper" in result or "dbml-error" in result


def test_plugin_empty_dbml_block_returns_error(plugin):
    md = """# Page

```dbml

```
"""
    config = {"docs_dir": "/tmp"}
    result = plugin.on_page_markdown(md, None, config, None)
    assert "dbml-error" in result or "Empty" in result or "No tables found" in result


def test_plugin_file_path_traversal_blocked(plugin):
    md = """# Page

```dbml
file: ../../../etc/passwd.dbml
```
"""
    config = {"docs_dir": tempfile.mkdtemp()}
    result = plugin.on_page_markdown(md, None, config, None)
    assert "dbml-error" in result
    assert "outside" in result or "not found" in result.lower()


def test_plugin_on_config_warns_invalid_theme(plugin, caplog):
    plugin.config["theme"] = "nonexistent_theme"
    import logging
    with caplog.at_level(logging.WARNING, logger="mkdocs.plugins.dbml"):
        plugin.on_config({})
    assert "unknown theme" in caplog.text


def test_plugin_on_post_page_skips_non_dbml_page(plugin):
    plugin.on_config({})
    output = "<html><head></head><body><p>Hello</p></body></html>"
    result = plugin.on_post_page(output, None, {})
    assert result == output


def test_plugin_on_post_page_injects_on_dbml_page(plugin):
    plugin.on_config({})
    output = "<html><head></head><body><!-- dbml-styles --><p>diagram</p></body></html>"
    result = plugin.on_post_page(output, None, {})
    assert "<style>" in result
    assert "<script>" in result
    assert "<!-- dbml-styles -->" not in result


def test_plugin_error_messages_are_escaped(plugin):
    md = """# Page

```dbml
file: <script>alert(1)</script>.dbml
```
"""
    config = {"docs_dir": tempfile.mkdtemp()}
    result = plugin.on_page_markdown(md, None, config, None)
    assert "<script>alert" not in result
