import rosbag
import numpy as np
from matplotlib import pyplot as plt
from skimage.draw import line

SIZE_X = 2375
SIZE_Y = 1779
ZERO_X = 575
ZERO_Y = 1583
MAP_SCALE = 9.93

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
        # x = int(float(msg.pose.position.x)*MAP_SCALE)+ZERO_X
        # y = int(float(msg.pose.position.y)*MAP_SCALE)+ZERO_Y
        if map_first_point_x is None:
            # map_first_point_x = x
            # map_first_point_y = y
            map_pose_zero_x = msg.pose.position.x
            map_pose_zero_y = msg.pose.position.y
            print(map_pose_zero_x)
            print(map_pose_zero_y)
            continue
        # elif map_second_point_x is None:
        #     map_second_point_x = x
        #     map_second_point_y = y
        # else:
        #     map_first_point_x = map_second_point_x
        #     map_first_point_y = map_second_point_y
        #     map_second_point_x = x
        #     map_second_point_y = y
        # rr, cc = line(map_first_point_y, map_first_point_x, map_second_point_y, map_second_point_x)
        # map_matrix[rr, cc] = 1

    if topic == '/odometry/extended':
        if map_pose_zero_x is None:
            continue
        x = int(float(msg.odom.pose.pose.position.x + map_pose_zero_x) * MAP_SCALE) + ZERO_X
        y = int(float(msg.odom.pose.pose.position.y + map_pose_zero_y) * MAP_SCALE) + ZERO_Y
        print(msg.odom.pose.pose.position.x)
        print(msg.odom.pose.pose.position.y)
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
        except:
            fig = plt.figure(figsize=(20, 40))
            plt.imshow(odom_matrix, origin='lower')
            plt.imsave('odometry_track.png', odom_matrix, origin='lower')
            break

# fig = plt.figure(figsize=(20, 40))
# plt.imshow(map_matrix, origin='lower')
# plt.imsave('map_pose_track.png', map_matrix, origin='lower')

plt.imshow(odom_matrix, origin='lower')
plt.imsave('odometry_track.png', odom_matrix, origin='lower')
