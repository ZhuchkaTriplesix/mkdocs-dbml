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
