# Installation and usage

## Development setup

1. Clone the repository:
```bash
git clone https://github.com/ZhuchkaTriplesix/mkdocs-dbml.git
cd mkdocs-dbml
```

2. Install dependencies (optional; pip will install runtime deps):
```bash
pip install -r requirements.txt
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
```

Diagrams include **Export** buttons (top-right): download as SVG or PNG. The exported image uses the theme background and includes all relationship lines.

## Publishing the package

To publish to PyPI:

```bash
pip install build twine
python -m build
twine upload dist/*
```
