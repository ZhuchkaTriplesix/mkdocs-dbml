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


def test_layout_is_deterministic_across_hash_seeds():
    import hashlib
    import os
    import subprocess
    import sys

    dbml = """
Table a {
  id integer
}
Table b {
  id integer
  a_id integer [ref: > a.id]
}
Table c {
  id integer
  a_id integer [ref: > a.id]
}
Table d {
  id integer
  a_id integer [ref: > a.id]
}
Table e {
  id integer
  b_id integer [ref: > b.id]
  c_id integer [ref: > c.id]
}
"""
    code = (
        "from pydbml import PyDBML\n"
        "from mkdocs_dbml_plugin.layout import GraphLayoutEngine\n"
        f"p = PyDBML({dbml!r})\n"
        "print(sorted(GraphLayoutEngine(p.tables, p.refs).calculate_positions()[0].items()))\n"
    )
    outputs = set()
    for seed in ("1", "2", "3", "4", "5", "6", "7", "8"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        res = subprocess.run(
            [sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True
        )
        outputs.add(hashlib.md5(res.stdout.encode()).hexdigest())
    assert len(outputs) == 1
