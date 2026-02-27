import re
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from .renderer import DbmlRenderer


class DbmlPlugin(BasePlugin):
    config_scheme = (
        ('theme', config_options.Type(str, default='default')),
        ('show_indexes', config_options.Type(bool, default=True)),
        ('show_notes', config_options.Type(bool, default=True)),
    )

    def on_page_markdown(self, markdown, page, config, files):
        pattern = r'```dbml\n(.*?)```'
        
        def replace_dbml(match):
            dbml_code = match.group(1)
            renderer = DbmlRenderer(
                theme=self.config['theme'],
                show_indexes=self.config['show_indexes'],
                show_notes=self.config['show_notes']
            )
            try:
                html = renderer.render(dbml_code)
                return html
            except Exception as e:
                return f'<div class="dbml-error">Error parsing DBML: {str(e)}</div>'
        
        markdown = re.sub(pattern, replace_dbml, markdown, flags=re.DOTALL)
        return markdown

    def on_post_page(self, output, page, config):
        if '<!-- dbml-styles -->' not in output:
            css = DbmlRenderer.get_css(self.config['theme'])
            output = output.replace('</head>', f'<style>{css}</style></head>')
        return output
