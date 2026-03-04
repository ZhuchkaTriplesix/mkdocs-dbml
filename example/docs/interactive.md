# Interactive features

This plugin doesn’t just show static images — it builds **fully interactive diagrams**!

## 🖱️ Drag & drop tables

You can **drag tables** with the mouse to arrange them:

1. Move the cursor over any table
2. Click and hold the left mouse button
3. Drag the table where you want it
4. Release the button

Relationships are redrawn automatically when you move tables!

## 🔍 Mouse wheel zoom

**Smooth zoom** centered on the cursor:

- **Scroll up** — zoom in
- **Scroll down** — zoom out
- Scale range: 10% to 300%
- Zoom is centered on the cursor (like Google Maps)

You can also use the round buttons in the top-right corner.

## 📥 Export (SVG / PNG)

Use the **Export** buttons (top-right, next to fullscreen):

- **SVG** — downloads the diagram as a vector image (theme background included).
- **PNG** — downloads a raster image at 2× resolution.

The exported image includes all relationship lines and markers. The view is auto-fitted so every table is visible (no cropping).

## ✨ Relationship highlighting

When you hover a table:
- All its relationships become **bright and thick**
- Other relationships become **semi-transparent**
- Easy to see which tables the current one is connected to

## 💡 Field tooltips

Hover over any field to see a tooltip with:
- Field name and data type
- All attributes (PRIMARY KEY, NOT NULL, UNIQUE, DEFAULT)
- Full information in one line

## 🎯 Field-to-field relationships

Unlike tools where lines go from the center of a table:
- Lines go **from the specific FK field**
- **To the specific PK field**
- The diagram is **much clearer**
- You can see exactly which fields are related

## 🎨 Material Design 3

All icons follow Material Design 3:
- 🔑 **Key icon** for Primary Keys
- 🔗 **Link icon** for Foreign Keys
- ℹ️ **Info icon** for NOT NULL
- ✓ **Check icon** for UNIQUE

Icons are vector (SVG) and scale without quality loss.

## Example to try

Try all features on this diagram:

```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null, unique]
  email varchar(100) [not null, unique]
  password_hash varchar(255) [not null]
  created_at timestamp
  
  Note: 'System users'
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200) [not null]
  content text
  published boolean [default: false]
  views_count integer [default: 0]
  created_at timestamp
  
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

Table likes {
  id integer [primary key]
  user_id integer [ref: > users.id]
  post_id integer [ref: > posts.id]
  created_at timestamp
  
  indexes {
    (user_id, post_id) [unique]
  }
  
  Note: 'Post likes'
}
```

## Practice tasks

Try:

1. **Drag** the `users` table to the center of the diagram
2. **Zoom in** with the wheel to about 150–200%
3. **Hover** the `posts` table — see its relationships to `users`, `comments`, and `likes`
4. **Hover** the `user_id` field in `posts` — see the tooltip
5. **Follow** the line from `posts.user_id` to `users.id` — it goes exactly from field to field!

## Technical details

### Drag & drop
- Uses SVG `transform="translate(x, y)"`
- Position is preserved when zooming
- Smooth animation with `cubic-bezier(0.4, 0, 0.2, 1)`

### Zoom
- Zoom centered on cursor position
- Range: 0.1x – 3.0x
- Step: 10% per wheel tick
- Position recalculated to keep focus

### Relationships
- Position of each field is computed
- Line runs from the right edge of the FK field to the left edge of the PK field
- Bezier curves for smooth bends
- Automatic choice of markers (arrows, circles)

Enjoy the interactive diagrams! 🎉
