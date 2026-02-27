"""
Routing module: tries Cython first, falls back to Numba JIT / pure Python.
"""

try:
    from ._routing import route_connection, build_table_rects
except ImportError:
    from ._routing_py import route_connection, build_table_rects

__all__ = ["route_connection", "build_table_rects"]
