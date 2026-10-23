"""SVG / PNG export."""

from __future__ import annotations

import struct



def read_download(download):
    path = download.path()
    with open(path, "rb") as fh:
        return fh.read()


def test_svg_export(home, wrapper):
    with home.expect_download() as info:
        wrapper.locator(".dbml-export-svg-btn").click()
    download = info.value
    assert download.suggested_filename.endswith(".svg")
    assert download.suggested_filename.startswith("diagram-dbml-")
    svg = read_download(download).decode("utf-8")
    assert svg.lstrip().startswith("<svg")
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg
    assert 'data-table="users"' in svg and 'data-table="comments"' in svg
    assert "relationship-hit" not in svg  # interaction helpers are stripped
    assert "<rect" in svg and 'fill="#000000"' in svg  # theme background


def test_png_export(home, wrapper):
    with home.expect_download() as info:
        wrapper.locator(".dbml-export-png-btn").click()
    download = info.value
    assert download.suggested_filename.endswith(".png")
    data = read_download(download)
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    assert width > 400 and height > 300


def test_export_reflects_moved_tables(home, wrapper):
    users = wrapper.locator('.dbml-table-group[data-table="users"]')
    users.focus()
    home.keyboard.press("ArrowRight")
    with home.expect_download() as info:
        wrapper.locator(".dbml-export-svg-btn").click()
    svg = read_download(info.value).decode("utf-8")
    assert "translate(" in svg


def test_second_diagram_exports_with_distinct_name(home):
    first, second = home.locator(".dbml-diagram-wrapper").all()
    names = []
    for w in (first, second):
        with home.expect_download() as info:
            w.locator(".dbml-export-svg-btn").click()
        names.append(info.value.suggested_filename)
    assert names[0] != names[1]
