from quick_hull import convex_hull, centroid_for_polygon, get_rectangle
import sys
import matplotlib.pyplot as plt
from OctaveClassifier import read_octave_map
import math
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Ellipse
import fitEllipse as fe


def get_two_types(reader):
    ret = list(), list()
    for p in (_.strip().split(',') for _ in reader):
        coord_x, coord_y = float(p[2]), float(p[3])
        if p[-1] == 'TT':
            ret[0].append((coord_x, coord_y))
        elif p[-1] == 'FM':
            ret[1].append((coord_x, coord_y))
    return ret


def do_plot(points, color_vertex, color_centroid, centroid_only=False):
    while points:
        vertexes = convex_hull(points)
        for pos, (x, y) in enumerate(vertexes):
            points.remove((x, y))
            if centroid_only:
                continue
            plt.plot(x, y, color_vertex +'o')
            if pos == 0:
                plt.plot([vertexes[-1][0], x], [vertexes[-1][1], y], color_vertex + '-')
            else:
                plt.plot([vertexes[pos-1][0], x], [vertexes[pos-1][1], y], color_vertex + '-')
        x, y = centroid_for_polygon(vertexes)
        plt.plot(x, y, color_centroid + 'o')
    if not centroid_only:
        plt.plot([_[0] for _ in points], [_[1] for _ in points], 'ro')


def do_line_to_centroids(points_a, points_b):
    a_x, a_y = centroid_for_polygon(convex_hull(points_a))
    b_x, b_y = centroid_for_polygon(convex_hull(points_b))
    if a_x is None or b_x is None:
        return
    plt.plot([a_x, b_x], [a_y, b_y], 'b-')
    #plt.arrow(a_x, a_y, a_x-b_x, a_y-b_y)


def plot_vertexes(vertexes, vertex_color='y'):
    for pos, (x, y) in enumerate(vertexes):
        plt.plot(x, y, vertex_color + 'o')
        if pos == 0:
            plt.plot([vertexes[-1][0], x], [vertexes[-1][1], y], vertex_color + '-')
        else:
            plt.plot([vertexes[pos-1][0], x], [vertexes[pos-1][1], y], vertex_color + '-')


def plot_ellipse(points):
    x,y = fe.make_x_y(points)
    a = fe.fitEllipse(x,y)
    fe_center = fe.ellipse_center(a)
    plt.plot(fe_center[0], fe_center[1], 'ro')
    angle = fe.ellipse_angle_of_rotation(a)
    axis_1, axis_2 = fe.ellipse_axis_length(a)
    rect = Ellipse(fe_center, 2*axis_1, 2*axis_2, math.degrees(angle))
    plt.gca().add_patch(rect)


if __name__ == '__main__':
    my_map = read_octave_map(sys.stdin)
    for set_id in my_map.set_ids():
        vals, cat_type = my_map.data_points(set_id)
        tt_points, fm_points = vals[0], vals[1]
        tt_hull, fm_hull = convex_hull(tt_points), convex_hull(fm_points)
        plot_vertexes(tt_hull, 'b')
        plot_vertexes(fm_hull, 'g')
        tt_center, fm_center = centroid_for_polygon(tt_hull), centroid_for_polygon(fm_hull)
        plt.plot(tt_center[0], tt_center[1], 'yo')
        plt.plot(fm_center[0], fm_center[1], 'yo')
        tt_rectangle = get_rectangle(tt_hull, tt_center)
        fm_rectangle = get_rectangle(fm_hull, fm_center)
        plot_ellipse(tt_hull)
        plot_ellipse(fm_hull)
        plt.plot([_[0] for _ in tt_points], [_[1] for _ in tt_points], 'bo')
        plt.plot([_[0] for _ in fm_points], [_[1] for _ in fm_points], 'go')
    plt.show()
