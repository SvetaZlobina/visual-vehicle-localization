from models.map import Map
from models.bag import Bag, ViewRegion
from models.frame import Frame
from models.pose import Pose
from util.utils import meters_to_pixels, save_array_as_png
from util.line import draw_line
import numpy as np
from scipy.optimize import minimize, least_squares
import math

import sys

sys.path.remove('/opt/ros/lunar/lib/python2.7/dist-packages')  # in order to import cv2 under python3
import cv2

sys.path.append('/opt/ros/lunar/lib/python2.7/dist-packages')  # append back in order to import rospy

a_priori_map = Map('../localization_data/map/map_info.json')
a_priori_map.save_as_png('map')

bag = Bag('../localization_data/bags/2019-03-29-18-40-33_0.bag')
camera_correction_x = int(bag.camera_correction_x * a_priori_map.scale)
camera_correction_y = int(bag.camera_correction_y * a_priori_map.scale)

prev_odometry_pose = None
curr_odometry_pose = None
curr_frame = None
prev_map_pose = None
curr_map_pose = None
curr_pose = None
zero_yaw = None
i_frame = 1

optimized_matrix = np.zeros((a_priori_map.size_y, a_priori_map.size_x), dtype=np.uint8)

COORDINATES_BOUND = 10
ANGLE_BOUND = 10


class OptimizationResult:
    def __init__(self, x, y, yaw):
        self.x = x
        self.y = y
        self.yaw = yaw


def opt_fun(independent_vars, *args):
    frame = args[0]
    view_region = args[1]

    x = independent_vars[0]
    y = independent_vars[1]
    yaw = independent_vars[2]

    map_frame = a_priori_map.crop_frame(x, y, yaw, view_region)
    equal = np.sum(frame != map_frame)
    print("equal = {}".format(equal))
    return equal


def sliding_window(start_x, start_y, start_yaw, frame, view_region):
    results = {}
    for x in range(start_x - COORDINATES_BOUND, start_x + COORDINATES_BOUND, 1):
        for y in range(start_y - COORDINATES_BOUND, start_y + COORDINATES_BOUND, 1):
            for yaw in range(start_yaw - ANGLE_BOUND, start_yaw + ANGLE_BOUND, 1):
                results[OptimizationResult(x, y, yaw)] = opt_fun([x, y, math.radians(yaw)], [frame, view_region])
                + abs(x - start_x) + abs(y - start_y) + abs(yaw - start_yaw)

    return min(results)


try:
    for topic, msg, t in bag.file.read_messages():
        if topic == Bag.TOPIC_MAP:
            if curr_map_pose is None:  # initial pose at the start of the ride
                curr_map_pose = Pose(msg.pose.position, msg.pose.orientation, a_priori_map.scale, a_priori_map.zero_x,
                                     a_priori_map.zero_y, a_priori_map.size_x,
                                     a_priori_map.size_y)
                zero_yaw = curr_map_pose.orientation.yaw
                curr_pose = curr_map_pose
                curr_pose.orientation.yaw -= zero_yaw
                continue

            prev_map_pose = curr_map_pose
            curr_map_pose = Pose(msg.pose.position, msg.pose.orientation, a_priori_map.scale, a_priori_map.zero_x,
                                 a_priori_map.zero_y, a_priori_map.size_x,
                                 a_priori_map.size_y)

        if topic == Bag.TOPIC_ODOMETRY:
            if prev_odometry_pose is None:
                prev_odometry_pose = Pose(msg.odom.pose.pose.position, msg.odom.pose.pose.orientation,
                                          a_priori_map.scale,
                                          a_priori_map.zero_x, a_priori_map.zero_y, a_priori_map.size_x,
                                          a_priori_map.size_y)
            else:
                curr_odometry_pose = Pose(msg.odom.pose.pose.position, msg.odom.pose.pose.orientation,
                                          a_priori_map.scale,
                                          a_priori_map.zero_x, a_priori_map.zero_y, a_priori_map.size_x,
                                          a_priori_map.size_y)

        if topic == Bag.TOPIC_ROAD_RECOGNITION:  # make comparison for each frame in road recognition

            if i_frame == 1:
                bag.set_view_region(ViewRegion(msg.view_region, a_priori_map.scale))

            curr_frame = Frame(msg, a_priori_map.scale, bag.view_region)
            curr_frame.save_as_png('curr_frame')

            i_frame += 1
            if curr_pose is not None and prev_odometry_pose is not None and curr_odometry_pose is not None:
                cv2.imwrite('frame{}.png'.format(i_frame - 1), curr_frame.frame_as_img)

                delta_x, delta_y, delta_yaw = curr_odometry_pose.get_delta(prev_odometry_pose)
                delta_x = meters_to_pixels(delta_x, a_priori_map.scale, 0)
                delta_y = meters_to_pixels(delta_y, a_priori_map.scale, 0)
                prev_odometry_pose = curr_odometry_pose

                x_start = int(curr_pose.position.x - camera_correction_x + delta_x)
                y_start = int(curr_pose.position.y - camera_correction_y + delta_y)
                yaw_start = curr_pose.orientation.yaw + delta_yaw

                map_frame = a_priori_map.crop_frame(curr_map_pose.position.x - camera_correction_x,
                                                    curr_map_pose.position.y - camera_correction_y,
                                                    curr_map_pose.orientation.yaw - zero_yaw,
                                                    bag.view_region)

                res = sliding_window(x_start, y_start, yaw_start, curr_frame, bag.view_region)

                optimal_pose_x = int(res.x[0]) + camera_correction_x
                optimal_pose_y = int(res.x[1]) + camera_correction_y
                optimal_pose_yaw = res.x[2]

                draw_line(optimized_matrix, curr_pose.position.x, curr_pose.position.y, optimal_pose_x, optimal_pose_y)
                draw_line(optimized_matrix, prev_map_pose.position.x, prev_map_pose.position.y,
                          curr_map_pose.position.x, curr_map_pose.position.y)

                curr_pose.position.x = optimal_pose_x
                curr_pose.position.y = optimal_pose_y
                curr_pose.orientation.yaw = optimal_pose_yaw

                # break
except Exception as e:
    print(e)
    save_array_as_png(optimized_matrix, 'optimized_track_error')
