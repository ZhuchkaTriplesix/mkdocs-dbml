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

## [1.0.1] - 2026-02-27

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
