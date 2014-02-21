
from operator import itemgetter
import math
import sys
from collections import Counter


TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)


def convex_hull(points):
    if not points:
        return points
    # leftmost one is on hull
    outside_points = [min(points, key=itemgetter(0)), ]
    for p in outside_points:
        q = _next_hull_pt(points, p)
        #_remove_inside_points(outside_points)
        if q != outside_points[0]:
            outside_points.append(q)
    return outside_points


def area_for_polygon(polygon):
    if len(polygon) < 3:
        return 0
    result = 0
    imax = len(polygon) - 1
    for i in range(0, imax):
        result += (polygon[i][0] * polygon[i+1][1]) - (polygon[i+1][0] * polygon[i][1])
    result += (polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1])
    return result / 2.


def get_rectangle(hull, center):
    # y = mx+b and tan(angle) = m
    # distance from (x0,y0) to line y = mx+b
    # abs(y0-mx0-b)/sqrt(1+m^2)
    # also m = y/x = tan(angle)
    # affine transform:
    # http://mathworld.wolfram.com/AffineTransformation.html
    # [ [cosT sinT] [-sinT cosT] ]
    # a = s*cosT, b=-s*sinT
    # x' = ax-by+c
    # y' = bx+ay+d
    # s = sqrt(a^2+b^2)
    # T = atan(-b/a)
    s, c, d = 1, 0, 0
    distances = dict()
    by_area = Counter()
    for angle in range(0, 91, 1):
        a, b = s*math.cos(math.radians(angle)), -s*math.sin(math.radians(angle))
        x_trans = lambda (x, y): a*x-b*y+c
        y_trans = lambda (x, y): b*x+a*y+d
        min_x, max_x, min_y, max_y = sys.maxint, -sys.maxint, sys.maxint, -sys.maxint
        for p in hull:
            x_prime, y_prime = x_trans(p), y_trans(p)
            min_x, max_x = min(min_x, x_prime), max(max_x, x_prime)
            min_y, max_y = min(min_y, y_prime), max(max_y, y_prime)
        distance_x, distance_y = max_x-min_x, max_y-min_y
        area = distance_x * distance_y
        ratio = 1.0 * distance_x / distance_y
        if ratio < 1:
            ratio = 1 / ratio
        distances[angle] = distance_x, distance_y, area, ratio
        by_area[angle] = int(area)
    #for angle, _ in by_area.most_common():
    #    print angle, distances[angle]
    best_angle = by_area.most_common()[-1][0]
    return best_angle, distances[best_angle][0], distances[best_angle][1]


def centroid_for_polygon(polygon):
    if not polygon:
        return None, None
    area = area_for_polygon(polygon)
    if area == 0:
        return polygon[0]
    imax = len(polygon) - 1

    result_x = 0
    result_y = 0
    for i in range(0,imax):
        result_x += (polygon[i][0] + polygon[i+1][0]) * ((polygon[i][0] * polygon[i+1][1]) - (polygon[i+1][0] * polygon[i][1]))
        result_y += (polygon[i][1] + polygon[i+1][1]) * ((polygon[i][0] * polygon[i+1][1]) - (polygon[i+1][0] * polygon[i][1]))
    result_x += (polygon[imax][0] + polygon[0][0]) * ((polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1]))
    result_y += (polygon[imax][1] + polygon[0][1]) * ((polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1]))
    result_x /= (area * 6.0)
    result_y /= (area * 6.0)

    return result_x, result_y


def pdis(a, b, c):
    t = b[0]-a[0], b[1]-a[1]           # Vector ab
    dd = math.sqrt(t[0]**2+t[1]**2)         # Length of ab
    t = t[0]/dd, t[1]/dd               # unit vector of ab
    n = -t[1], t[0]                    # normal unit vector to ab
    ac = c[0]-a[0], c[1]-a[1]          # vector ac
    return math.fabs(ac[0]*n[0]+ac[1]*n[1])


def _point_inside_triangle2(pt, tri):
    # see http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-triangle
    a = 1/(-tri[1][1]*tri[2][0]+tri[0][1]*(-tri[1][0]+tri[2][0]) +
           tri[0][0]*(tri[1][1]-tri[2][1])+tri[1][0]*tri[2][1])
    s = a*(tri[2][0]*tri[0][1]-tri[0][0]*tri[2][1]+(tri[2][1]-tri[0][1])*pt[0]+
           (tri[0][0]-tri[2][0])*pt[1])
    if s < 0:
        return False
    else:
        t = a*(tri[0][0]*tri[1][1]-tri[1][0]*tri[0][1]+(tri[0][1]-tri[1][1])*pt[0]+
              (tri[1][0]-tri[0][0])*pt[1])
    return t > 0 and 1-s-t > 0


def _remove_inside_points(outside_points):
    if len(outside_points) < 3:
        return
    pos = 0
    tri = (outside_points[-1], outside_points[-2], outside_points[-3])
    removals = list()
    while pos < len(outside_points):
        if False and _point_inside_triangle2(outside_points[pos], tri):
            removals.append(outside_points.pop(pos))
        else:
            pos += 1
    if removals:
        print 'removes', removals


def turn(p, q, r):
    """Returns -1, 0, 1 if p,q,r forms a right, straight, or left turn."""
    return cmp((q[0] - p[0])*(r[1] - p[1]) - (r[0] - p[0])*(q[1] - p[1]), 0)


def _dist(p, q):
    """Returns the squared Euclidean distance between p and q."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    return dx * dx + dy * dy


def _next_hull_pt(points, p):
    """Returns the next point on the convex hull in CCW from p."""
    q = p
    for r in points:
        t = turn(p, q, r)
        if t == TURN_RIGHT or t == TURN_NONE and _dist(p, r) > _dist(p, q):
            q = r
    return q
