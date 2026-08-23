"""
High-performance orthogonal edge routing with Numba JIT / NumPy.
Falls back to pure Python if Numba / NumPy is unavailable.
"""

try:
    import numpy as np
except ImportError:
    np = None

try:
    from numba import njit
except ImportError:

    def njit(f=None, **kw):
        if f is None:
            return lambda fn: fn
        return f


def _seg_hits_any_py(x1, y1, x2, y2, rects, n, skip1, skip2):
    pad = 5.0
    lo_x = min(x1, x2)
    hi_x = max(x1, x2)
    lo_y = min(y1, y2)
    hi_y = max(y1, y2)
    for i in range(n):
        if i == skip1 or i == skip2:
            continue
        rx, ry, rw, rh = rects[i]
        if (
            lo_x <= rx + rw + pad
            and hi_x >= rx - pad
            and lo_y <= ry + rh + pad
            and hi_y >= ry - pad
        ):
            return i
    return -1


def _path_hits_py(pts, rects, n_rects, skip1, skip2):
    for s in range(len(pts) - 1):
        hit = _seg_hits_any_py(
            pts[s][0],
            pts[s][1],
            pts[s + 1][0],
            pts[s + 1][1],
            rects,
            n_rects,
            skip1,
            skip2,
        )
        if hit >= 0:
            return hit
    return -1


def _path_cost_py(pts):
    cost = 0.0
    for i in range(len(pts) - 1):
        cost += abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1])
    return cost


def _route_one_py(sx, sy, ex, ey, skip1, skip2, rects, n, gap, sf="right", st="left"):
    y_lo = min(sy, ey)
    y_hi = max(sy, ey)

    if sf == "right" and st == "right":
        mid_x = max(sx, ex) + gap
        for _ in range(n):
            blocker = _seg_hits_any_py(mid_x, y_lo, mid_x, y_hi, rects, n, skip1, skip2)
            if blocker >= 0:
                bx, by, bw, bh = rects[blocker]
                mid_x = max(mid_x, bx + bw + gap)
            else:
                break
        return [(sx, sy), (mid_x, sy), (mid_x, ey), (ex, ey)]

    if sf == "left" and st == "left":
        mid_x = min(sx, ex) - gap
        for _ in range(n):
            blocker = _seg_hits_any_py(mid_x, y_lo, mid_x, y_hi, rects, n, skip1, skip2)
            if blocker >= 0:
                bx, by, bw, bh = rects[blocker]
                mid_x = min(mid_x, bx - gap)
            else:
                break
        return [(sx, sy), (mid_x, sy), (mid_x, ey), (ex, ey)]

    mid_x = (sx + ex) * 0.5

    blocker = _seg_hits_any_py(mid_x, y_lo, mid_x, y_hi, rects, n, skip1, skip2)
    if blocker < 0:
        return [(sx, sy), (mid_x, sy), (mid_x, ey), (ex, ey)]

    bx, by, bw, bh = rects[blocker]
    left_x = bx - gap
    right_x = bx + bw + gap

    left_ok = (
        _seg_hits_any_py(left_x, y_lo, left_x, y_hi, rects, n, skip1, skip2) < 0
    )
    right_ok = (
        _seg_hits_any_py(right_x, y_lo, right_x, y_hi, rects, n, skip1, skip2) < 0
    )

    if left_ok and right_ok:
        mid_x = left_x if abs(left_x - sx) < abs(right_x - sx) else right_x
    elif left_ok:
        mid_x = left_x
    elif right_ok:
        mid_x = right_x
    else:
        jog_y = by - gap if sy < by else by + bh + gap
        safe_x = left_x if abs(left_x - sx) < abs(right_x - sx) else right_x
        stub = gap if ex < sx else -gap
        return [
            (sx, sy),
            (safe_x, sy),
            (safe_x, jog_y),
            (ex + stub, jog_y),
            (ex + stub, ey),
            (ex, ey),
        ]

    return [(sx, sy), (mid_x, sy), (mid_x, ey), (ex, ey)]


def _route_connection_py(
    from_rect,
    to_rect,
    field_y_from,
    field_y_to,
    from_idx,
    to_idx,
    table_rects,
    gap=48.0,
):
    fx, fy, fw, fh = from_rect
    tx, ty, tw, th = to_rect
    n = len(table_rects)

    best_cost = 1e18
    best_wp = []
    best_sf = "right"
    best_st = "left"

    for sf_idx, sf in enumerate(("right", "left")):
        for st_idx, st in enumerate(("left", "right")):
            sx = fx + fw if sf_idx == 0 else fx
            ex = tx if st_idx == 0 else tx + tw

            backwards = (sf == "right" and st == "left" and sx >= ex) or (
                sf == "left" and st == "right" and sx <= ex
            )

            pts = _route_one_py(
                sx,
                field_y_from,
                ex,
                field_y_to,
                from_idx,
                to_idx,
                table_rects,
                n,
                gap,
                sf=sf,
                st=st,
            )
            hit = _path_hits_py(pts, table_rects, n, from_idx, to_idx)
            cost = _path_cost_py(pts)
            if hit >= 0:
                cost += 100000.0
            if backwards:
                cost += 50000.0

            if cost < best_cost:
                best_cost = cost
                best_wp = pts
                best_sf = sf
                best_st = st

    return best_wp, best_sf, best_st


if np is not None:

    @njit(cache=True)
    def _seg_hits_any(x1, y1, x2, y2, rects, n, skip1, skip2):
        """Check if an axis-aligned segment (x1,y1)-(x2,y2) overlaps any rect (with 5px padding)."""
        pad = 5.0
        lo_x = min(x1, x2)
        hi_x = max(x1, x2)
        lo_y = min(y1, y2)
        hi_y = max(y1, y2)
        for i in range(n):
            if i == skip1 or i == skip2:
                continue
            rx = rects[i, 0] - pad
            ry = rects[i, 1] - pad
            rr = rects[i, 0] + rects[i, 2] + pad
            rb = rects[i, 1] + rects[i, 3] + pad
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
    def _route_one(sx, sy, ex, ey, skip1, skip2, rects, n, gap, sf, st, out):
        """
        Build orthogonal polyline, write into out array.
        Returns number of waypoints written.
        """
        y_lo = min(sy, ey)
        y_hi = max(sy, ey)

        if sf == 0 and st == 1:  # right to right
            mid_x = max(sx, ex) + gap
            for _ in range(n):
                blocker = _seg_hits_any(mid_x, y_lo, mid_x, y_hi, rects, n, skip1, skip2)
                if blocker >= 0:
                    bx = rects[blocker, 0]
                    bw = rects[blocker, 2]
                    mid_x = max(mid_x, bx + bw + gap)
                else:
                    break
            out[0, 0] = sx
            out[0, 1] = sy
            out[1, 0] = mid_x
            out[1, 1] = sy
            out[2, 0] = mid_x
            out[2, 1] = ey
            out[3, 0] = ex
            out[3, 1] = ey
            return 4

        if sf == 1 and st == 0:  # left to left
            mid_x = min(sx, ex) - gap
            for _ in range(n):
                blocker = _seg_hits_any(mid_x, y_lo, mid_x, y_hi, rects, n, skip1, skip2)
                if blocker >= 0:
                    bx = rects[blocker, 0]
                    mid_x = min(mid_x, bx - gap)
                else:
                    break
            out[0, 0] = sx
            out[0, 1] = sy
            out[1, 0] = mid_x
            out[1, 1] = sy
            out[2, 0] = mid_x
            out[2, 1] = ey
            out[3, 0] = ex
            out[3, 1] = ey
            return 4

        mid_x = (sx + ex) * 0.5

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
                    sx = fx + fw
                else:
                    sx = fx
                if st == 0:
                    ex = tx
                else:
                    ex = tx + tw

                backwards = (sf == 0 and st == 0 and sx >= ex) or (
                    sf == 1 and st == 1 and sx <= ex
                )

                n_pts = _route_one(
                    sx, field_y_from, ex, field_y_to, skip1, skip2, rects, n, gap, sf, st, buf
                )

                hit = _path_hits(buf, n_pts, rects, n, skip1, skip2)
                cost = _path_cost(buf, n_pts)
                if hit >= 0:
                    cost += 100000.0
                if backwards:
                    cost += 50000.0

                if cost < best_cost:
                    best_cost = cost
                    best_n = n_pts
                    best_sf = sf
                    best_st = st
                    for i in range(n_pts):
                        best_buf[i, 0] = buf[i, 0]
                        best_buf[i, 1] = buf[i, 1]

        return best_buf, best_n, best_sf, best_st

    def _route_connection_np(
        from_rect,
        to_rect,
        field_y_from,
        field_y_to,
        from_idx,
        to_idx,
        table_rects,
        gap=48.0,
    ):
        fx, fy, fw, fh = from_rect
        tx, ty, tw, th = to_rect

        n = len(table_rects)
        rects = (
            table_rects
            if isinstance(table_rects, np.ndarray)
            else np.array(table_rects, dtype=np.float64)
        )

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

    route_connection = _route_connection_np
else:
    route_connection = _route_connection_py


def build_table_rects(positions, dimensions):
    names = list(positions.keys())
    idx_map = {}
    rects = []
    for i, name in enumerate(names):
        idx_map[name] = i
        px, py = positions[name]
        w, h = dimensions[name]
        rects.append((px, py, w, h))
    return names, idx_map, rects
