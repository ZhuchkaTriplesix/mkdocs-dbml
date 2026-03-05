# Color themes

The plugin supports several color themes for diagrams. The **default theme is black** (high contrast, OLED-friendly). Override it in `mkdocs.yml` if you prefer another theme.

## Black (default)

Near-black background, white/gray lines and text. Best for dark docs and OLED screens.

## Default (purple)

Classic purple theme with a gradient from indigo to purple.

```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null]
  email varchar(100) [unique]
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200)
}
```

## How to change the theme

In `mkdocs.yml`:

```yaml
plugins:
  - dbml:
      theme: black  # default; or default, ocean, sunset, forest, dark, dark_gray
```

## Available themes

### 🌊 Ocean
Blue sea theme — great for technical documentation.

### 🌅 Sunset
Pink-to-blue gradient — bright and modern.

### 🌲 Forest
Green theme — calm and professional.

### 🌙 Dark / Dark gray / Black
Dark themes for dark-mode UIs.

## Customization

Want your own theme? Edit `mkdocs_dbml_plugin/config.py`:

```python
THEMES = {
    'my_theme': {
        'gradient_start': '#FF6B6B',
        'gradient_end': '#4ECDC4',
        'line_color': '#45B7D1',
        'bg_color': '#f8f9fa',
        'border_color': '#dee2e6',
    }
}
```

Then use it:

```yaml
plugins:
  - dbml:
      theme: my_theme
```

## Choosing a theme

- **Black** — default; dark, high contrast, OLED-friendly
- **Default** — purple gradient; universal for light docs
- **Ocean** — technical projects, API docs
- **Sunset** — creative projects, startups
- **Forest** — corporate documentation
- **Dark / Dark gray** — alternative dark themes

All themes are responsive and look good on any screen.
