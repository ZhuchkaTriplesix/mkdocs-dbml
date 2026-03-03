# Contributing to mkdocs-dbml

Thanks for your interest in contributing.

## Development setup

```bash
git clone https://github.com/ZhuchkaTriplesix/mkdocs-dbml.git
cd mkdocs-dbml
pip install -e ".[dev]"   # if you add dev deps
# or
pip install -e .
cd example && mkdocs serve
```

Edit code in `mkdocs_dbml_plugin/`. The `example/` site uses the local plugin.

## Testing

- Run the example: `cd example && mkdocs serve` and check docs in the browser.
- Optionally install Cython and build: `pip install cython && python setup.py build_ext --inplace`.

## Pull requests

1. Fork the repo and create a branch.
2. Make your changes; keep the code style consistent.
3. Open a PR with a clear description and check the PR template.

## Reporting issues

Use [GitHub Issues](https://github.com/ZhuchkaTriplesix/mkdocs-dbml/issues). For bugs, please include:

- MkDocs and Python versions
- Minimal `mkdocs.yml` and DBML snippet to reproduce
- Expected vs actual behaviour

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
