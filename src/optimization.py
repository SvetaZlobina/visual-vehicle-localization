from models.map import Map
from models.bag import Bag, ViewRegion
from models.frame import Frame
from models.pose import Pose
from util.utils import meters_to_pixels, save_array_as_png
from util.line import draw_line
import numpy as np
from scipy.optimize import minimize, least_squares
import math

a_priori_map = Map('../localization_data/map/map_info.json')

bag = Bag('../localization_data/bags/2019-03-29-18-40-33_0.bag')
camera_correction_x = int(bag.camera_correction_x * a_priori_map.scale)
camera_correction_y = int(bag.camera_correction_y * a_priori_map.scale)

prev_odometry_pose = None
curr_odometry_pose = None
curr_frame = None
curr_map_pose = None
curr_pose = None
zero_yaw = None
i_frame = 1

optimized_matrix = np.zeros((a_priori_map.size_y, a_priori_map.size_x), dtype=np.uint8)


def opt_fun(independent_vars, *args):
    frame_sum = args[0]
    view_region = args[1]

    x = independent_vars[0]
    y = independent_vars[1]
    yaw = independent_vars[2]

    map_sum = np.count_nonzero(a_priori_map.crop_frame(x, y, yaw, view_region))
    diff = abs(frame_sum - map_sum)
    print("frame_sum = {}, map_sum = {}, diff = {}".format(frame_sum, map_sum, diff))
    return diff


try:
    for topic, msg, t in bag.file.read_messages():
        if topic == Bag.TOPIC_MAP:
            curr_map_pose = Pose(msg.pose.position, msg.pose.orientation, a_priori_map.scale, a_priori_map.zero_x,
                                 a_priori_map.zero_y, a_priori_map.size_x,
                                 a_priori_map.size_y)
            if curr_pose is None:  # initial pose at the start of the ride
                zero_yaw = curr_map_pose.orientation.yaw
                curr_pose = curr_map_pose
                curr_pose.orientation.yaw -= zero_yaw

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
            curr_frame_sum = np.count_nonzero(curr_frame.frame_as_img)

            i_frame += 1
            if curr_pose is not None and prev_odometry_pose is not None and curr_odometry_pose is not None:
                delta_x, delta_y, delta_yaw = curr_odometry_pose.get_delta(prev_odometry_pose)
                delta_x = meters_to_pixels(delta_x, a_priori_map.scale, 0)
                delta_y = meters_to_pixels(delta_y, a_priori_map.scale, 0)
                print("delta_x = {}, delta_y = {}, delta_yaw = {}".format(delta_x, delta_y, delta_yaw))
                prev_odometry_pose = curr_odometry_pose

                print("curr_pose: {}, {}, {}".format(curr_pose.position.x, curr_pose.position.y,
                                                     curr_pose.orientation.yaw))
                print("curr_map_pose: {}, {}, {}".format(curr_map_pose.position.x, curr_map_pose.position.y,
                                                         curr_map_pose.orientation.yaw - zero_yaw))

                x_start = int(curr_pose.position.x - camera_correction_x + delta_x)
                y_start = int(curr_pose.position.y - camera_correction_y + delta_y)
                yaw_start = curr_pose.orientation.yaw + delta_yaw

                print("x_start = {}".format(x_start + camera_correction_x))
                print("y_start = {}".format(y_start + camera_correction_y))
                print("yaw_start = {}".format(yaw_start))

                # map_frame = a_priori_map.crop_frame(x_start,y_start, yaw_start, bag.view_region)

                # res = minimize(opt_fun, np.array([x_start, y_start, yaw_start]), args=(curr_frame_sum, bag.view_region),
                #                bounds=[(x_start - 10, x_start + 10), (y_start - 10, y_start + 10),
                #                        (yaw_start - math.radians(10), yaw_start + math.radians(10))],
                #                options={'eps': [1, 1, 0.017]})

                res = least_squares(opt_fun, np.array([x_start, y_start, yaw_start]),
                                    args=(curr_frame_sum, bag.view_region),
                                    bounds=[(x_start - 10, y_start - 10, yaw_start - math.radians(10)),
                                            (x_start + 10, y_start + 10, yaw_start + math.radians(10))],
                                    diff_step=[1, 1, 0.017])

                print(str(res))

                optimal_pose_x = int(res.x[0]) + camera_correction_x
                optimal_pose_y = int(res.x[1]) + camera_correction_y
                optimal_pose_yaw = res.x[2]

                print("x_optimal = {}".format(optimal_pose_x))
                print("y_optimal = {}".format(optimal_pose_y))
                print("yaw_optimal = {}".format(optimal_pose_yaw))

                draw_line(optimized_matrix, curr_pose.position.x, curr_pose.position.y, optimal_pose_x, optimal_pose_y)

                curr_pose.position.x = optimal_pose_x
                curr_pose.position.y = optimal_pose_y
                curr_pose.orientation.yaw = optimal_pose_yaw

                if i_frame == 150:
                    save_array_as_png(optimized_matrix, 'optimized_track')
                    break
except Exception as e:
    print(e)
    save_array_as_png(optimized_matrix, 'optimized_track_error')
