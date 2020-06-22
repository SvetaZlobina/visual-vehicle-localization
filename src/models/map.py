import json
import numpy as np
import math

import sys

sys.path.remove('/opt/ros/lunar/lib/python2.7/dist-packages')  # in order to import cv2 under python3
import cv2

sys.path.append('/opt/ros/lunar/lib/python2.7/dist-packages')  # append back in order to import rospy

from util.line import draw_line
from util.utils import meters_to_pixels, meters_to_pixels_reversed, save_array_as_png, rotate_on_angle


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
        self.count = 1

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

    def crop_frame(self, x, y, yaw, view_region):

        print("crop_frame called: x = {}, y = {}, yaw = {}".format(x, y, yaw))

        rect = cv2.minAreaRect(
            np.array([[int(x - view_region.size_x / 2), int(y)],
                      [int(x - view_region.size_x / 2), int(y + view_region.size_y)],
                      [int(x + view_region.size_x / 2), int(y + view_region.size_y)],
                      [int(x + view_region.size_x / 2), int(y)]]))

        mask = np.zeros((self.size_y, self.size_x), dtype=np.uint8)

        rotation_matrix = cv2.getRotationMatrix2D((self.size_y / 2, self.size_x / 2), math.degrees(-yaw), 1)

        box = cv2.boxPoints(rect)
        pts = np.int0(cv2.transform(np.array([box]), rotation_matrix))[0]

        cv2.fillPoly(mask, [pts], 255)
        cv2.imwrite('mask{}.png'.format(self.count), np.invert(mask))

        masked_image = cv2.bitwise_and(self.map_as_img, mask)
        # cv2.imwrite('map_frame{}.png'.format(self.count), masked_image)

        back_rotation_matrix = cv2.getRotationMatrix2D((self.size_y / 2, self.size_x / 2), math.degrees(yaw), 1)
        final_rect = cv2.minAreaRect(np.int0(pts))
        final_box = cv2.boxPoints(final_rect)
        pts_final = np.int0(cv2.transform(np.int0([final_box]), back_rotation_matrix))[0]

        x, y, w, h = cv2.boundingRect(pts_final)
        w = view_region.size_x
        h = view_region.size_y
        cropped = masked_image[y: y + h, x: x + w]
        cv2.imwrite('cropped{}.png'.format(self.count), np.invert(cropped))

        self.count += 1

        return cropped

    def save_as_png(self, file_name):
        cv2.imwrite('{}.png'.format(file_name), np.invert(self.map_as_img))
