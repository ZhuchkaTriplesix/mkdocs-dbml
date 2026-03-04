import os
import re
import html as html_module
import logging
from pathlib import Path
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from .renderer import DbmlRenderer
from .config import THEMES

log = logging.getLogger("mkdocs.plugins.dbml")


class DbmlPlugin(BasePlugin):
    config_scheme = (
        ("theme", config_options.Type(str, default="black")),
        ("show_indexes", config_options.Type(bool, default=True)),
        ("show_notes", config_options.Type(bool, default=True)),
    )

    def on_config(self, config):
        theme = self.config["theme"]
        if theme not in THEMES:
            available = ", ".join(sorted(THEMES.keys()))
            log.warning(
                "mkdocs-dbml: unknown theme %r, falling back to 'default'. "
                "Available themes: %s",
                theme,
                available,
            )

        js_path = Path(__file__).parent / "assets" / "dbml.js"
        self._js_content = js_path.read_text(encoding="utf-8")
        return config

    def on_page_markdown(self, markdown, page, config, files):
        pattern = r"```dbml\n(.*?)```"
        docs_dir = config.get("docs_dir", "docs")

        def replace_dbml(match):
            raw = match.group(1)
            if not raw:
                return '<div class="dbml-error">Empty DBML block</div>'
            dbml_code = raw.strip()
            lines = dbml_code.split("\n")
            first = lines[0].strip() if lines else ""

            file_path = None
            if first.startswith("file:") or first.startswith("include:"):
                file_path = first.split(":", 1)[1].strip()
            elif len(lines) == 1 and first.endswith(".dbml") and " " not in first:
                file_path = first

            if file_path:
                resolved = os.path.normpath(os.path.join(docs_dir, file_path))
                if not os.path.abspath(resolved).startswith(
                    os.path.abspath(docs_dir)
                ):
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

            renderer = DbmlRenderer(
                theme=self.config["theme"],
                show_indexes=self.config["show_indexes"],
                show_notes=self.config["show_notes"],
            )
            try:
                return renderer.render(dbml_code)
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

        markdown = re.sub(pattern, replace_dbml, markdown, flags=re.DOTALL)
        return markdown

    def on_post_page(self, output, page, config):
        if "<!-- dbml-styles -->" not in output:
            return output
        css = DbmlRenderer.get_css(self.config["theme"])
        js = self._js_content
        output = output.replace("</head>", f"<style>{css}</style></head>")
        output = output.replace("</body>", f"<script>{js}</script></body>")
        output = output.replace("<!-- dbml-styles -->", "")
        return output
