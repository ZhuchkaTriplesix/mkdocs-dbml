# MkDocs DBML Plugin

MkDocs plugin that renders [DBML](https://dbml.dbdiagram.io/) code blocks as interactive, visual ERD (Entity-Relationship Diagram) directly in your documentation.

## Features

- **Interactive SVG diagrams** — drag tables, zoom with mouse wheel, pan the canvas
- **Field-to-field connections** — relationship lines go from the exact FK field to the exact PK field
- **Orthogonal routing** — lines use right-angle paths and automatically avoid overlapping tables
- **Click-to-select** — click any relationship line to highlight it and its connected fields
- **Crow's foot notation** — classic ERD markers for one-to-one, one-to-many, many-to-many
- **Material Design 3 icons** — PK, FK, NOT NULL, UNIQUE badges on fields
- **7 color themes** — default, ocean, sunset, forest, dark, dark_gray, black
- **High performance** — optional Cython-compiled routing engine; Numba JIT fallback

## Installation

### From source (local project)

```bash
git clone https://github.com/ZhuchkaTriplesix/mkdocs-dbml.git
cd mkdocs-dbml
pip install -e .
```

### From source with Cython (optional, for best performance)

If you have a C compiler available (MSVC on Windows, gcc/clang on Linux/macOS):

```bash
pip install cython
python setup.py build_ext --inplace
pip install -e .
```

Without Cython the plugin works fine — it falls back to a pure-Python router.

### Dependencies

Installed automatically by `pip install`:

| Package | Purpose |
|---------|---------|
| `mkdocs >= 1.0` | Documentation framework |
| `pydbml >= 1.0` | DBML parser |

## Quick start

### 1. Enable the plugin in `mkdocs.yml`

```yaml
plugins:
  - search
  - dbml
```

### 2. Write DBML in any Markdown file

````markdown
```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null, unique]
  email varchar(100) [not null]
  created_at timestamp
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200) [not null]
  content text
  published boolean [default: false]
  created_at timestamp
}

Table comments {
  id integer [primary key]
  post_id integer [ref: > posts.id]
  user_id integer [ref: > users.id]
  content text [not null]
  created_at timestamp
}
```
````

### 3. Build or serve

```bash
mkdocs serve        # live preview at http://127.0.0.1:8000
mkdocs build        # static output in site/
```

The plugin converts every `` ```dbml `` code block into an interactive SVG diagram.

### Including native `.dbml` files

You can embed the contents of a `.dbml` file instead of pasting DBML inline. Paths are relative to your `docs_dir`.

**Option 1 — single line with path (must end with `.dbml`, no spaces):**

````markdown
```dbml
schema.dbml
```
````

**Option 2 — explicit `file:` or `include:` prefix:**

````markdown
```dbml
file: schemas/public.dbml
```
````

The file is read from `docs_dir` (e.g. `docs/schema.dbml` or `docs/schemas/public.dbml`). Path traversal (`../`) outside `docs_dir` is not allowed.

## Configuration

All options are set under the `dbml` plugin entry in `mkdocs.yml`:

```yaml
plugins:
  - dbml:
      theme: default      # color theme (see below)
      show_indexes: true   # display index information
      show_notes: true     # display table notes
```

### Themes

| Theme | Header gradient | Best for |
|-------|----------------|----------|
| `default` | Purple | Light backgrounds |
| `ocean` | Deep blue → cyan | Light backgrounds |
| `sunset` | Pink → blue | Light backgrounds |
| `forest` | Dark teal → green | Light backgrounds |
| `dark` | Dark violet | Dark backgrounds |
| `dark_gray` | Gray → slate | Dark backgrounds, neutral |
| `black` | Near-black → gray | Dark backgrounds, high contrast |

Example with the dark theme:

```yaml
plugins:
  - dbml:
      theme: dark
```

## DBML syntax cheat-sheet

```dbml
Table table_name {
  column_name column_type [attributes]
}
```

### Column attributes

| Attribute | Syntax |
|-----------|--------|
| Primary key | `[primary key]` or `[pk]` |
| Not null | `[not null]` |
| Unique | `[unique]` |
| Default value | `[default: value]` |
| Foreign key | `[ref: > other_table.column]` |

### Relationship types

| Syntax | Meaning | Markers |
|--------|---------|---------|
| `ref: > table.col` | Many-to-one | Circle → Crow's foot |
| `ref: < table.col` | One-to-many | Crow's foot → Bar |
| `ref: - table.col` | One-to-one | Bar → Bar |
| `ref: <> table.col` | Many-to-many | Crow's foot → Crow's foot |

### Indexes and notes

```dbml
Table example {
  id integer [pk]
  user_id integer
  post_id integer

  indexes {
    user_id
    (user_id, post_id) [unique]
  }

  Note: 'Description of this table'
}
```

Full DBML specification: [dbml.dbdiagram.io/docs](https://dbml.dbdiagram.io/docs/)

## Interaction guide

| Action | How |
|--------|-----|
| **Move a table** | Click and drag the table |
| **Pan the canvas** | Click and drag empty space |
| **Zoom** | Mouse wheel (10% – 300%) |
| **Fullscreen** | Click the expand button (top-right), Esc to exit |
| **Highlight connections** | Hover over a table |
| **Select a line** | Click on any relationship line |
| **Field tooltip** | Hover over a field row |

## Project structure

```
mkdocs-dbml/
├── setup.py                          # package config
├── requirements.txt
├── mkdocs_dbml_plugin/
│   ├── __init__.py
│   ├── plugin.py                     # MkDocs hook + interactive JS
│   ├── renderer.py                   # DBML → SVG rendering + CSS
│   ├── layout.py                     # BFS graph layout engine
│   ├── config.py                     # theme definitions
│   ├── routing.py                    # import wrapper (Cython → Python)
│   ├── _routing.pyx                  # Cython routing (optional)
│   └── _routing_py.py               # pure-Python routing fallback
└── example/                          # demo MkDocs site
    ├── mkdocs.yml
    └── docs/
        └── *.md
```

## License

MIT
