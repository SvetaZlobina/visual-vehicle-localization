import rosbag
import numpy as np
from matplotlib import pyplot as plt
from skimage.draw import line
from scipy.spatial.transform import Rotation as R
import math

MAP_SCALE = 9.93
SIZE_X = 2375
SIZE_Y = 1779
ZERO_X = int(57.99496178446453 * MAP_SCALE)
ZERO_Y = int(159.50359386718588 * MAP_SCALE)

bag = rosbag.Bag('localization_data/bags/2019-03-29-18-40-33_0.bag')
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

for topic, msg, t in bag.read_messages():
    if topic == '/map/pose':
        if map_pose_zero_x is None:
            map_pose_zero_x = msg.pose.position.x
            map_pose_zero_y = msg.pose.position.y
            print(map_pose_zero_x)
            print(map_pose_zero_y)
            angle = R.from_quat([msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z,
                                 msg.pose.orientation.w]).as_euler('xyz')[2]
            cos = math.cos(angle)
            sin = math.sin(angle)
            print(angle)
            continue

    if topic == '/odometry/extended':
        if map_pose_zero_x is None:
            continue
        x_shifted = float(msg.odom.pose.pose.position.x + map_pose_zero_x)
        y_shifted = float(msg.odom.pose.pose.position.y + map_pose_zero_y)
        x_rotated = x_shifted * cos + y_shifted * sin
        y_rotated = - x_shifted * sin + y_shifted * cos
        x = int(x_rotated * MAP_SCALE) + ZERO_X
        y = int(y_rotated * MAP_SCALE) + ZERO_Y
        print(x)
        print(y)
        if odom_first_point_x is None:
            odom_first_point_x = x
            odom_first_point_y = y
            continue
        elif odom_second_point_x is None:
            odom_second_point_x = x
            odom_second_point_y = y
        else:
            odom_first_point_x = odom_second_point_x
            odom_first_point_y = odom_second_point_y
            odom_second_point_x = x
            odom_second_point_y = y
        rr, cc = line(odom_first_point_y, odom_first_point_x, odom_second_point_y, odom_second_point_x)
        try:
            odom_matrix[rr, cc] = 1
        except Exception as e:
            print(e)
            fig = plt.figure(figsize=(20, 40))
            plt.imshow(odom_matrix, origin='lower')
            plt.imsave('odometry_track_error.png', odom_matrix, origin='lower')
            break

plt.imshow(odom_matrix, origin='lower')
plt.imsave('odometry_track_rotated.png', odom_matrix, origin='lower')
