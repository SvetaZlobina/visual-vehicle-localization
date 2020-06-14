import rosbag


class Bag:
    TOPIC_ROAD_RECOGNITION = '/vision/front/left/road_recognition'
    TOPIC_MAP = '/map/pose'
    TOPIC_ODOMETRY = '/odometry/extended'

    def __init__(self, file_path):
        self.file = rosbag.Bag(file_path)
