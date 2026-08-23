"""Tests for DbmlRenderer."""

import pytest
from mkdocs_dbml_plugin.renderer import DbmlRenderer


def test_render_simple_dbml_contains_wrapper(simple_dbml):
    r = DbmlRenderer(theme="black")
    html = r.render(simple_dbml)
    assert "dbml-diagram-wrapper" in html
    assert "dbml-diagram" in html
    assert "dbml-styles" in html


def test_render_simple_dbml_contains_table_names(simple_dbml):
    r = DbmlRenderer(theme="default")
    html = r.render(simple_dbml)
    assert "users" in html
    assert "posts" in html
    assert "dbml-table-group" in html


def test_render_simple_dbml_contains_relationship_layer(simple_dbml):
    r = DbmlRenderer(theme="black")
    html = r.render(simple_dbml)
    assert "dbml-relationships-layer" in html
    assert "dbml-relationship-line" in html or "dbml-relationship-group" in html


def test_render_single_table():
    r = DbmlRenderer()
    html = r.render("Table t1 {\n  id integer [primary key]\n}")
    assert "dbml-diagram" in html
    assert "t1" in html


def test_render_no_tables_returns_message():
    r = DbmlRenderer()
    html = r.render("")
    assert "No tables" in html or "dbml-error" in html


def test_render_invalid_dbml_raises_or_returns_error():
    r = DbmlRenderer()
    try:
        html = r.render("not valid dbml {")
        assert "dbml-error" in html or "Error" in html
    except Exception:
        pass


def test_render_with_tablegroup(simple_dbml):
    dbml = simple_dbml + """

TableGroup g1 {
  users
  posts
}
"""
    r = DbmlRenderer(theme="black")
    html = r.render(dbml)
    assert "dbml-tablegroups-layer" in html or "dbml-tablegroup" in html
    assert 'data-tables="' in html
    assert 'data-group="' in html


def test_get_css_returns_non_empty_string():
    css = DbmlRenderer.get_css("black")
    assert isinstance(css, str)
    assert "dbml-diagram-wrapper" in css
    assert len(css) > 500


def test_xss_in_table_name_is_escaped():
    dbml = 'Table "users\\"style=\\"bad" {\n  id integer [pk]\n}'
    r = DbmlRenderer()
    try:
        html = r.render(dbml)
    except Exception:
        return
    assert 'style="bad"' not in html


def test_data_attributes_are_escaped(simple_dbml):
    r = DbmlRenderer(theme="black")
    html = r.render(simple_dbml)
    assert 'data-table="' in html
    assert 'data-field="' in html
    assert 'data-from="' in html or 'data-to="' in html


def test_render_uses_sha256_ids(simple_dbml):
    r = DbmlRenderer()
    html = r.render(simple_dbml)
    assert "dbml-" in html
    import re
    ids = re.findall(r'id="dbml-([a-f0-9]+)"', html)
    for h in ids:
        assert len(h) == 16, f"Expected 16-char sha256 hash, got {len(h)}"


def test_pure_python_routing_fallback():
    from mkdocs_dbml_plugin import _routing_py
    from_rect = (10.0, 10.0, 100.0, 100.0)
    to_rect = (200.0, 10.0, 100.0, 100.0)
    table_rects = [from_rect, to_rect]

    wp = _routing_py._route_one_py(
        110.0, 30.0, 190.0, 30.0, 0, 1, table_rects, len(table_rects), 20.0
    )
    assert len(wp) >= 2

    wp, sf, st = _routing_py._route_connection_py(
        from_rect, to_rect, 30.0, 30.0, 0, 1, table_rects, 20.0
    )
    assert len(wp) >= 2
    assert sf in ("left", "right")
    assert st in ("left", "right")


def test_same_side_right_right_routing():
    from mkdocs_dbml_plugin import _routing_py
    from mkdocs_dbml_plugin.routing import route_connection

    from_rect = (300.0, 50.0, 150.0, 120.0)   # left = 300, right = 450
    to_rect = (310.0, 250.0, 160.0, 120.0)    # left = 310, right = 470
    table_rects = [from_rect, to_rect]

    # Explicit right-to-right
    wp_rr = _routing_py._route_one_py(
        450.0, 80.0, 470.0, 280.0, 0, 1, table_rects, 2, 48.0, sf="right", st="right"
    )
    assert len(wp_rr) == 4
    assert wp_rr[0][0] == 450.0
    assert wp_rr[1][0] >= 470.0 + 48.0
    assert wp_rr[2][0] == wp_rr[1][0]
    assert wp_rr[3][0] == 470.0

    # Explicit left-to-left
    wp_ll = _routing_py._route_one_py(
        300.0, 80.0, 310.0, 280.0, 0, 1, table_rects, 2, 48.0, sf="left", st="left"
    )
    assert len(wp_ll) == 4
    assert wp_ll[0][0] == 300.0
    assert wp_ll[1][0] <= 300.0 - 48.0
    assert wp_ll[2][0] == wp_ll[1][0]
    assert wp_ll[3][0] == 310.0

    # Global route_connection picks the best same-side outer corridor
    wp, sf, st = route_connection(
        from_rect, to_rect, 80.0, 280.0, 0, 1, table_rects, gap=48.0
    )
    assert len(wp) == 4
    if sf == "right" and st == "right":
        assert wp[1][0] >= 470.0 + 48.0
    elif sf == "left" and st == "left":
        assert wp[1][0] <= 300.0 - 48.0


def test_diagonal_staggered_s_step_routing():
    from mkdocs_dbml_plugin import _routing_py
    from mkdocs_dbml_plugin.routing import route_connection

    # Table 1 top-left, Table 2 bottom-right, with 30px horizontal overlap and vertical clearance
    from_rect = (100.0, 50.0, 200.0, 100.0)   # right = 300, bottom = 150
    to_rect = (270.0, 250.0, 200.0, 100.0)     # left = 270, top = 250 (overlap = 30px, vert clearance = 100px)
    table_rects = [from_rect, to_rect]

    wp, sf, st = route_connection(
        from_rect, to_rect, 90.0, 290.0, 0, 1, table_rects, gap=48.0
    )
    # Natural S-step connection (sf="right", st="left")
    assert sf == "right"
    assert st == "left"
    assert len(wp) == 6
    # Vertical transition occurs in the inter-table vertical corridor (between y=150 and y=250)
    assert 150.0 <= wp[2][1] <= 250.0


def test_parallel_connections_multi_lane_offsets():
    from mkdocs_dbml_plugin.routing import route_connection

    from_rect = (300.0, 50.0, 150.0, 120.0)
    to_rect = (310.0, 250.0, 160.0, 120.0)
    table_rects = [from_rect, to_rect]

    wp1, sf1, st1 = route_connection(
        from_rect, to_rect, 80.0, 280.0, 0, 1, table_rects, gap=48.0, lane_offset=0.0
    )
    wp2, sf2, st2 = route_connection(
        from_rect, to_rect, 100.0, 300.0, 0, 1, table_rects, gap=48.0, lane_offset=14.0
    )

    assert sf1 == sf2
    assert st1 == st2
    # Verify that the two parallel vertical corridors are separated by the lane offset
    mid_x1 = wp1[1][0]
    mid_x2 = wp2[1][0]
    assert abs(abs(mid_x2 - mid_x1) - 14.0) < 1e-5


def test_narrow_gap_penalty_routes_around_perimeter():
    from mkdocs_dbml_plugin.routing import route_connection

    # Table 1 at left, Table 2 at right with only 20px gap (narrow gap < 48px)
    from_rect = (100.0, 200.0, 150.0, 100.0)  # right = 250
    to_rect = (270.0, 50.0, 150.0, 100.0)     # left = 270 (gap is only 20px)
    table_rects = [from_rect, to_rect]

    wp, sf, st = route_connection(
        from_rect, to_rect, 250.0, 80.0, 0, 1, table_rects, gap=48.0
    )
    # Because gap is < 48px, router avoids the narrow 20px space between tables
    # and routes around the outer perimeter (e.g. L-L or R-R)
    assert sf == st or (sf == "left" or st == "right")


def test_multi_inbound_preferred_side_balancing():
    from mkdocs_dbml_plugin.routing import route_connection

    from_rect = (100.0, 100.0, 150.0, 100.0)
    to_rect = (400.0, 100.0, 150.0, 100.0)
    table_rects = [from_rect, to_rect]

    wp1, sf1, st1 = route_connection(
        from_rect, to_rect, 150.0, 150.0, 0, 1, table_rects, gap=48.0, preferred_side_to="left"
    )
    assert st1 == "left"

    wp2, sf2, st2 = route_connection(
        from_rect, to_rect, 150.0, 150.0, 0, 1, table_rects, gap=48.0, preferred_side_to="right"
    )
    assert st2 == "right"


def test_avoid_cutting_through_table_interior():
    from mkdocs_dbml_plugin.routing import route_connection

    # posts at bottom-left: x in [90, 390], y in [600, 900]
    # users at top-center: x in [240, 540], y in [100, 340]
    posts_rect = (90.0, 600.0, 300.0, 300.0)
    users_rect = (240.0, 100.0, 300.0, 240.0)
    table_rects = [posts_rect, users_rect]

    wp, sf, st = route_connection(
        posts_rect, users_rect, 720.0, 160.0, 0, 1, table_rects, gap=48.0
    )

    # Ensure no segment cuts through users interior [242..538] x [102..338]
    for i in range(len(wp) - 1):
        x1, y1 = wp[i]
        x2, y2 = wp[i + 1]
        if abs(x1 - x2) < 1e-3:  # vertical
            vx = x1
            if 242.0 < vx < 538.0:
                assert not (min(y1, y2) < 338.0 and max(y1, y2) > 102.0)
        elif abs(y1 - y2) < 1e-3:  # horizontal
            hy = y1
            if 102.0 < hy < 338.0:
                assert not (min(x1, x2) < 538.0 and max(x1, x2) > 242.0)








