# cython: boundscheck=False, wraparound=False, cdivision=True
from libc.math cimport fabs
from libc.stdlib cimport malloc, free

cdef struct Rect:
    double x, y, w, h


cdef int _overlaps_v(double vx, double y_lo, double y_hi,
                     Rect *rects, int n, int skip1, int skip2) noexcept nogil:
    cdef int i
    cdef Rect r
    cdef double pad = 5.0
    for i in range(n):
        if i == skip1 or i == skip2:
            continue
        r = rects[i]
        if r.x - pad <= vx <= r.x + r.w + pad:
            if not (y_hi < r.y - pad or y_lo > r.y + r.h + pad):
                return i
    return -1


cdef double _path_cost(list waypoints):
    cdef double cost = 0.0
    cdef int i
    cdef double x1, y1, x2, y2
    for i in range(len(waypoints) - 1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i + 1]
        cost += fabs(x2 - x1) + fabs(y2 - y1)
    return cost


cdef list _route_one(double sx, double sy, double ex, double ey,
                     int skip1, int skip2, Rect *rects, int n, double gap):
    cdef double mid_x = (sx + ex) / 2.0
    cdef double y_lo = sy if sy < ey else ey
    cdef double y_hi = sy if sy > ey else ey
    cdef int blocker, dummy
    cdef double left_x, right_x, jog_y, safe_x, stub
    cdef bint left_ok, right_ok

    blocker = _overlaps_v(mid_x, y_lo, y_hi, rects, n, skip1, skip2)
    if blocker < 0:
        return [(sx, sy), (mid_x, sy), (mid_x, ey), (ex, ey)]

    left_x = rects[blocker].x - gap
    right_x = rects[blocker].x + rects[blocker].w + gap

    left_ok = _overlaps_v(left_x, y_lo, y_hi, rects, n, skip1, skip2) < 0
    right_ok = _overlaps_v(right_x, y_lo, y_hi, rects, n, skip1, skip2) < 0

    if left_ok and right_ok:
        mid_x = left_x if fabs(left_x - sx) < fabs(right_x - sx) else right_x
    elif left_ok:
        mid_x = left_x
    elif right_ok:
        mid_x = right_x
    else:
        if sy < rects[blocker].y:
            jog_y = rects[blocker].y - gap
        else:
            jog_y = rects[blocker].y + rects[blocker].h + gap
        safe_x = left_x if fabs(left_x - sx) < fabs(right_x - sx) else right_x
        stub = gap if ex < sx else -gap
        return [
            (sx, sy), (safe_x, sy), (safe_x, jog_y),
            (ex + stub, jog_y), (ex + stub, ey), (ex, ey),
        ]

    return [(sx, sy), (mid_x, sy), (mid_x, ey), (ex, ey)]


def route_connection(from_rect, to_rect, field_y_from, field_y_to,
                     from_idx, to_idx, table_rects, gap=20.0):
    cdef int n = len(table_rects)
    cdef Rect *rects = <Rect *>malloc(n * sizeof(Rect))
    if rects == NULL:
        return [(0, 0), (0, 0)], 'right', 'left'

    cdef int i
    for i in range(n):
        rects[i].x = table_rects[i][0]
        rects[i].y = table_rects[i][1]
        rects[i].w = table_rects[i][2]
        rects[i].h = table_rects[i][3]

    cdef double fx = from_rect[0], fy = from_rect[1], fw = from_rect[2], fh = from_rect[3]
    cdef double tx = to_rect[0], ty = to_rect[1], tw = to_rect[2], th = to_rect[3]
    cdef double sx, ex, cost, best_cost
    cdef list wp, best_wp
    cdef str best_sf, best_st

    best_cost = 1e18
    best_wp = []
    best_sf = 'right'
    best_st = 'left'

    for sf in ('right', 'left'):
        for st in ('right', 'left'):
            sx = (fx + fw + 12.0) if sf == 'right' else (fx - 12.0)
            ex = (tx - 12.0) if st == 'left' else (tx + tw + 12.0)
            wp = _route_one(sx, field_y_from, ex, field_y_to,
                            from_idx, to_idx, rects, n, gap)
            cost = _path_cost(wp)

            for j in range(1, len(wp) - 1):
                mx, my = wp[j]
                for k in range(n):
                    if k == from_idx or k == to_idx:
                        continue
                    if rects[k].x <= mx <= rects[k].x + rects[k].w and rects[k].y <= my <= rects[k].y + rects[k].h:
                        cost += 100000
                        break

            if cost < best_cost:
                best_cost = cost
                best_wp = wp
                best_sf = sf
                best_st = st

    free(rects)
    return best_wp, best_sf, best_st


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
