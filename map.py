import json
import numpy as np
from matplotlib import pyplot as plt

from line import draw_line
from utils import meters_to_pixels, meters_to_pixels_reversed, save_array_as_png


class Map:
    MAP_TYPE_LINE = 'line'
    MAP_TYPE_CURVE = 'curve'

    def __init__(self, file_path):
        with open(file_path, 'r') as map_file:
            map_dict = json.load(map_file)

        self.markup = map_dict['markup']
        self.scale = map_dict['img']['scale']
        self.zero_x = float(map_dict['img']['zeroX'])
        self.zero_y = float(map_dict['img']['zeroY'])
        self.size_x = map_dict['img']['sizeX']
        self.size_y = map_dict['img']['sizeY']

        self.map_as_img = np.zeros((self.size_y, self.size_x), dtype=np.uint8)

        for elem in self.markup:
            if elem['type'] == Map.MAP_TYPE_LINE:
                draw_line(img=self.map_as_img,
                          point1_x=meters_to_pixels(float(elem['u']['x']), self.scale, self.zero_x),
                          point1_y=meters_to_pixels_reversed(float(elem['u']['y']), self.scale, self.zero_y,
                                                             self.size_y),
                          point2_x=meters_to_pixels(float(elem['v']['x']), self.scale, self.zero_x),
                          point2_y=meters_to_pixels_reversed(float(elem['v']['y']), self.scale, self.zero_y,
                                                             self.size_y))

            if elem['type'] == Map.MAP_TYPE_CURVE:
                for pos in range(len(elem['points']) - 1):
                    draw_line(img=self.map_as_img,
                              point1_x=meters_to_pixels(float(elem['points'][pos]['x']), self.scale, self.zero_x),
                              point1_y=meters_to_pixels_reversed(float(elem['points'][pos]['y']), self.scale,
                                                                 self.zero_y,
                                                                 self.size_y),
                              point2_x=meters_to_pixels(float(elem['points'][pos + 1]['x']), self.scale, self.zero_x),
                              point2_y=meters_to_pixels_reversed(float(elem['points'][pos + 1]['y']), self.scale,
                                                                 self.zero_y,
                                                                 self.size_y))

    def save_as_png(self, file_name):
        save_array_as_png(self.map_as_img, file_name)
