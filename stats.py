from quick_hull import convex_hull, centroid_for_polygon, get_rectangle
import sys
from OctaveClassifier import read_octave_map
import math
import fitEllipse as fe

from collections import namedtuple
Ellipse = namedtuple('Ellipse', 'center width height angle')


def get_ellipse(points):
    x, y = fe.make_x_y(points)
    try:
        a = fe.fitEllipse(x,y)
    except Exception as ex:
        print >>sys.stderr, 'problem with points', points, ex
        return None
    fe_center = fe.ellipse_center(a)
    angle = fe.ellipse_angle_of_rotation(a)
    axis_1, axis_2 = fe.ellipse_axis_length(a)
    try:
        center = int(fe_center[0]), int(fe_center[1])
        width, height = int(axis_1), int(axis_2)
        my_angle = int(math.degrees(angle))
        return Ellipse(center, width, height, my_angle)
    except Exception as ex:
        print >>sys.stderr, 'Error with parsing', fe_center, axis_1, axis_2, angle, ex
        return None

#  print '%d %d %d %d %d %d %d %d %d %d' % (
#            tt_ellipse[0][0], tt_ellipse[0][1], tt_ellipse[1], tt_ellipse[2], tt_ellipse[3],
#            fm_ellipse[0][0], fm_ellipse[0][1], fm_ellipse[1], fm_ellipse[2], fm_ellipse[3])


def within_ellipse(ellipse, point):
    if ellipse[1] == 0 or ellipse[2] == 0:
        return False
    t = math.radians(ellipse[3])
    dx = (point[0]-ellipse[0][0])
    dy = (point[1]-ellipse[0][1])
    x_prime = +dx*math.cos(t) + dy*math.sin(t)
    y_prime = -dx*math.sin(t) + dy*math.cos(t)
    ecc = math.pow(x_prime/ellipse[1], 2) + math.pow(y_prime/ellipse[2], 2)
    return ecc < 1.23


def match_ellipses(ellipses, points):
    for ellipse_pos, (tt_ellipse, fm_ellipse) in enumerate(ellipses):
        tt_count, fm_count = 0, 0
        for point in points:
            tt_count += 1 if within_ellipse(tt_ellipse, point) else 0
            fm_count += 1 if within_ellipse(fm_ellipse, point) else 0
        print '  ellipse #%d : %d %d / %d' % (ellipse_pos, tt_count, fm_count, len(points))


def read_ellipses(reader):
    my_map = read_octave_map(reader)
    ellipses = list()
    for set_id in my_map.set_ids():
        vals, cat_type = my_map.data_points(set_id)
        tt_points, fm_points = vals[0], vals[1]
        tt_hull, fm_hull = convex_hull(tt_points), convex_hull(fm_points)
        tt_ellipse, fm_ellipse = get_ellipse(tt_hull), get_ellipse(fm_hull)
        if tt_ellipse is None or fm_ellipse is None:
            continue
        ellipses.append((tt_ellipse, fm_ellipse))
    return ellipses

if __name__ == '__main__':
    ellipses = read_ellipses(open(sys.argv[1]))
    test_map = read_octave_map(open(sys.argv[2]))
    for set_id in test_map.set_ids():
        print 'set_id', set_id
        vals, rule_type = test_map.data_points(set_id)
        match_ellipses(ellipses, vals[0])
