"""Tests for GraphLayoutEngine."""

import pytest
from pydbml import PyDBML
from mkdocs_dbml_plugin.layout import GraphLayoutEngine


def test_layout_single_table():
    parsed = PyDBML("Table a {\n  id integer [primary key]\n}")
    engine = GraphLayoutEngine(parsed.tables, parsed.refs)
    positions, dimensions = engine.calculate_positions()
    assert "a" in positions
    assert "a" in dimensions
    assert len(positions) == 1
    assert dimensions["a"][0] > 0
    assert dimensions["a"][1] > 0


def test_layout_two_tables():
    parsed = PyDBML("""
Table a {
  id integer [primary key]
}
Table b {
  id integer [primary key]
  a_id integer [ref: > a.id]
}
""")
    engine = GraphLayoutEngine(parsed.tables, parsed.refs)
    positions, dimensions = engine.calculate_positions()
    assert "a" in positions and "b" in positions
    assert len(positions) == 2


def test_layout_empty_returns_empty():
    engine = GraphLayoutEngine([], [])
    positions, dimensions = engine.calculate_positions()
    assert positions == {}
    assert dimensions == {}
