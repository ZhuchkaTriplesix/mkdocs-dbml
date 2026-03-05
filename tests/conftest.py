"""Pytest fixtures for mkdocs-dbml-plugin tests."""

import pytest


SIMPLE_DBML = """
Table users {
  id integer [primary key]
  username varchar(50) [not null]
  email varchar(100)
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200)
}
"""


@pytest.fixture
def simple_dbml():
    return SIMPLE_DBML.strip()
