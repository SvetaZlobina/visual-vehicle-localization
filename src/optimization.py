from models.map import Map
from models.bag import Bag, ViewRegion
from models.frame import Frame
from models.pose import Pose
from util.utils import meters_to_pixels
import numpy as np
from scipy.optimize import minimize
import math

a_priori_map = Map('../localization_data/map/map_info.json')

bag = Bag('../localization_data/bags/2019-03-29-18-40-33_0.bag')

prev_odometry_pose = None
curr_odometry_pose = None
curr_frame = None
curr_map_pose = None
curr_pose = None
zero_yaw = None
i_frame = 1


def opt_fun(independent_vars, *args):
    frame_sum = args[0]
    view_region = args[1]
    x = independent_vars[0]
    y = independent_vars[1]
    yaw = independent_vars[2]

    map_sum = np.sum(a_priori_map.crop_frame(x, y, yaw, view_region), dtype=np.uint8)
    diff = abs(frame_sum.astype(int) - map_sum.astype(int))
    print("frame_sum = {}, map_sum = {}, diff = {}".format(frame_sum.astype(int), map_sum.astype(int), diff))
    return diff


for topic, msg, t in bag.file.read_messages():
    if topic == Bag.TOPIC_MAP:
        curr_map_pose = Pose(msg.pose.position, msg.pose.orientation, a_priori_map.scale, a_priori_map.zero_x,
                             a_priori_map.zero_y, a_priori_map.size_x,
                             a_priori_map.size_y)
        if curr_pose is None:  # initial pose at the start of the ride
            zero_yaw = curr_map_pose.orientation.yaw
            curr_pose = curr_map_pose

    if topic == Bag.TOPIC_ODOMETRY:
        if prev_odometry_pose is None:
            prev_odometry_pose = Pose(msg.odom.pose.pose.position, msg.odom.pose.pose.orientation, a_priori_map.scale,
                                      a_priori_map.zero_x, a_priori_map.zero_y, a_priori_map.size_x,
                                      a_priori_map.size_y)
        else:
            curr_odometry_pose = Pose(msg.odom.pose.pose.position, msg.odom.pose.pose.orientation, a_priori_map.scale,
                                      a_priori_map.zero_x, a_priori_map.zero_y, a_priori_map.size_x,
                                      a_priori_map.size_y)

    if topic == Bag.TOPIC_ROAD_RECOGNITION:  # make comparison for each frame in road recognition
        if i_frame == 1:
            bag.set_view_region(ViewRegion(msg.view_region, a_priori_map.scale))
        curr_frame = Frame(msg, a_priori_map.scale, bag.view_region)
        curr_frame_sum = np.sum(curr_frame.frame_as_img, dtype=np.uint8)
        i_frame += 1
        if curr_pose is not None and prev_odometry_pose is not None and curr_odometry_pose is not None:
            delta_x, delta_y, delta_yaw = curr_odometry_pose.get_delta(prev_odometry_pose)
            delta_x = meters_to_pixels(delta_x, a_priori_map.scale, 0)
            delta_y = meters_to_pixels(delta_y, a_priori_map.scale, 0)
            print("delta_x = {}, delta_y = {}, delta_yaw = {}".format(delta_x, delta_y, delta_yaw))
            prev_odometry_pose = curr_odometry_pose

            print("curr_pose: {}, {}, {}".format(curr_pose.position.x, curr_pose.position.y,
                                                 curr_pose.orientation.yaw - zero_yaw))
            print("curr_map_pose: {}, {}, {}".format(curr_map_pose.position.x, curr_map_pose.position.y,
                                                     curr_map_pose.orientation.yaw - zero_yaw))

            x_start = int(curr_pose.position.x + delta_x)
            y_start = int(curr_pose.position.y + delta_y)
            yaw_start = curr_pose.orientation.yaw - zero_yaw + delta_yaw

            print("x_start = {}".format(x_start))
            print("y_start = {}".format(y_start))
            print("yaw_start = {}".format(yaw_start))

            # map_frame = a_priori_map.crop_frame(x_start, y_start, yaw_start, bag.view_region)

            res = minimize(opt_fun, np.array([x_start, y_start, yaw_start]), args=(curr_frame_sum, bag.view_region),
                           bounds=[(x_start - 10, x_start + 10), (y_start - 10, y_start + 10),
                                   (yaw_start - math.radians(10), yaw_start + math.radians(10))],
                           options={'eps': [1, 1, 0.017]})

            print(str(res))

            # print(str(curr_frame.frame_as_img.shape))
            # print(str(curr_frame_sum))
            # print(str(map_frame.shape))
            # print(str(np.sum(map_frame, dtype=np.uint8)))

            if i_frame == 30:
                break
