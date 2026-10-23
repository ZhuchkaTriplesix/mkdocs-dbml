# Installation and usage

## Development setup

1. Clone the repository:
```bash
git clone https://github.com/ZhuchkaTriplesix/mkdocs-dbml.git
cd mkdocs-dbml
```

2. Install dev dependencies (tests, lint):
```bash
pip install -e ".[dev]"
```

3. Install the plugin in development mode:
```bash
pip install -e .
```

## Testing with the example

1. Go to the example directory:
```bash
cd example
```

2. Start the MkDocs server:
```bash
mkdocs serve
```

3. Open your browser at `http://127.0.0.1:8000`

## Using in your project

1. Install the plugin:
```bash
pip install mkdocs-dbml-plugin
```

2. Add to `mkdocs.yml`:
```yaml
plugins:
  - search
  - dbml
```

3. Use DBML in markdown:
````markdown
```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null]
  email varchar(100) [not null, unique]
}
```
````

## Configuration

Available options:

```yaml
plugins:
  - dbml:
      theme: black    # default; or default, ocean, sunset, forest, dark, dark_gray
      show_indexes: true
      show_notes: true
      height: 600     # diagram height in px
```

Diagrams include **Export** buttons (top-right): download as SVG or PNG. The exported image uses the theme background and includes all relationship lines.

## Publishing the package

Releases are automated: bump the version in `pyproject.toml` and `mkdocs_dbml_plugin/__init__.py`, add a `CHANGELOG.md` section, merge `release/vX.Y.Z` into `master` and push the `vX.Y.Z` tag. The `Release` workflow runs the tests, builds the package, publishes to PyPI and creates a GitHub Release.
