from scipy.spatial.transform import Rotation as R
from util.utils import meters_to_pixels, meters_to_pixels_reversed


class Pose:
    def __init__(self, msg_position, msg_orientation, scale, zero_x, zero_y, size_x, size_y):
        self.position = Position(msg_position.x, msg_position.y, msg_position.z, scale, zero_x, zero_y, size_x, size_y)
        self.orientation = Orientation(msg_orientation.x, msg_orientation.y, msg_orientation.z, msg_orientation.w)

    def get_delta(self, prev_pose):
        return (self.position.x - prev_pose.position.x, self.position.y - prev_pose.position.y,
                self.orientation.yaw - prev_pose.orientation.yaw)


class Position:
    def __init__(self, x, y, z, scale, zero_x, zero_y, size_x, size_y):
        self.x = meters_to_pixels(x, scale, zero_x)  # in meters
        self.y = meters_to_pixels_reversed(y, scale, zero_y, size_y)
        self.z = z


class Orientation:
    def __init__(self, x, y, z, w):
        self.roll, self.pitch, self.yaw = R.from_quat([x, y, z, w]).as_euler('xyz')  # in radians
