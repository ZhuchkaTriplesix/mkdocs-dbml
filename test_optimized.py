#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mkdocs_dbml_plugin.renderer import DbmlRenderer
from mkdocs_dbml_plugin.plugin import DbmlPlugin

dbml_code = """
Table users {
  id integer [primary key]
  username varchar(50) [not null, unique]
  email varchar(100) [not null]
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200) [not null]
  content text
}

Table comments {
  id integer [primary key]
  post_id integer [ref: > posts.id]
  user_id integer [ref: > users.id]
  content text [not null]
}
"""

print("Testing optimized version...")

renderer = DbmlRenderer()
html = renderer.render(dbml_code)

plugin = DbmlPlugin()
js = plugin._get_interactive_js()
css = DbmlRenderer.get_css()

with open("test_optimized.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Optimized DBML Diagram</title>
    <style>
    {css}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        padding: 2rem;
        background: #ffffff;
        margin: 0;
    }}
    h1 {{
        color: #1f2937;
        margin-bottom: 1rem;
    }}
    .features {{
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 1rem 1.5rem;
        margin: 1rem 0 2rem 0;
        border-radius: 4px;
    }}
    .features h3 {{
        margin: 0 0 0.75rem 0;
        color: #065f46;
    }}
    .features ul {{
        margin: 0;
        padding-left: 1.5rem;
    }}
    .features li {{
        color: #047857;
        margin: 0.5rem 0;
    }}
    </style>
</head>
<body>
    <h1>Оптимизированная версия</h1>
    
    <div class="features">
        <h3>Что исправлено:</h3>
        <ul>
            <li><strong>Производительность</strong> - используется requestAnimationFrame для плавного drag</li>
            <li><strong>Связи прикрепляются</strong> - динамически обновляются при перемещении</li>
            <li><strong>Стрелки "воронья лапка"</strong> - классический стиль как на картинке</li>
            <li><strong>Тонкие линии</strong> - stroke-width: 2px (вместо 2.5-3px)</li>
            <li><strong>Без пунктира</strong> - сплошные линии по умолчанию</li>
        </ul>
    </div>
    
    {html}
    
    <script>
    {js}
    </script>
</body>
</html>""")

print("Generated: test_optimized.html")
print()
print("Improvements:")
print("1. Performance - requestAnimationFrame for smooth dragging")
print("2. Connections update - dynamically recalculated when dragging")
print("3. Crow's foot arrows - classic ERD style")
print("4. Thinner lines - 2px stroke width")
print("5. No dashed lines - solid by default")
print()
print("Open test_optimized.html and try:")
print("- Drag a table - connections will follow!")
print("- Scroll mouse wheel - smooth zoom")
print("- Hover table - see connection highlights")
