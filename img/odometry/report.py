import numpy as np

import sys

sys.path.remove('/opt/ros/lunar/lib/python2.7/dist-packages')  # in order to import cv2 under python3
import cv2

sys.path.append('/opt/ros/lunar/lib/python2.7/dist-packages')  # append back in order to import rospy

map = cv2.imread('result.png')
map[map == [84, 1, 68]] = 0
map[map != [0, 0, 0]] = 255
cv2.imwrite('result_reversed.png', np.invert(map))

# odometry = cv2.imread('odometry_track_rotated.png')
# odometry[odometry == [84, 1, 68]] = 0
# odometry[odometry != [0, 0, 0]] = 255
# cv2.imwrite('map_odometry_track_rotated_reversed.png', np.invert(odometry))

