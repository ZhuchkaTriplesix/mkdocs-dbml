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

- **Unit tests:** `pip install -e ".[dev]"` then `pytest tests/ -v`
- **Lint:** `ruff check .` (also available as `pre-commit install`); CI enforces it and a coverage floor (`pytest --cov`)
- **Example site:** `cd example && mkdocs serve` and check docs in the browser.
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


## Tests

```bash
pip install -e ".[dev]"
pytest tests --ignore=tests/e2e        # unit tests
```

### End-to-end (browser) tests

The e2e suite builds a real MkDocs site (Material, `navigation.instant`) from
`tests/e2e/fixture_site` and drives it with Playwright/Chromium.

```bash
pip install -e ".[e2e]"
playwright install chromium
pytest tests/e2e
```

Use a system Chromium instead of the downloaded one with
`DBML_E2E_CHROMIUM=/usr/bin/chromium pytest tests/e2e`. Known defects are
marked `xfail(strict=True)` with the issue number; fixing the bug makes the
test XPASS and fails the run, so remove the marker in the same PR.
