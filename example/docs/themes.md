# Color themes

The plugin supports several color themes for diagrams. Pick one that fits your documentation!

## Default

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
      theme: ocean  # choose: default, ocean, sunset, forest, dark, dark_gray, black
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

- **Default** — universal, works for any docs
- **Ocean** — technical projects, API docs
- **Sunset** — creative projects, startups
- **Forest** — corporate documentation
- **Dark** — dark-mode sites

All themes are responsive and look good on any screen.
