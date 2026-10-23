"""End-to-end fixtures: build a real MkDocs site and drive it with Playwright."""

from __future__ import annotations

import functools
import http.server
import os
import threading
from pathlib import Path

import pytest

SITE_SRC = Path(__file__).parent / "fixture_site"


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs):
        pass


def pytest_collection_modifyitems(items):
    for item in items:
        if "/e2e/" in str(item.fspath).replace(os.sep, "/"):
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(scope="session")
def site_url(tmp_path_factory):
    from mkdocs.commands.build import build
    from mkdocs.config import load_config

    out = tmp_path_factory.mktemp("e2e-site")
    handler = functools.partial(_QuietHandler, directory=str(out))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"

    config = load_config(
        config_file=str(SITE_SRC / "mkdocs.yml"), site_dir=str(out), site_url=url
    )
    build(config)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield url
    server.shutdown()
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Allow running against a system Chromium: DBML_E2E_CHROMIUM=/usr/bin/chromium
    exe = os.environ.get("DBML_E2E_CHROMIUM")
    if exe:
        return {**browser_type_launch_args, "executable_path": exe}
    return browser_type_launch_args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 900},
        "permissions": ["clipboard-read", "clipboard-write"],
        "accept_downloads": True,
    }


@pytest.fixture
def home(page, site_url):
    page.goto(site_url)
    page.wait_for_selector(".dbml-diagram-wrapper[data-dbml-init]")
    page.wait_for_load_state("load")
    page.evaluate("document.fonts.ready")
    return page


@pytest.fixture
def wrapper(home):
    return home.locator(".dbml-diagram-wrapper").first


def center(locator):
    box = locator.bounding_box()
    assert box is not None
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def svg_transform(wrapper):
    return wrapper.locator(".dbml-diagram").evaluate("el => el.style.transform")


def scale_of(wrapper):
    import re

    return float(re.search(r"scale\(([\d.]+)\)", svg_transform(wrapper)).group(1))
