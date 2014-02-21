import sys
import math
from operator import itemgetter
import random

from collections import namedtuple
Ellipse = namedtuple('Ellipse', 'center width height angle')


categories = dict(FM=1, TT=2, Both=3, Undetermined=4, Aberrant=5)




class OctaveMap(object):
    def __init__(self):
        self.my_dict = dict()
        self.my_cat_types = dict()

    def add_record(self, line):
        parts = line.split(',')
        set_id = int(parts[0])
        if not set_id in self.my_dict:
            self.my_dict[set_id] = list(), list(), list(), list(), list()
            self.my_cat_types[set_id] = parts[4]
        coord_x, coord_y = float(parts[2]), float(parts[3])
        slot = 0 if len(parts) == 5 else categories[parts[5]]-1
        self.my_dict[set_id][slot].append((coord_x, coord_y))

    def set_ids(self):
        return sorted(self.my_dict.keys())

    def data_points(self, set_id):
        return self.my_dict[set_id], self.my_cat_types[set_id]


def calc_distance(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2, 2))


def get_distance_map(data):
    distances = list()
    for foo in data:
        distances.append([0 for _ in data])
    for pos1, (x1, y1) in enumerate(data):
        for pos2, (x2, y2) in enumerate(data):
            distance = calc_distance(x1, y1, x2, y2)
            distances[pos1][pos2] = distance
            distances[pos2][pos1] = distance
    return distances


def get_sum_distances(data, x, y):
    return sum(calc_distance(x1, y1, x, y) for x1, y1 in data)


def get_knn_center(data, center_x, center_y, dist=50, delta_angle=5):
    if dist == 0:
        return center_x, center_y
    orig_distance = get_sum_distances(data, center_x, center_y)
    best_distance = orig_distance
    best_x, best_y = center_x, center_y
    for angle in range(random.randint(0, 10), 360, delta_angle):
        new_x, new_y = center_x + dist * math.cos(math.radians(angle)), center_y + dist * math.sin(math.radians(angle))
        distance = get_sum_distances(data, new_x, new_y)
        if distance < best_distance:
            best_x, best_y, best_distance = new_x, new_y, distance
    return get_knn_center(data, best_x, best_y, dist-1, delta_angle)


def get_centroid(data):
    if not data:
        return None, 0, None, None, None, None
    distances = get_distance_map(data)
    distance_sums = list()
    for pos1, (x1, y1) in enumerate(data):
        count = 0
        for pos2, (x2, y2) in enumerate(data):
            count += distances[pos1][pos2]
        distance_sums.append((pos1, count))
    distance_sums = sorted(distance_sums, key=itemgetter(1))
    #print distance_sums
    best_row = distance_sums[0][0]
    x, y = data[best_row][0], data[best_row][1]
    return best_row, len(distance_sums), x, y, math.atan2(y, x), math.sqrt(math.pow(x, 2) + math.pow(y, 2))


def read_train_and_test(train_data, test_data):
    return read_octave_map(train_data), read_octave_map(test_data)


def read_octave_map(reader):
    ret = OctaveMap()
    for line in reader:
        ret.add_record(line.strip())
    return ret


def classify(training_data, test_data):
    ret = list()
    return ret


if __name__ == '__main__':
    octave_map = read_octave_map(sys.stdin)
    set_id = octave_map.set_ids()[-1]
    data, cat_type = octave_map.data_points(set_id)
    print 'set_id', set_id, 'cat_type', cat_type
    for cat_type, cat_number in categories.items():
        my_data = data[cat_number-1]
        row_id, number_points, x, y, angle, distance = get_centroid(my_data)
        center_x, center_y = get_knn_center(my_data, x, y)
        print '%s (%d) (%.1f, %.1f) => (%.1f, %.1f) %d %d' % (cat_type, number_points, x, y, center_x, center_y, math.degrees(angle), distance)
