import numpy as np

from util.line import draw_line
from util.utils import meters_to_pixels, meters_to_pixels_reversed, save_array_as_png

import sys

sys.path.remove('/opt/ros/lunar/lib/python2.7/dist-packages')  # in order to import cv2 under python3
import cv2

sys.path.append('/opt/ros/lunar/lib/python2.7/dist-packages')  # append back in order to import rospy


class Frame:
    def __init__(self, msg, scale, view_region):
        self.size_x = view_region.size_x
        self.size_y = view_region.size_y

        self.frame_as_img = np.zeros((self.size_y, self.size_x), dtype=np.uint8)

        self._draw_frame_features(msg.markup_elements, scale, view_region.correction_x, view_region.correction_y)
        self._draw_frame_features(msg.edges, scale, view_region.correction_x, view_region.correction_y)

    def save_as_png(self, file_name):
        cv2.imwrite('{}.png'.format(file_name), np.invert(self.frame_as_img))

    def _draw_frame_features(self, features_list, scale, correction_x, correction_y):
        for elem in features_list:
            for index in range(len(elem.pts) - 1):
                draw_line(img=self.frame_as_img,
                          point1_x=meters_to_pixels(elem.pts[index].x, scale, correction_x, self.size_x),
                          point1_y=meters_to_pixels_reversed(elem.pts[index].y, scale, correction_y, self.size_y),
                          point2_x=meters_to_pixels(elem.pts[index + 1].x, scale, correction_x, self.size_x),
                          point2_y=meters_to_pixels_reversed(elem.pts[index + 1].y, scale, correction_y, self.size_y))
