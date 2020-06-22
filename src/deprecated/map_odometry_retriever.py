import rosbag
from matplotlib import pyplot as plt
from skimage.draw import line
from scipy.spatial.transform import Rotation as R
import math

import numpy as np

import sys

sys.path.remove('/opt/ros/lunar/lib/python2.7/dist-packages')  # in order to import cv2 under python3
import cv2

sys.path.append('/opt/ros/lunar/lib/python2.7/dist-packages')  # append back in order to import rospy

MAP_SCALE = 9.93
SIZE_X = 2375
SIZE_Y = 1779
ZERO_X = 57.99496178446453
ZERO_Y = 159.50359386718588

bag = rosbag.Bag('../../localization_data/bags/2019-03-29-18-40-33_0.bag')
map_matrix = np.zeros((SIZE_Y, SIZE_X), dtype=np.uint8)
odom_matrix = np.zeros((SIZE_Y, SIZE_X), dtype=np.uint8)

map_pose_zero_x = None
map_pose_zero_y = None

map_first_point_x = None
map_first_point_y = None
map_second_point_x = None
map_second_point_y = None

odom_first_point_x = None
odom_first_point_y = None
odom_second_point_x = None
odom_second_point_y = None

odom_zero_x = None
odom_zero_y = None

count = 1

for topic, msg, t in bag.read_messages():
    if topic == '/map/pose':
        if map_pose_zero_x is None:
            map_pose_zero_x = msg.pose.position.x
            map_pose_zero_y = msg.pose.position.y
            print("map_pose_zero_x = " + str(map_pose_zero_x))
            print("map_pose_zero_y = " + str(map_pose_zero_y))
            angle = R.from_quat([msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z,
                                 msg.pose.orientation.w]).as_euler('xyz')[2]
            print("map_pose_zero_yaw (rad) = " + str(angle))

            map_first_point_x = int((msg.pose.position.x + ZERO_X) * MAP_SCALE)
            map_first_point_y = SIZE_Y - int((msg.pose.position.y + ZERO_Y) * MAP_SCALE)

            continue
        if count < 2097:
            map_second_point_x = map_first_point_x
            map_second_point_y = map_first_point_y
            map_first_point_x = int((msg.pose.position.x + ZERO_X) * MAP_SCALE)
            map_first_point_y = SIZE_Y - int((msg.pose.position.y + ZERO_Y) * MAP_SCALE)
            rr, cc = line(map_second_point_y, map_second_point_x, map_first_point_y, map_first_point_x)
            print("rr, cc = {}, {}".format(rr, cc))
            map_matrix[rr, cc] = 1
            count += 1
        elif 2097 <= count <= 2197:
            map_second_point_x = map_first_point_x
            map_second_point_y = map_first_point_y
            map_first_point_x = int((msg.pose.position.x + ZERO_X) * MAP_SCALE)
            map_first_point_y = SIZE_Y - int((msg.pose.position.y + ZERO_Y) * MAP_SCALE)
            count += 1
        else:
            map_second_point_x = map_first_point_x
            map_second_point_y = map_first_point_y
            map_first_point_x = int((msg.pose.position.x + ZERO_X) * MAP_SCALE)
            map_first_point_y = SIZE_Y - int((msg.pose.position.y + ZERO_Y) * MAP_SCALE)
            rr, cc = line(map_second_point_y, map_second_point_x, map_first_point_y, map_first_point_x)
            print("rr, cc = {}, {}".format(rr, cc))
            map_matrix[rr, cc] = 1
            count += 1

    # if topic == '/odometry/extended':
    #     if map_pose_zero_x is None:
    #         continue
    #     if odom_zero_x is None:
    #         odom_zero_x = msg.odom.pose.pose.position.x
    #         odom_zero_y = msg.odom.pose.pose.position.y
    #         angle_odom = R.from_quat(
    #             [msg.odom.pose.pose.orientation.x, msg.odom.pose.pose.orientation.y, msg.odom.pose.pose.orientation.z,
    #              msg.odom.pose.pose.orientation.w]).as_euler('xyz')[2]
    #         cos = math.cos(angle - angle_odom)
    #         sin = math.sin(angle - angle_odom)
    #     #     print("cos = " + str(cos))
    #     #     print("sin = " + str(sin))
    #     # print("odom_zero_x = " + str(odom_zero_x))
    #     # print("odom_zero_y = " + str(odom_zero_y))
    #     raw_x = msg.odom.pose.pose.position.x
    #     raw_y = msg.odom.pose.pose.position.y
    #     # print("raw_x = " + str(raw_x))
    #     # print("raw_y = " + str(raw_y))
    #     # x_shifted = float(msg.odom.pose.pose.position.x - odom_zero_x + map_pose_zero_x)
    #     # y_shifted = float(msg.odom.pose.pose.position.y - odom_zero_y + map_pose_zero_y)
    #     # print("x_shifted = " + str(x_shifted))
    #     # print("y_shifted = " + str(y_shifted))
    #     x_rotated = map_pose_zero_x + raw_x * cos - raw_y * sin - odom_zero_x + ZERO_X
    #     y_rotated = map_pose_zero_y + raw_x * sin + raw_y * cos - odom_zero_y + ZERO_Y
    #     # print("x_rotated = " + str(x_rotated))
    #     # print("y_rotated = " + str(y_rotated))
    #     x = int(x_rotated * MAP_SCALE)
    #     y = SIZE_Y - int(y_rotated * MAP_SCALE)
    #     # print("x = " + str(x))
    #     # print("y = " + str(y))
    #     if odom_first_point_x is None:
    #         odom_first_point_x = x
    #         odom_first_point_y = y
    #         continue
    #     elif odom_second_point_x is None:
    #         odom_second_point_x = x
    #         odom_second_point_y = y
    #     else:
    #         odom_first_point_x = odom_second_point_x
    #         odom_first_point_y = odom_second_point_y
    #         odom_second_point_x = x
    #         odom_second_point_y = y
    #     rr1, cc1 = line(odom_first_point_y, odom_first_point_x, odom_second_point_y, odom_second_point_x)
    #     try:
    #         odom_matrix[rr1, cc1] = 1
    #         if count >= 2097:
    #             map_matrix[rr1, cc1] = 1
    #             count += 1
    #     except Exception as e:
    #         # print(e)
    #         fig = plt.figure(figsize=(20, 40))
    #         plt.imshow(odom_matrix)
    #         plt.imsave('odometry_track_error.png', odom_matrix)
    #         break

# plt.imshow(odom_matrix)
# cv2.imwrite('odometry_track_rotated.png', np.invert(odom_matrix))

# cv2.imwrite('map.png', np.invert(map_matrix))
plt.imsave('map.png', map_matrix)
