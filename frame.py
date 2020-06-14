import numpy as np

from line import draw_line
from utils import meters_to_pixels, meters_to_pixels_reversed, save_array_as_png


class Frame:
    def __init__(self, msg, scale):
        self.view_region = ViewRegion(msg.view_region)

        if self.view_region.x1 != 0:
            correction_x = 0 - self.view_region.x1
        else:
            correction_x = 0
        if self.view_region.y1 != 0:
            correction_y = 0 - self.view_region.y1
        else:
            correction_y = 0

        self.size_x = meters_to_pixels(self.view_region.x2, scale, correction_x)
        self.size_y = meters_to_pixels(self.view_region.y2, scale, correction_y)

        self.frame_as_img = np.zeros((self.size_y, self.size_x), dtype=np.uint8)

        self._draw_frame_features(msg.markup_elements, scale, correction_x, correction_y)
        self._draw_frame_features(msg.edges, scale, correction_x, correction_y)

    def save_as_png(self, file_name):
        save_array_as_png(self.frame_as_img, file_name)

    def _draw_frame_features(self, features_list, scale, correction_x, correction_y):
        for elem in features_list:
            for index in range(len(elem.pts) - 1):
                draw_line(img=self.frame_as_img,
                          point1_x=meters_to_pixels(elem.pts[index].x, scale, correction_x),
                          point1_y=meters_to_pixels_reversed(elem.pts[index].y, scale, correction_y, self.size_y),
                          point2_x=meters_to_pixels(elem.pts[index + 1].x, scale, correction_x),
                          point2_y=meters_to_pixels_reversed(elem.pts[index + 1].y, scale, correction_y, self.size_y))


class ViewRegion:
    def __init__(self, view_region_points):
        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None
        for point in view_region_points:
            if self.x1 is None:
                self.x1 = point.x
            elif self.x1 != point.x:
                self.x2 = point.x
            if self.y1 is None:
                self.y1 = point.y
            elif self.y1 != point.y:
                self.y2 = point.y
