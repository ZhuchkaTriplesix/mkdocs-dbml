"""
High-performance orthogonal edge routing with Numba JIT.
Falls back to pure Python if Numba is unavailable.
"""

import numpy as np

try:
    from numba import njit

    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

    def njit(f=None, **kw):
        if f is None:
            return lambda fn: fn
        return f


@njit(cache=True)
def _seg_hits_any(x1, y1, x2, y2, rects, n, skip1, skip2):
    """Check if an axis-aligned segment (x1,y1)-(x2,y2) overlaps any rect (with 5px padding)."""
    cdef_pad = 5.0
    lo_x = min(x1, x2)
    hi_x = max(x1, x2)
    lo_y = min(y1, y2)
    hi_y = max(y1, y2)
    for i in range(n):
        if i == skip1 or i == skip2:
            continue
        rx = rects[i, 0] - cdef_pad
        ry = rects[i, 1] - cdef_pad
        rr = rects[i, 0] + rects[i, 2] + cdef_pad
        rb = rects[i, 1] + rects[i, 3] + cdef_pad
        if lo_x <= rr and hi_x >= rx and lo_y <= rb and hi_y >= ry:
            return i
    return -1


@njit(cache=True)
def _path_hits(pts, n_pts, rects, n_rects, skip1, skip2):
    """Check if any segment of the polyline hits a table."""
    for s in range(n_pts - 1):
        hit = _seg_hits_any(
            pts[s, 0],
            pts[s, 1],
            pts[s + 1, 0],
            pts[s + 1, 1],
            rects,
            n_rects,
            skip1,
            skip2,
        )
        if hit >= 0:
            return hit
    return -1


@njit(cache=True)
def _path_cost(pts, n_pts):
    """Manhattan length of polyline."""
    cost = 0.0
    for i in range(n_pts - 1):
        cost += abs(pts[i + 1, 0] - pts[i, 0]) + abs(pts[i + 1, 1] - pts[i, 1])
    return cost


@njit(cache=True)
def _route_one(sx, sy, ex, ey, skip1, skip2, rects, n, gap, out):
    """
    Build orthogonal polyline, write into out array.
    Returns number of waypoints written.
    """
    mid_x = (sx + ex) * 0.5
    y_lo = min(sy, ey)
    y_hi = max(sy, ey)

    blocker = _seg_hits_any(mid_x, y_lo, mid_x, y_hi, rects, n, skip1, skip2)
    if blocker < 0:
        out[0, 0] = sx
        out[0, 1] = sy
        out[1, 0] = mid_x
        out[1, 1] = sy
        out[2, 0] = mid_x
        out[2, 1] = ey
        out[3, 0] = ex
        out[3, 1] = ey
        return 4

    bx = rects[blocker, 0]
    by = rects[blocker, 1]
    bw = rects[blocker, 2]
    bh = rects[blocker, 3]

    left_x = bx - gap
    right_x = bx + bw + gap

    left_ok = _seg_hits_any(left_x, y_lo, left_x, y_hi, rects, n, skip1, skip2) < 0
    right_ok = _seg_hits_any(right_x, y_lo, right_x, y_hi, rects, n, skip1, skip2) < 0

    if left_ok and right_ok:
        if abs(left_x - sx) < abs(right_x - sx):
            mid_x = left_x
        else:
            mid_x = right_x
    elif left_ok:
        mid_x = left_x
    elif right_ok:
        mid_x = right_x
    else:
        if sy < by:
            jog_y = by - gap
        else:
            jog_y = by + bh + gap
        if abs(left_x - sx) < abs(right_x - sx):
            safe_x = left_x
        else:
            safe_x = right_x
        stub = gap if ex < sx else -gap
        out[0, 0] = sx
        out[0, 1] = sy
        out[1, 0] = safe_x
        out[1, 1] = sy
        out[2, 0] = safe_x
        out[2, 1] = jog_y
        out[3, 0] = ex + stub
        out[3, 1] = jog_y
        out[4, 0] = ex + stub
        out[4, 1] = ey
        out[5, 0] = ex
        out[5, 1] = ey
        return 6

    out[0, 0] = sx
    out[0, 1] = sy
    out[1, 0] = mid_x
    out[1, 1] = sy
    out[2, 0] = mid_x
    out[2, 1] = ey
    out[3, 0] = ex
    out[3, 1] = ey
    return 4


@njit(cache=True)
def _find_best(
    fx,
    fy,
    fw,
    fh,
    tx,
    ty,
    tw,
    th,
    field_y_from,
    field_y_to,
    skip1,
    skip2,
    rects,
    n,
    gap,
):
    """Try all 4 side combos, return best waypoints + side indices."""
    buf = np.empty((6, 2), dtype=np.float64)
    best_buf = np.empty((6, 2), dtype=np.float64)
    best_n = 0
    best_cost = 1e18
    best_sf = 0
    best_st = 0

    for sf in range(2):
        for st in range(2):
            if sf == 0:
                sx = fx + fw + 12.0
            else:
                sx = fx - 12.0
            if st == 0:
                ex = tx - 12.0
            else:
                ex = tx + tw + 12.0

            n_pts = _route_one(
                sx, field_y_from, ex, field_y_to, skip1, skip2, rects, n, gap, buf
            )

            hit = _path_hits(buf, n_pts, rects, n, skip1, skip2)
            cost = _path_cost(buf, n_pts)
            if hit >= 0:
                cost += 100000.0

            if cost < best_cost:
                best_cost = cost
                best_n = n_pts
                best_sf = sf
                best_st = st
                for i in range(n_pts):
                    best_buf[i, 0] = buf[i, 0]
                    best_buf[i, 1] = buf[i, 1]

    return best_buf, best_n, best_sf, best_st


def route_connection(
    from_rect,
    to_rect,
    field_y_from,
    field_y_to,
    from_idx,
    to_idx,
    table_rects,
    gap=20.0,
):
    fx, fy, fw, fh = from_rect
    tx, ty, tw, th = to_rect

    n = len(table_rects)
    rects = np.array(table_rects, dtype=np.float64)

    buf, n_pts, sf, st = _find_best(
        fx,
        fy,
        fw,
        fh,
        tx,
        ty,
        tw,
        th,
        field_y_from,
        field_y_to,
        from_idx,
        to_idx,
        rects,
        n,
        gap,
    )

    waypoints = [(buf[i, 0], buf[i, 1]) for i in range(n_pts)]
    side_from = "right" if sf == 0 else "left"
    side_to = "left" if st == 0 else "right"
    return waypoints, side_from, side_to


def build_table_rects(positions, dimensions):
    names = sorted(positions.keys())
    idx_map = {}
    rects = []
    for i, name in enumerate(names):
        idx_map[name] = i
        px, py = positions[name]
        w, h = dimensions[name]
        rects.append((px, py, w, h))
    return names, idx_map, rects
