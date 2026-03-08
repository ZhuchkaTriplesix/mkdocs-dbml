# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-27

### Added

- Interactive ERD diagrams from DBML code blocks in MkDocs
- Field-to-field relationship lines with orthogonal routing (lines avoid tables)
- Drag & drop tables, pan canvas, mouse wheel zoom
- Click relationship line to highlight it and connected fields
- Fullscreen mode (button top-right)
- 7 color themes: default, ocean, sunset, forest, dark, dark_gray, black
- Embedding native `.dbml` files: `file: path/schema.dbml` or single-line path in a dbml block
- Crow's foot notation (one, many, optional)
- Material Design 3 icons for PK, FK, Not Null, Unique
- Optional Cython routing for performance; Numba JIT / pure Python fallback

### Changed

- N/A (initial stable release)

### Fixed

- N/A

## [1.0.7] - 2026-02-27

### Added

- Table groups: drag individual tables (group rect auto-resizes); drag group background to move all tables together
- Example page `groups.md` with identity/catalog/sales groups

### Fixed

- Group background not receiving pointer events (pointer-events: fill on .dbml-tablegroup-bg)

## [1.0.6] - 2026-02-27

### Security

- Escape DBML table/column names in SVG `data-*` attributes to prevent XSS
- Escape error messages and file paths in plugin HTML output

### Changed

- Diagram/gradient/clip IDs use SHA256 (16 chars) instead of MD5 (8 chars)
- Layout and renderer use named constants (HEADER_HEIGHT, ROW_HEIGHT, etc.) from config
- Theme validation: warn in `on_config` when theme is unknown, list available themes
- Interactive JS moved to `mkdocs_dbml_plugin/assets/dbml.js` (load once, no inline string)
- Export clone matches table groups by `data-table` attribute instead of DOM index
- Narrow exception handling: catch ValueError/KeyError for parse errors; log full traceback for unexpected errors
- Remove `<!-- dbml-styles -->` marker from final HTML after injecting CSS/JS

### Added

- Tests for XSS escaping, SHA256 IDs, theme warning, post_page injection, error escaping

## [1.0.5] - 2026-02-27

### Added

- TableGroup support (visual grouping with rounded border and label)
- Export diagram as SVG or PNG (buttons in diagram controls)
- Export uses theme background color (`data-bg`)

### Fixed

- Export SVG/PNG: relationship lines now visible (inline styles, remove hit paths)
- Export: viewBox recalculated from table positions so nothing is cut off
- Export: markers (arrows, circles) no longer overwritten; larger stroke for visibility
- Export: dark theme background in downloaded SVG/PNG

[1.0.0]: https://github.com/ZhuchkaTriplesix/mkdocs-dbml/releases/tag/v1.0.0
[1.0.1]: https://github.com/ZhuchkaTriplesix/mkdocs-dbml/releases/tag/v1.0.1
