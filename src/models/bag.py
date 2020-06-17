import rosbag
from util.utils import meters_to_pixels


class Bag:
    TOPIC_ROAD_RECOGNITION = '/vision/front/left/road_recognition'
    TOPIC_MAP = '/map/pose'
    TOPIC_ODOMETRY = '/odometry/extended'

    def __init__(self, file_path):
        self.file = rosbag.Bag(file_path)
        self.view_region = None
        self.camera_correction_x = 0.4
        self.camera_correction_y = 0.3

    def set_view_region(self, view_region):
        self.view_region = view_region


class ViewRegion:
    def __init__(self, view_region_points, scale):
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

        if self.x1 != 0:
            self.correction_x = 0 - self.x1
        else:
            self.correction_x = 0
        if self.y1 != 0:
            self.correction_y = 0 - self.y1
        else:
            self.correction_y = 0

        self.size_x = meters_to_pixels(self.x2, scale, self.correction_x)
        self.size_y = meters_to_pixels(self.y2, scale, self.correction_y)
