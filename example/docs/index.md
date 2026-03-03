# MkDocs DBML Plugin — Demo

Welcome! This plugin lets you embed **visual ERD diagrams** of your database directly into your MkDocs documentation.

Diagrams are rendered in a Mermaid/dbdiagram.io style with:
- Tables as cards with gradient headers
- **Field-to-field relationships** — lines run from the exact FK field to the exact PK field
- **Material Design 3 icons** — modern SVG icons
- **Drag & Drop** — drag tables with the mouse
- **Mouse wheel zoom** — scale the diagram
- Interactive hover effects and relationship highlighting

## Simple example

Here is a simple blog schema:

```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null, unique]
  email varchar(100) [not null]
  created_at timestamp [default: `now()`]
  
  Note: 'System users table'
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200) [not null]
  content text
  published boolean [default: false]
  created_at timestamp [default: `now()`]
  
  indexes {
    user_id
    (user_id, created_at)
  }
  
  Note: 'User posts'
}

Table comments {
  id integer [primary key]
  post_id integer [ref: > posts.id]
  user_id integer [ref: > users.id]
  content text [not null]
  created_at timestamp
  
  Note: 'Post comments'
}
```

## Features

- ✅ **Visual ERD diagrams** with SVG graphics
- ✅ **Field-to-field relationships** — lines run from FK to PK
- ✅ **Material Design 3 icons** — modern SVG icons
- ✅ **Drag & drop tables** — move them with the mouse
- ✅ **Mouse wheel zoom** — smooth scaling
- ✅ Automatic DBML parsing
- ✅ Graph-based layout algorithm
- ✅ Gradient headers (multiple color themes)
- ✅ Interactivity: hover effects, relationship highlighting
- ✅ Tooltips with full field information
- ✅ Legend with Material Design icons
- ✅ Responsive design for all devices
- ✅ Dark theme support with auto-detection

## How it works

1. You write DBML in a markdown code block
2. The plugin parses DBML and extracts tables, fields, and relationships
3. A graph-based algorithm computes table positions
4. An SVG diagram is generated with exact field positions
5. **Relationships are drawn from the specific FK field to the specific PK field**
6. Material Design icons and interactive effects are added
7. JavaScript handles drag & drop and mouse wheel zoom

## Interactivity

**Try it:**
- 🖱️ **Drag a table** — click and hold on a table, then move
- 🔍 **Zoom** — use the mouse wheel to zoom in/out
- ✨ **Hover a table** — see all its relationships highlighted
- 💡 **Hover a field** — a tooltip shows full information

See more examples on the [Examples](examples.md) page.

## Including a .dbml file

You can reference a native `.dbml` file — the path is relative to the `docs` directory:

```dbml
schema.dbml
```

The diagram above is rendered from `docs/schema.dbml`.
