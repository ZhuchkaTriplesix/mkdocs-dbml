from pydbml import PyDBML
import hashlib
from .layout import GraphLayoutEngine
from .config import get_theme_colors
from .routing import route_connection, build_table_rects


class DbmlRenderer:
    def __init__(self, theme="default", show_indexes=True, show_notes=True):
        self.theme = theme
        self.show_indexes = show_indexes
        self.show_notes = show_notes
        self.table_positions = {}
        self.table_dimensions = {}
        self.colors = get_theme_colors(theme)

    def render(self, dbml_code: str) -> str:
        parsed = PyDBML(dbml_code)

        if not parsed.tables:
            return '<div class="dbml-container">No tables found</div>'

        layout_engine = GraphLayoutEngine(parsed.tables, parsed.refs)
        self.table_positions, self.table_dimensions = (
            layout_engine.calculate_positions()
        )

        self.field_positions = {}
        for table in parsed.tables:
            self.field_positions[table.name] = {}
            x, y = self.table_positions[table.name]
            current_y = y + 66
            for column in table.columns:
                self.field_positions[table.name][column.name] = (x, current_y)
                current_y += 36

        self._table_names, self._table_idx, self._table_rects = build_table_rects(
            self.table_positions, self.table_dimensions
        )

        diagram_id = hashlib.md5(dbml_code.encode()).hexdigest()[:8]

        html_parts = [
            "<!-- dbml-styles -->",
            f'<div class="dbml-diagram-wrapper" id="dbml-{diagram_id}">',
        ]

        html_parts.append('<div class="dbml-legend">')
        html_parts.append('<div class="dbml-legend-item">')
        html_parts.append(
            '<svg width="20" height="20" viewBox="0 0 24 24"><path fill="#ef4444" d="M12 2C13.1 2 14 2.9 14 4C14 4.74 13.6 5.39 13 5.73V7H14C16.76 7 19 9.24 19 12V13H21V15H19V16H21V18H19V20H17V18H15V20H13V18H11V20H9V18H7V20H5V18H3V16H5V15H3V13H5V12C5 9.24 7.24 7 10 7H11V5.73C10.4 5.39 10 4.74 10 4C10 2.9 10.9 2 12 2M12 4C11.45 4 11 4.45 11 5C11 5.55 11.45 6 12 6C12.55 6 13 5.55 13 5C13 4.45 12.55 4 12 4Z"/></svg>'
        )
        html_parts.append("<span>Primary Key</span></div>")
        html_parts.append('<div class="dbml-legend-item">')
        html_parts.append(
            '<svg width="20" height="20" viewBox="0 0 24 24"><path fill="#10b981" d="M10.59,13.41C11,13.8 11,14.44 10.59,14.83C10.2,15.22 9.56,15.22 9.17,14.83C7.22,12.88 7.22,9.71 9.17,7.76V7.76L12.71,4.22C14.66,2.27 17.83,2.27 19.78,4.22C21.73,6.17 21.73,9.34 19.78,11.29L18.29,12.78C18.3,11.96 18.17,11.14 17.89,10.36L18.36,9.88C19.54,8.71 19.54,6.81 18.36,5.64C17.19,4.46 15.29,4.46 14.12,5.64L10.59,9.17C9.41,10.34 9.41,12.24 10.59,13.41M13.41,9.17C13.8,8.78 14.44,8.78 14.83,9.17C16.78,11.12 16.78,14.29 14.83,16.24V16.24L11.29,19.78C9.34,21.73 6.17,21.73 4.22,19.78C2.27,17.83 2.27,14.66 4.22,12.71L5.71,11.22C5.7,12.04 5.83,12.86 6.11,13.65L5.64,14.12C4.46,15.29 4.46,17.19 5.64,18.36C6.81,19.54 8.71,19.54 9.88,18.36L13.41,14.83C14.59,13.66 14.59,11.76 13.41,10.59C13,10.2 13,9.56 13.41,9.17Z"/></svg>'
        )
        html_parts.append("<span>Foreign Key</span></div>")
        html_parts.append('<div class="dbml-legend-item">')
        html_parts.append(
            '<svg width="18" height="18" viewBox="0 0 24 24"><path fill="#f59e0b" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M11,7H13V9H11V7M11,11H13V17H11V11Z"/></svg>'
        )
        html_parts.append("<span>Not Null</span></div>")
        html_parts.append('<div class="dbml-legend-item">')
        html_parts.append(
            '<svg width="18" height="18" viewBox="0 0 24 24"><path fill="#3b82f6" d="M19,3H14.82C14.4,1.84 13.3,1 12,1C10.7,1 9.6,1.84 9.18,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M12,3A1,1 0 0,1 13,4A1,1 0 0,1 12,5A1,1 0 0,1 11,4A1,1 0 0,1 12,3M7,7H17V5H19V19H5V5H7V7M7.5,13.5L9,12L11,14L15.5,9.5L17,11L11,17L7.5,13.5Z"/></svg>'
        )
        html_parts.append("<span>Unique</span></div>")
        html_parts.append("</div>")

        svg_content = self._render_svg_diagram(parsed)
        html_parts.append(svg_content)

        html_parts.append("</div>")

        return "\n".join(html_parts)

    def _render_svg_diagram(self, parsed) -> str:
        max_x = (
            max(
                pos[0] + self.table_dimensions[name][0]
                for name, pos in self.table_positions.items()
            )
            + 50
        )
        max_y = (
            max(
                pos[1] + self.table_dimensions[name][1]
                for name, pos in self.table_positions.items()
            )
            + 50
        )

        svg_parts = [
            f'<svg class="dbml-diagram" viewBox="0 0 {max_x} {max_y}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">'
        ]

        line_color = self.colors["line_color"]

        svg_parts.append("<defs>")

        svg_parts.append(
            '<marker id="arrow-one-start" viewBox="0 0 10 10" markerWidth="10" markerHeight="10"'
            ' refX="0" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
        )
        svg_parts.append(
            f'<line x1="0" y1="1" x2="0" y2="9" stroke="{line_color}" stroke-width="2"/>'
        )
        svg_parts.append("</marker>")

        svg_parts.append(
            '<marker id="arrow-one-end" viewBox="0 0 10 10" markerWidth="10" markerHeight="10"'
            ' refX="10" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
        )
        svg_parts.append(
            f'<line x1="10" y1="1" x2="10" y2="9" stroke="{line_color}" stroke-width="2"/>'
        )
        svg_parts.append("</marker>")

        svg_parts.append(
            '<marker id="arrow-many-start" viewBox="0 0 12 10" markerWidth="12" markerHeight="10"'
            ' refX="0" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
        )
        svg_parts.append(
            f'<path d="M 0,2 L 6,5 L 0,8" stroke="{line_color}" stroke-width="1.5" fill="none"/>'
            f'<path d="M 4,0 L 12,5 L 4,10" stroke="{line_color}" stroke-width="1.5" fill="none"/>'
        )
        svg_parts.append("</marker>")

        svg_parts.append(
            '<marker id="arrow-many-end" viewBox="0 0 12 10" markerWidth="12" markerHeight="10"'
            ' refX="12" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
        )
        svg_parts.append(
            f'<path d="M 12,2 L 6,5 L 12,8" stroke="{line_color}" stroke-width="1.5" fill="none"/>'
            f'<path d="M 8,0 L 0,5 L 8,10" stroke="{line_color}" stroke-width="1.5" fill="none"/>'
        )
        svg_parts.append("</marker>")

        svg_parts.append(
            '<marker id="arrow-optional-start" viewBox="0 0 10 10" markerWidth="10" markerHeight="10"'
            ' refX="0" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
        )
        svg_parts.append(
            f'<circle cx="5" cy="5" r="4" fill="none" stroke="{line_color}" stroke-width="1.5"/>'
        )
        svg_parts.append("</marker>")

        svg_parts.append(
            '<marker id="arrow-optional-end" viewBox="0 0 10 10" markerWidth="10" markerHeight="10"'
            ' refX="10" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
        )
        svg_parts.append(
            f'<circle cx="5" cy="5" r="4" fill="none" stroke="{line_color}" stroke-width="1.5"/>'
        )
        svg_parts.append("</marker>")

        svg_parts.append('<filter id="shadow">')
        svg_parts.append(
            '<feDropShadow dx="0" dy="2" stdDeviation="4" flood-opacity="0.15"/>'
        )
        svg_parts.append("</filter>")

        svg_parts.append('<filter id="glow">')
        svg_parts.append('<feGaussianBlur stdDeviation="2" result="coloredBlur"/>')
        svg_parts.append(
            '<feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        )
        svg_parts.append("</filter>")

        svg_parts.append("</defs>")

        if parsed.refs:
            svg_parts.append('<g class="dbml-relationships-layer">')
            for ref in parsed.refs:
                svg_parts.append(self._render_relationship_line(ref))
            svg_parts.append("</g>")

        svg_parts.append('<g class="dbml-tables-layer">')
        for table in parsed.tables:
            svg_parts.append(self._render_svg_table(table))
        svg_parts.append("</g>")

        svg_parts.append("</svg>")

        return "\n".join(svg_parts)

    def _render_svg_table(self, table) -> str:
        x, y = self.table_positions[table.name]
        width, height = self.table_dimensions[table.name]

        svg = []

        svg.append(f'<g class="dbml-table-group" data-table="{table.name}">')

        svg.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" ')
        svg.append(
            'class="dbml-table-bg" fill="white" stroke="#e5e7eb" stroke-width="2" rx="8" filter="url(#shadow)"/>'
        )

        gradient_id = f"gradient-{hashlib.md5(table.name.encode()).hexdigest()[:8]}"
        svg.append(
            f'<defs><linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="100%" y2="0%">'
        )
        svg.append(
            f'<stop offset="0%" style="stop-color:{self.colors["gradient_start"]};stop-opacity:1" />'
        )
        svg.append(
            f'<stop offset="100%" style="stop-color:{self.colors["gradient_end"]};stop-opacity:1" />'
        )
        svg.append("</linearGradient></defs>")

        clip_id = f"clip-{hashlib.md5(table.name.encode()).hexdigest()[:8]}"
        svg.append(
            f'<defs><clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{width}" height="44" rx="8"/></clipPath></defs>'
        )
        svg.append(f'<rect x="{x}" y="{y}" width="{width}" height="44" ')
        svg.append(f'fill="url(#{gradient_id})" clip-path="url(#{clip_id})"/>')
        svg.append(
            f'<rect x="{x}" y="{y + 36}" width="{width}" height="8" fill="url(#{gradient_id})"/>'
        )

        svg.append(f'<text x="{x + width / 2}" y="{y + 28}" ')
        svg.append('class="dbml-table-title" text-anchor="middle" fill="white" ')
        svg.append(
            f'font-size="16" font-weight="600">{self._escape_html(table.name)}</text>'
        )

        current_y = y + 66
        for idx, column in enumerate(table.columns):
            if idx > 0:
                svg.append(
                    f'<line x1="{x + 8}" y1="{current_y - 18}" x2="{x + width - 8}" y2="{current_y - 18}" '
                )
                svg.append('stroke="#f3f4f6" stroke-width="1"/>')
            svg.append(self._render_svg_field(column, x, current_y, width, table))
            current_y += 36

        svg.append("</g>")

        return "\n".join(svg)

    def _render_svg_field(self, column, x, y, width, table) -> str:
        svg = []

        name_color = "#1f2937"
        is_fk = False

        for ref in getattr(table, "_refs", []):
            if hasattr(ref, "col1") and ref.col1:
                for col in ref.col1:
                    if col.name == column.name:
                        is_fk = True
                        break

        tooltip_parts = [f"{column.name}: {column.type}"]
        if column.pk:
            tooltip_parts.append("PRIMARY KEY")
        if column.not_null:
            tooltip_parts.append("NOT NULL")
        if column.unique:
            tooltip_parts.append("UNIQUE")
        if column.default:
            tooltip_parts.append(f"DEFAULT: {column.default}")
        tooltip = " | ".join(tooltip_parts)

        svg.append(
            f'<g class="dbml-field-row" data-field="{table.name}.{column.name}">'
        )
        svg.append(
            f'<rect x="{x + 1}" y="{y - 16}" width="{width - 2}" height="34" fill="transparent" rx="4"/>'
        )
        svg.append(f"<title>{self._escape_html(tooltip)}</title>")

        icon_x = x + 10
        text_x = x + 30

        if column.pk:
            name_color = "#ef4444"
            svg.append(
                f'<svg x="{icon_x}" y="{y - 12}" width="16" height="16" viewBox="0 0 24 24">'
            )
            svg.append(
                '<path fill="#ef4444" d="M12 2C13.1 2 14 2.9 14 4C14 4.74 13.6 5.39 13 5.73V7H14C16.76 7 19 9.24 19 12V13H21V15H19V16H21V18H19V20H17V18H15V20H13V18H11V20H9V18H7V20H5V18H3V16H5V15H3V13H5V12C5 9.24 7.24 7 10 7H11V5.73C10.4 5.39 10 4.74 10 4C10 2.9 10.9 2 12 2Z"/>'
            )
            svg.append("</svg>")
        elif is_fk:
            name_color = "#10b981"
            svg.append(
                f'<svg x="{icon_x}" y="{y - 12}" width="16" height="16" viewBox="0 0 24 24">'
            )
            svg.append(
                '<path fill="#10b981" d="M10.59,13.41C11,13.8 11,14.44 10.59,14.83C10.2,15.22 9.56,15.22 9.17,14.83C7.22,12.88 7.22,9.71 9.17,7.76L12.71,4.22C14.66,2.27 17.83,2.27 19.78,4.22C21.73,6.17 21.73,9.34 19.78,11.29L18.29,12.78C18.3,11.96 18.17,11.14 17.89,10.36L18.36,9.88C19.54,8.71 19.54,6.81 18.36,5.64C17.19,4.46 15.29,4.46 14.12,5.64L10.59,9.17C9.41,10.34 9.41,12.24 10.59,13.41M13.41,9.17C13.8,8.78 14.44,8.78 14.83,9.17C16.78,11.12 16.78,14.29 14.83,16.24L11.29,19.78C9.34,21.73 6.17,21.73 4.22,19.78C2.27,17.83 2.27,14.66 4.22,12.71L5.71,11.22C5.7,12.04 5.83,12.86 6.11,13.65L5.64,14.12C4.46,15.29 4.46,17.19 5.64,18.36C6.81,19.54 8.71,19.54 9.88,18.36L13.41,14.83C14.59,13.66 14.59,11.76 13.41,10.59C13,10.2 13,9.56 13.41,9.17Z"/>'
            )
            svg.append("</svg>")

        svg.append(
            f'<text x="{text_x}" y="{y}" font-size="13" fill="{name_color}" font-weight="500" font-family="monospace">'
        )
        svg.append(f"{self._escape_html(column.name)}</text>")

        type_text = column.type
        if len(type_text) > 15:
            type_text = type_text[:12] + "..."

        svg.append(
            f'<text x="{x + 150}" y="{y}" font-size="11" fill="#7c3aed" font-family="monospace">'
        )
        svg.append(f"{self._escape_html(type_text)}</text>")

        badges_x = x + width - 14

        if column.not_null:
            svg.append(
                f'<svg x="{badges_x - 18}" y="{y - 12}" width="16" height="16" viewBox="0 0 24 24">'
            )
            svg.append(
                '<path fill="#f59e0b" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M11,7H13V9H11V7M11,11H13V17H11V11Z"/>'
            )
            svg.append("</svg>")
            badges_x -= 22

        if column.unique:
            svg.append(
                f'<svg x="{badges_x - 18}" y="{y - 12}" width="16" height="16" viewBox="0 0 24 24">'
            )
            svg.append(
                '<path fill="#3b82f6" d="M19,3H14.82C14.4,1.84 13.3,1 12,1C10.7,1 9.6,1.84 9.18,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M12,3A1,1 0 0,1 13,4A1,1 0 0,1 12,5A1,1 0 0,1 11,4A1,1 0 0,1 12,3M7,7H17V5H19V19H5V5H7V7M7.5,13.5L9,12L11,14L15.5,9.5L17,11L11,17L7.5,13.5Z"/>'
            )
            svg.append("</svg>")

        svg.append("</g>")

        return "".join(svg)

    def _render_relationship_line(self, ref) -> str:
        col1 = ref.col1[0] if ref.col1 else None
        col2 = ref.col2[0] if ref.col2 else None

        if not col1 or not col2:
            return ""

        table1_name = col1.table.name
        table2_name = col2.table.name
        field1_name = col1.name
        field2_name = col2.name

        if (
            table1_name not in self.field_positions
            or table2_name not in self.field_positions
        ):
            return ""
        if (
            field1_name not in self.field_positions[table1_name]
            or field2_name not in self.field_positions[table2_name]
        ):
            return ""

        _, y1_field = self.field_positions[table1_name][field1_name]
        _, y2_field = self.field_positions[table2_name][field2_name]

        from_idx = self._table_idx.get(table1_name, -1)
        to_idx = self._table_idx.get(table2_name, -1)

        from_rect = self._table_rects[from_idx] if from_idx >= 0 else (0, 0, 0, 0)
        to_rect = self._table_rects[to_idx] if to_idx >= 0 else (0, 0, 0, 0)

        waypoints, side_from, side_to = route_connection(
            from_rect,
            to_rect,
            y1_field,
            y2_field,
            from_idx,
            to_idx,
            self._table_rects,
            gap=20.0,
        )

        parts = [f"M {waypoints[0][0]} {waypoints[0][1]}"]
        for wx, wy in waypoints[1:]:
            parts.append(f"L {wx} {wy}")
        path = " ".join(parts)

        marker_start = ""
        marker_end = ""
        if ref.type == ">":
            marker_start = "url(#arrow-optional-start)"
            marker_end = "url(#arrow-many-end)"
        elif ref.type == "<":
            marker_start = "url(#arrow-many-start)"
            marker_end = "url(#arrow-one-end)"
        elif ref.type == "-":
            marker_start = "url(#arrow-one-start)"
            marker_end = "url(#arrow-one-end)"
        elif ref.type == "<>":
            marker_start = "url(#arrow-many-start)"
            marker_end = "url(#arrow-many-end)"

        line_color = self.colors["line_color"]

        svg = []
        svg.append(
            f'<g class="dbml-relationship-group" data-from="{table1_name}.{field1_name}" data-to="{table2_name}.{field2_name}">'
        )
        svg.append(
            f'<path d="{path}" stroke="transparent" stroke-width="12" fill="none" class="dbml-relationship-hit"/>'
        )
        svg.append(
            f'<path d="{path}" stroke="{line_color}" stroke-width="1.5" fill="none" '
        )
        svg.append(f'marker-start="{marker_start}" marker-end="{marker_end}" ')
        svg.append('class="dbml-relationship-line" opacity="0.7"/>')
        svg.append("</g>")

        return "".join(svg)

    def _escape_html(self, text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    @staticmethod
    def get_css(theme="default") -> str:
        base_css = """
        .dbml-diagram-wrapper {
            margin: 2rem 0;
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
            border-radius: 16px;
            border: 1px solid #e5e7eb;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
            position: relative;
            cursor: grab;
            user-select: none;
            height: 600px;
        }
        
        .dbml-controls {
            position: absolute;
            top: 1rem;
            right: 1rem;
            display: flex;
            gap: 0.5rem;
            z-index: 10;
        }
        
        .dbml-zoom-btn {
            background: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .dbml-zoom-btn:hover {
            background: #6366f1;
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3), 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .dbml-zoom-btn:hover::after {
            filter: brightness(0) invert(1);
        }
        
        .dbml-zoom-btn:active {
            transform: translateY(0) scale(0.95);
        }
        
        .dbml-legend {
            position: absolute;
            bottom: 1.5rem;
            left: 1.5rem;
            background: white;
            border: none;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            display: flex;
            gap: 1.5rem;
            font-size: 13px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
            z-index: 10;
        }
        
        .dbml-legend-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #4b5563;
            font-weight: 500;
        }
        
        .dbml-legend-item svg {
            flex-shrink: 0;
        }
        
        .dbml-legend-item span {
            white-space: nowrap;
        }
        
        .dbml-diagram {
            width: 100%;
            height: 100%;
            overflow: visible;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            will-change: transform;
            transform-origin: 0 0;
            pointer-events: none;
        }
        
        .dbml-table-group {
            cursor: pointer;
            will-change: transform;
            pointer-events: all;
        }
        
        .dbml-table-group:hover .dbml-table-bg {
            stroke: #6366f1;
            stroke-width: 3;
        }
        
        .dbml-field-row {
            cursor: help;
        }
        
        .dbml-field-row:hover text {
            font-weight: 600;
        }
        
        .dbml-table-title {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            user-select: none;
        }
        
        .dbml-relationship-line {
            opacity: 0.7;
            pointer-events: stroke;
            cursor: pointer;
            stroke-linecap: square;
        }
        
        .dbml-relationship-hit {
            pointer-events: stroke;
            cursor: pointer;
            stroke: transparent;
            fill: none;
        }
        
        .dbml-relationship-group {
            pointer-events: none;
        }
        
        .dbml-relationships-layer {
            pointer-events: none;
        }
        
        .dbml-relationship-line.selected {
            opacity: 1 !important;
            stroke-width: 3 !important;
            filter: drop-shadow(0 0 4px currentColor);
        }
        
        .dbml-field-row.selected rect {
            fill: rgba(99, 102, 241, 0.1);
        }
        
        .dbml-field-row.selected text {
            font-weight: 700 !important;
        }
        
        .dbml-rel-label {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            user-select: none;
            pointer-events: none;
        }
        
        .dbml-error {
            padding: 1rem 1.5rem;
            background: #fef2f2;
            border: 2px solid #ef4444;
            border-radius: 8px;
            color: #dc2626;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            margin: 2rem 0;
        }
        
        @media (max-width: 768px) {
            .dbml-diagram-wrapper {
                height: 400px;
            }
            
            .dbml-controls {
                top: 0.5rem;
                right: 0.5rem;
            }
            
            .dbml-zoom-btn {
                padding: 0.375rem 0.5rem;
                font-size: 12px;
            }
            
            .dbml-legend {
                position: static;
                margin-top: 1rem;
                flex-wrap: wrap;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .dbml-diagram-wrapper {
                background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
                border-color: #374151;
            }
            
            .dbml-legend {
                background: rgba(31, 41, 55, 0.95);
                backdrop-filter: blur(10px);
            }
            
            .dbml-legend-item {
                color: #e5e7eb;
            }
            
            .dbml-zoom-btn {
                background: rgba(31, 41, 55, 0.95);
                backdrop-filter: blur(10px);
                color: #e5e7eb;
            }
            
            .dbml-zoom-btn:hover {
                background: #818cf8;
            }
            
            .dbml-table-bg {
                fill: #111827;
                stroke: #374151;
            }
            
            .dbml-table-group:hover .dbml-table-bg {
                stroke: #818cf8;
                filter: drop-shadow(0 12px 24px rgba(129, 140, 248, 0.4));
            }
            
            .dbml-table-title {
                fill: white;
            }
            
            text {
                fill: #e5e7eb;
            }
            
            .dbml-relationship-line {
                stroke: #818cf8;
            }
            
            .dbml-rel-label {
                fill: white;
            }
            
            .dbml-relationship-line:hover {
                filter: drop-shadow(0 4px 12px rgba(129, 140, 248, 0.6));
            }
        }
        """

        return base_css
