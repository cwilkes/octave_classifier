import sys
import math
from operator import itemgetter


class OctaveMap(object):
    def __init__(self):
        self.my_dict = dict()
        self.my_ary = dict()
        self.categories = dict(FM=1, TT=2, Both=3, Undetermined=4, Aberrant=5)

    def _add_record(self, line):
        parts = line.split(',')
        set_id, data_point_id = int(parts[0]), int(parts[1])
        if not set_id in self.my_dict:
            self.my_dict[set_id] = dict()
        coord_x, coord_y = float(parts[2]), float(parts[3])
        liberal = 0 if parts[4] == 'L' else 1
        if len(parts) == 5:
            self.my_dict[set_id][data_point_id] = (coord_x, coord_y, liberal)
        else:
            self.my_dict[set_id][data_point_id] = (coord_x, coord_y, liberal, self.categories[parts[5]])

    def finalize(self):
        for set_id in self.my_dict.keys():
            self.my_ary[set_id] = self.my_dict[set_id].values()

    def set_ids(self):
        return sorted(self.my_ary.keys())

    def data_points(self, set_id):
        return self.my_ary[set_id]

    def __repr__(self):
        output = list()
        for set_id in self.set_ids():
            vals = ','.join(str(_) for _ in self.data_points(set_id))
            output.append('%d => %s' % (set_id, vals))
        return '\n'.join(output)


def calc_distance(point1, point2):
    return math.sqrt(math.pow(point1[0]-point2[0],2) + math.pow(point1[1]-point2[1],2))


def get_distance_map(data):
    distances = list()
    for x in data:
        distances.append([0 for _ in data])
    for pos1, row1 in enumerate(data):
        for pos2, row2 in enumerate(data):
            distance = calc_distance(row1, row2)
            distances[pos1][pos2] = distance
            distances[pos2][pos1] = distance
    return distances


def get_centroid(data):
    distances = get_distance_map(data)
    distance_sums = list()
    for center_position in range(len(data)):
        count = 0
        for other_position in range(len(data)):
            count += distances[center_position][other_position]
        distance_sums.append((center_position, count))
    distance_sums = sorted(distance_sums, key=itemgetter(1))
    #print distance_sums
    best_row = distance_sums[0][0]
    x, y = data[best_row][0], data[best_row][1]
    return best_row, x, y, math.atan2(y, x), math.sqrt(math.pow(x, 2) + math.pow(y, 2))


def read_train_and_test(train_data, test_data):
    return read_octave_map(train_data), read_octave_map(test_data)


def read_octave_map(reader):
    ret = OctaveMap()
    for line in reader:
        ret._add_record(line.strip())
    ret.finalize()
    return ret


def classify(training_data, test_data):
    ret = list()
    return ret


def only_category_type(data, category_type):
    for row in data:
        if row[3] == category_type:
            yield row

if __name__ == '__main__':
    octave_map = read_octave_map(sys.stdin)
    data = octave_map.data_points(octave_map.set_ids()[-1])
    print 'fm', get_centroid(list(only_category_type(data, 1)))
    print 'tt', get_centroid(list(only_category_type(data, 2)))