from __future__ import annotations

import os
import re
import html as html_module
import logging
from pathlib import Path
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from .renderer import DbmlRenderer
from .config import THEMES, DEFAULT_HEIGHT

log = logging.getLogger("mkdocs.plugins.dbml")

STYLES_MARKER = "<!-- dbml-styles -->"


class DbmlPlugin(BasePlugin):
    config_scheme = (
        ("theme", config_options.Type(str, default="black")),
        ("show_indexes", config_options.Type(bool, default=True)),
        ("show_notes", config_options.Type(bool, default=True)),
        ("height", config_options.Type(int, default=DEFAULT_HEIGHT)),
    )

    def on_config(self, config):
        theme = self.config["theme"]
        if theme not in THEMES:
            available = ", ".join(sorted(THEMES.keys()))
            log.warning(
                "mkdocs-dbml: unknown theme %r, falling back to 'black'. "
                "Available themes: %s",
                theme,
                available,
            )
            self.config["theme"] = "black"

        js_path = Path(__file__).parent / "assets" / "dbml.js"
        css_path = Path(__file__).parent / "assets" / "dbml.css"
        self._js_content = js_path.read_text(encoding="utf-8")
        self._css_content = css_path.read_text(encoding="utf-8")
        self._renderer = DbmlRenderer(
            theme=self.config["theme"],
            show_indexes=self.config["show_indexes"],
            show_notes=self.config["show_notes"],
            height=self.config.get("height", DEFAULT_HEIGHT),
        )
        return config

    @staticmethod
    def _indent(text, indent):
        if not indent:
            return text
        return "\n".join(indent + line for line in text.split("\n"))

    def on_page_markdown(self, markdown, page, config, files):
        pattern = r"^([ \t]*)```dbml[ \t]*\r?\n(.*?)^[ \t]*```[ \t]*\r?$"
        docs_dir = config.get("docs_dir", "docs")

        def replace_dbml(match):
            indent = match.group(1)
            raw = match.group(2)
            if not raw.strip():
                return '<div class="dbml-error">Empty DBML block</div>'
            dbml_code = "\n".join(
                line[len(indent):] if line.startswith(indent) else line
                for line in raw.replace("\r\n", "\n").split("\n")
            ).strip()
            lines = dbml_code.split("\n")
            first = lines[0].strip() if lines else ""

            file_path = None
            if first.startswith("file:") or first.startswith("include:"):
                file_path = first.split(":", 1)[1].strip()
            elif len(lines) == 1 and first.endswith(".dbml") and " " not in first:
                file_path = first

            if file_path:
                resolved = os.path.normpath(os.path.join(docs_dir, file_path))
                docs_root = os.path.realpath(docs_dir)
                real = os.path.realpath(resolved)
                if os.path.commonpath([docs_root, real]) != docs_root:
                    return (
                        '<div class="dbml-error">DBML file path outside docs: '
                        f"{html_module.escape(file_path)}</div>"
                    )
                try:
                    with open(resolved, "r", encoding="utf-8") as f:
                        dbml_code = f.read()
                except FileNotFoundError:
                    return (
                        '<div class="dbml-error">DBML file not found: '
                        f"{html_module.escape(file_path)}</div>"
                    )
                except OSError as e:
                    return (
                        '<div class="dbml-error">Cannot read DBML file: '
                        f"{html_module.escape(str(e))}</div>"
                    )

            renderer = getattr(self, "_renderer", None)
            if renderer is None:
                renderer = DbmlRenderer(
                    theme=self.config["theme"],
                    show_indexes=self.config["show_indexes"],
                    show_notes=self.config["show_notes"],
                    height=self.config.get("height", DEFAULT_HEIGHT),
                )
            try:
                return self._indent(renderer.render(dbml_code), indent)
            except (ValueError, KeyError) as e:
                safe_msg = html_module.escape(str(e))
                return f'<div class="dbml-error">Error parsing DBML: {safe_msg}</div>'
            except Exception:
                log.exception("Unexpected error rendering DBML diagram")
                return (
                    '<div class="dbml-error">'
                    "Unexpected error rendering DBML diagram (see build log)"
                    "</div>"
                )

        markdown = re.sub(pattern, replace_dbml, markdown, flags=re.DOTALL | re.MULTILINE)
        if 'class="dbml-error"' in markdown and STYLES_MARKER not in markdown:
            markdown = STYLES_MARKER + "\n" + markdown
        return markdown

    def on_post_page(self, output, page, config):
        if STYLES_MARKER not in output:
            return output
        css = self._css_content
        js = self._js_content
        output = output.replace("</head>", f"<style>{css}</style></head>")
        output = output.replace("</body>", f"<script>{js}</script></body>")
        output = output.replace(STYLES_MARKER, "")
        return output
