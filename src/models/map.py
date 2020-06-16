import json
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.path import Path
import math

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

        self.map_as_img = np.zeros((self.size_y, self.size_x, 3), dtype=np.uint8)

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
        # (middle_x, middle_y) - rotation origin (center) - middle bottom point of the frame
        middle_x = int(x)
        # TODO: add yaw condition (+/- size_y)
        middle_y = int(y + view_region.size_y)

        bottom_left = rotate_on_angle(x - int(view_region.size_x / 2), y, yaw, middle_x, middle_y)
        top_left = rotate_on_angle(x - int(view_region.size_x / 2), y + view_region.size_y, yaw, middle_x, middle_y)
        top_right = rotate_on_angle(x + int(view_region.size_x / 2), y + view_region.size_y, yaw, middle_x, middle_y)
        bottom_right = rotate_on_angle(x + int(view_region.size_x / 2), y, yaw, middle_x, middle_y)

        max_margin = max(view_region.size_y, view_region.size_x)
        y_min = int(y - max_margin)
        y_max = int(y + view_region.size_y + max_margin)
        x_min = int(x - view_region.size_x / 2 - max_margin)
        x_max = int(x + view_region.size_x / 2 + max_margin)

        cropped = self.map_as_img[y_min:y_max, x_min:x_max]
        # plt.imsave('cropped.png', cropped)

        yc = np.array([bottom_left[0] - y_min, top_left[0] - y_min, top_right[0] - y_min, bottom_right[0] - y_min])
        xc = np.array([bottom_left[1] - x_min, top_left[1] - x_min, top_right[1] - x_min, bottom_right[1] - x_min])
        xycrop = np.vstack((xc, yc)).T

        nr, nc, ncolor = cropped.shape
        ygrid, xgrid = np.mgrid[:nr, :nc]
        xypix = np.vstack((xgrid.ravel(), ygrid.ravel())).T

        pth = Path(xycrop, closed=False)
        mask = pth.contains_points(xypix)
        mask = mask.reshape((nr, nc))
        masked = np.ma.masked_array(cropped[:, :, 0], ~mask)
        # xmin, xmax = int(xc.min()), int(np.ceil(xc.max()))
        # ymin, ymax = int(yc.min()), int(np.ceil(yc.max()))
        # trimmed = masked[ymin:ymax, xmin:xmax]

        # rr, cc = line(bottom_left[0], bottom_left[1], top_left[0], top_left[1])
        # cropped[rr, cc] = (255, 255, 0)
        # rr, cc = line(top_left[0], top_left[1], top_right[0], top_right[1])
        # cropped[rr, cc] = (255, 255, 0)
        # rr, cc = line(top_right[0], top_right[1], bottom_right[0], bottom_right[1])
        # cropped[rr, cc] = (255, 255, 0)
        # rr, cc = line(bottom_right[0], bottom_right[1], bottom_left[0], bottom_left[1])
        # cropped[rr, cc] = (255, 255, 0)
        # plt.imsave('cropped_map.png', cropped)

        # plt.imsave('masked.png', masked)
        # plt.imsave('trimmed.png', trimmed)
        return masked

    def save_as_png(self, file_name):
        save_array_as_png(self.map_as_img, file_name)
