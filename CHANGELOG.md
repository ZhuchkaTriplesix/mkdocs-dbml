# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-08-23

### Added
- **Smooth Cubic Bézier Curves**: Modern, elegant relationship curves (matching dbdiagram.io / React Flow industry standard) with automatic horizontal tangent alignment for flush arrow markers.
- **Adaptive Port Selection**: Smart side selection (Left/Right) based on spatial facing orientation and canvas obstacle density.
- **Multi-Lane Concentric Corridors**: Automatic channel allocation (`lane_offset = i * 14px`) to prevent parallel relationships from overlapping.
- **Multi-Inbound Port Balancing**: Intelligent inbound port distribution across opposing sides of target tables to eliminate T-junction collisions on primary key fields.
- **Multi-Touch Pinch-to-Zoom**: Fluid two-finger pinch-to-zoom and two-finger panning for mobile and tablet devices.
- **MkDocs Material Dynamic Dark Theme**: Real-time palette sync supporting `[data-md-color-scheme="slate"]`, `[data-theme="dark"]`, and `.dark` classes without page reloads.

### Changed
- **Performance**: Instant $O(1)$ Bézier evaluation in `dbml.js` providing silky smooth 60 FPS interactive drag-and-drop animation.
- **Toolbar UI**: Unified 36x36px action buttons with rounded corners, translucent backdrop, accessible focus rings, and responsive mobile legend layout.
- **Collision Checking**: Strict table interior collision detection preventing connection lines from slicing through table cards or entering through top/bottom borders.

### Fixed
- Fixed global SVG text selector bleeding into parent theme document text.
- Fixed mobile legend clipping and overflow on narrow viewports.
- Fixed drag flickering and jitter by introducing hysteresis stability buffers.

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

[1.1.0]: https://github.com/ZhuchkaTriplesix/mkdocs-dbml/releases/tag/v1.1.0
[1.0.7]: https://github.com/ZhuchkaTriplesix/mkdocs-dbml/releases/tag/v1.0.7
[1.0.0]: https://github.com/ZhuchkaTriplesix/mkdocs-dbml/releases/tag/v1.0.0
[1.0.1]: https://github.com/ZhuchkaTriplesix/mkdocs-dbml/releases/tag/v1.0.1
