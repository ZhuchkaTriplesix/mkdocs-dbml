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


def test_plugin_file_path_sibling_dir_with_same_prefix_blocked(plugin, tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    secret = tmp_path / "docs_secret"
    secret.mkdir()
    (secret / "x.dbml").write_text("Table t { id integer }", encoding="utf-8")
    md = "```dbml\nfile: ../docs_secret/x.dbml\n```\n"
    result = plugin.on_page_markdown(md, None, {"docs_dir": str(docs)}, None)
    assert "outside docs" in result


def test_plugin_unknown_theme_falls_back_to_black(caplog):
    p = DbmlPlugin()
    p.config = {"theme": "nope", "show_indexes": True, "show_notes": True}
    p.on_config({})
    assert p.config["theme"] == "black"
    assert "falling back to 'black'" in caplog.text


def test_plugin_handles_crlf(plugin):
    md = "# Page\r\n\r\n```dbml\r\nTable users {\r\n  id integer [pk]\r\n}\r\n```\r\n"
    result = plugin.on_page_markdown(md, None, {"docs_dir": "docs"}, None)
    assert "dbml-diagram-wrapper" in result
    assert "```dbml" not in result


def test_plugin_handles_indented_block(plugin):
    md = '!!! note\n    ```dbml\n    Table users {\n      id integer [pk]\n    }\n    ```\n'
    result = plugin.on_page_markdown(md, None, {"docs_dir": "docs"}, None)
    assert "dbml-diagram-wrapper" in result
    assert "```dbml" not in result
    assert all(line.startswith("    ") for line in result.splitlines()[1:] if line.strip())


def test_plugin_height_option_passed_to_renderer():
    p = DbmlPlugin()
    p.config = {"theme": "black", "show_indexes": True, "show_notes": True, "height": 321}
    p.on_config({})
    assert "--dbml-height:321px" in p.on_page_markdown(
        "```dbml\nTable a {\n  id integer\n}\n```\n", None, {"docs_dir": "docs"}, None
    )


def test_plugin_injects_styles_for_error_only_pages(plugin):
    plugin.on_config({})
    md = "```dbml\nfile: missing.dbml\n```\n"
    out = plugin.on_page_markdown(md, None, {"docs_dir": "docs"}, None)
    assert "<!-- dbml-styles -->" in out
    html = plugin.on_post_page("<html><head></head><body>" + out + "</body></html>", None, {})
    assert "<style>" in html and ".dbml-error" in html


def test_plugin_syntax_error_is_reported_without_traceback(plugin, caplog):
    plugin.on_config({})
    md = "```dbml\nTable oops {\n  id integer [\n```\n"
    out = plugin.on_page_markdown(md, None, {"docs_dir": "docs"}, None)
    assert "Error parsing DBML" in out
    assert "Unexpected error" not in out
    assert "Traceback" not in caplog.text


def test_plugin_syntax_error_message_is_concise(plugin):
    plugin.on_config({})
    md = "```dbml\nTable oops {\n  id integer [\n}\n```\n"
    out = plugin.on_page_markdown(md, None, {"docs_dir": "docs"}, None)
    assert "syntax error at line 3, column 1" in out
    assert len(out) < 400
