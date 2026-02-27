from pydbml import PyDBML
from typing import Dict, List


class DbmlRenderer:
    def __init__(self, theme='default', show_indexes=True, show_notes=True):
        self.theme = theme
        self.show_indexes = show_indexes
        self.show_notes = show_notes

    def render(self, dbml_code: str) -> str:
        parsed = PyDBML(dbml_code)
        
        html_parts = ['<!-- dbml-styles -->', '<div class="dbml-container">']
        
        if parsed.tables:
            html_parts.append('<div class="dbml-tables">')
            for table in parsed.tables:
                html_parts.append(self._render_table(table))
            html_parts.append('</div>')
        
        if parsed.refs:
            html_parts.append(self._render_relationships(parsed.refs))
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)

    def _render_table(self, table) -> str:
        html = [f'<div class="dbml-table">']
        html.append(f'<div class="dbml-table-header">')
        html.append(f'<h3 class="dbml-table-name">{table.name}</h3>')
        if table.note and self.show_notes:
            html.append(f'<div class="dbml-table-note">{table.note}</div>')
        html.append('</div>')
        
        html.append('<table class="dbml-fields-table">')
        html.append('<thead>')
        html.append('<tr>')
        html.append('<th>Поле</th>')
        html.append('<th>Тип</th>')
        html.append('<th>Атрибуты</th>')
        html.append('</tr>')
        html.append('</thead>')
        html.append('<tbody>')
        
        for column in table.columns:
            html.append(self._render_column(column))
        
        html.append('</tbody>')
        html.append('</table>')
        
        if self.show_indexes and table.indexes:
            html.append('<div class="dbml-indexes">')
            html.append('<h4>Индексы:</h4>')
            html.append('<ul>')
            for index in table.indexes:
                index_fields = ', '.join([col.name for col in index.subjects])
                index_type = 'UNIQUE' if index.unique else 'INDEX'
                html.append(f'<li><span class="dbml-index-type">{index_type}</span>: {index_fields}</li>')
            html.append('</ul>')
            html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)

    def _render_column(self, column) -> str:
        html = ['<tr>']
        
        name_class = 'dbml-field-name'
        if column.pk:
            name_class += ' dbml-primary-key'
        
        html.append(f'<td class="{name_class}">')
        html.append(column.name)
        if column.pk:
            html.append(' <span class="dbml-badge dbml-badge-pk">PK</span>')
        html.append('</td>')
        
        html.append(f'<td class="dbml-field-type">{column.type}</td>')
        
        attributes = []
        if column.not_null:
            attributes.append('<span class="dbml-badge dbml-badge-not-null">NOT NULL</span>')
        if column.unique:
            attributes.append('<span class="dbml-badge dbml-badge-unique">UNIQUE</span>')
        if column.default is not None:
            default_val = str(column.default)
            attributes.append(f'<span class="dbml-badge dbml-badge-default">DEFAULT: {default_val}</span>')
        if column.note:
            attributes.append(f'<span class="dbml-note-inline">{column.note}</span>')
        
        html.append(f'<td class="dbml-field-attributes">{" ".join(attributes) if attributes else "-"}</td>')
        
        html.append('</tr>')
        return ''.join(html)

    def _render_relationships(self, refs: List) -> str:
        if not refs:
            return ''
        
        html = ['<div class="dbml-relationships">']
        html.append('<h3>Связи между таблицами</h3>')
        html.append('<table class="dbml-refs-table">')
        html.append('<thead>')
        html.append('<tr>')
        html.append('<th>Из таблицы</th>')
        html.append('<th>Тип связи</th>')
        html.append('<th>В таблицу</th>')
        html.append('</tr>')
        html.append('</thead>')
        html.append('<tbody>')
        
        for ref in refs:
            rel_type = self._get_relationship_type(ref.type)
            
            col1 = ref.col1[0] if ref.col1 else None
            col2 = ref.col2[0] if ref.col2 else None
            
            if col1 and col2:
                from_text = f'{col1.table.name}.{col1.name}'
                to_text = f'{col2.table.name}.{col2.name}'
                
                html.append('<tr>')
                html.append(f'<td class="dbml-ref-from">{from_text}</td>')
                html.append(f'<td class="dbml-ref-type"><span class="dbml-badge dbml-badge-ref">{rel_type}</span></td>')
                html.append(f'<td class="dbml-ref-to">{to_text}</td>')
                html.append('</tr>')
        
        html.append('</tbody>')
        html.append('</table>')
        html.append('</div>')
        
        return '\n'.join(html)

    def _get_relationship_type(self, ref_type: str) -> str:
        mapping = {
            '>': 'Many-to-One',
            '<': 'One-to-Many',
            '-': 'One-to-One',
            '<>': 'Many-to-Many'
        }
        return mapping.get(ref_type, ref_type)

    @staticmethod
    def get_css(theme='default') -> str:
        base_css = """
        .dbml-container {
            margin: 2rem 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }
        
        .dbml-tables {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .dbml-table {
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            overflow: hidden;
            background: #ffffff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .dbml-table:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .dbml-table-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem 1.25rem;
            color: white;
        }
        
        .dbml-table-name {
            margin: 0;
            font-size: 1.25rem;
            font-weight: 600;
            color: white;
        }
        
        .dbml-table-note {
            margin-top: 0.5rem;
            font-size: 0.875rem;
            opacity: 0.9;
        }
        
        .dbml-fields-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }
        
        .dbml-fields-table thead {
            background: #f6f8fa;
        }
        
        .dbml-fields-table th {
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            color: #24292e;
            border-bottom: 2px solid #e1e4e8;
        }
        
        .dbml-fields-table td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #e1e4e8;
            vertical-align: top;
        }
        
        .dbml-fields-table tbody tr:last-child td {
            border-bottom: none;
        }
        
        .dbml-fields-table tbody tr:hover {
            background: #f6f8fa;
        }
        
        .dbml-field-name {
            font-weight: 500;
            color: #0366d6;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }
        
        .dbml-field-name.dbml-primary-key {
            color: #d73a49;
            font-weight: 600;
        }
        
        .dbml-field-type {
            color: #6f42c1;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }
        
        .dbml-field-attributes {
            display: flex;
            flex-wrap: wrap;
            gap: 0.375rem;
        }
        
        .dbml-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            white-space: nowrap;
        }
        
        .dbml-badge-pk {
            background: #ffeef0;
            color: #d73a49;
            border: 1px solid #d73a49;
        }
        
        .dbml-badge-not-null {
            background: #fff5e6;
            color: #e36209;
            border: 1px solid #e36209;
        }
        
        .dbml-badge-unique {
            background: #f0f6ff;
            color: #0366d6;
            border: 1px solid #0366d6;
        }
        
        .dbml-badge-default {
            background: #f6f8fa;
            color: #586069;
            border: 1px solid #d1d5da;
        }
        
        .dbml-badge-ref {
            background: #f0fff4;
            color: #22863a;
            border: 1px solid #22863a;
        }
        
        .dbml-note-inline {
            font-style: italic;
            color: #6a737d;
            font-size: 0.8125rem;
        }
        
        .dbml-indexes {
            padding: 1rem 1.25rem;
            background: #f6f8fa;
            border-top: 1px solid #e1e4e8;
        }
        
        .dbml-indexes h4 {
            margin: 0 0 0.5rem 0;
            font-size: 0.875rem;
            color: #24292e;
            font-weight: 600;
        }
        
        .dbml-indexes ul {
            margin: 0;
            padding-left: 1.25rem;
            list-style: none;
        }
        
        .dbml-indexes li {
            padding: 0.25rem 0;
            font-size: 0.8125rem;
            color: #586069;
        }
        
        .dbml-index-type {
            font-weight: 600;
            color: #0366d6;
        }
        
        .dbml-relationships {
            margin-top: 2rem;
            padding: 1.5rem;
            background: #f6f8fa;
            border-radius: 8px;
            border: 1px solid #e1e4e8;
        }
        
        .dbml-relationships h3 {
            margin: 0 0 1rem 0;
            font-size: 1.125rem;
            color: #24292e;
        }
        
        .dbml-refs-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 6px;
            overflow: hidden;
        }
        
        .dbml-refs-table th {
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            background: #ffffff;
            border-bottom: 2px solid #e1e4e8;
        }
        
        .dbml-refs-table td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #e1e4e8;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.875rem;
        }
        
        .dbml-refs-table tbody tr:last-child td {
            border-bottom: none;
        }
        
        .dbml-refs-table tbody tr:hover {
            background: #f6f8fa;
        }
        
        .dbml-ref-from {
            color: #0366d6;
        }
        
        .dbml-ref-to {
            color: #22863a;
        }
        
        .dbml-ref-type {
            text-align: center;
        }
        
        .dbml-error {
            padding: 1rem;
            background: #ffeef0;
            border: 1px solid #d73a49;
            border-radius: 6px;
            color: #d73a49;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }
        
        @media (max-width: 768px) {
            .dbml-tables {
                grid-template-columns: 1fr;
            }
        }
        """
        
        dark_theme_additions = """
        @media (prefers-color-scheme: dark) {
            .dbml-table {
                background: #1e1e1e;
                border-color: #3e3e3e;
            }
            
            .dbml-fields-table thead {
                background: #2d2d2d;
            }
            
            .dbml-fields-table th {
                color: #e1e4e8;
                border-bottom-color: #3e3e3e;
            }
            
            .dbml-fields-table td {
                border-bottom-color: #3e3e3e;
            }
            
            .dbml-fields-table tbody tr:hover {
                background: #2d2d2d;
            }
            
            .dbml-relationships {
                background: #2d2d2d;
                border-color: #3e3e3e;
            }
            
            .dbml-relationships h3 {
                color: #e1e4e8;
            }
            
            .dbml-refs-table {
                background: #1e1e1e;
            }
            
            .dbml-refs-table th {
                background: #1e1e1e;
                border-bottom-color: #3e3e3e;
            }
            
            .dbml-refs-table td {
                border-bottom-color: #3e3e3e;
            }
            
            .dbml-refs-table tbody tr:hover {
                background: #2d2d2d;
            }
            
            .dbml-indexes {
                background: #2d2d2d;
                border-top-color: #3e3e3e;
            }
            
            .dbml-indexes h4 {
                color: #e1e4e8;
            }
        }
        """
        
        if theme == 'dark':
            return base_css + dark_theme_additions
        
        return base_css

    def _render_relationships(self, refs: List) -> str:
        if not refs:
            return ''
        
        html = ['<div class="dbml-relationships">']
        html.append('<h3>Связи между таблицами</h3>')
        html.append('<table class="dbml-refs-table">')
        html.append('<thead>')
        html.append('<tr>')
        html.append('<th>Из таблицы</th>')
        html.append('<th>Тип связи</th>')
        html.append('<th>В таблицу</th>')
        html.append('</tr>')
        html.append('</thead>')
        html.append('<tbody>')
        
        for ref in refs:
            rel_type = self._get_relationship_type(ref.type)
            
            col1 = ref.col1[0] if ref.col1 else None
            col2 = ref.col2[0] if ref.col2 else None
            
            if col1 and col2:
                from_text = f'{col1.table.name}.{col1.name}'
                to_text = f'{col2.table.name}.{col2.name}'
                
                html.append('<tr>')
                html.append(f'<td class="dbml-ref-from">{from_text}</td>')
                html.append(f'<td class="dbml-ref-type"><span class="dbml-badge dbml-badge-ref">{rel_type}</span></td>')
                html.append(f'<td class="dbml-ref-to">{to_text}</td>')
                html.append('</tr>')
        
        html.append('</tbody>')
        html.append('</table>')
        html.append('</div>')
        
        return '\n'.join(html)

    def _get_relationship_type(self, ref_type: str) -> str:
        mapping = {
            '>': 'Many-to-One',
            '<': 'One-to-Many',
            '-': 'One-to-One',
            '<>': 'Many-to-Many'
        }
        return mapping.get(ref_type, ref_type)
