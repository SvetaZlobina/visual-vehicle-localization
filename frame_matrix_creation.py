import rosbag
import numpy as np
from matplotlib import pyplot as plt
from skimage.draw import line

bag = rosbag.Bag('localization_data/bags/2019-03-29-18-40-33_0.bag')

MAP_SCALE = 9.93

matrices = []
frame_x = None
frame_y = None
frame = None
correction_x = 0
correction_y = 0

for topic, msg, t in bag.read_messages():
    if topic == '/vision/front/left/road_recognition' and msg.header.stamp.nsecs == 988421689:
        x1 = None
        x2 = None
        y1 = None
        y2 = None
        for point in msg.view_region:
            if x1 is None:
                x1 = point.x
            elif x1 != point.x:
                x2 = point.x
            if y1 is None:
                y1 = point.y
            elif y1 != point.y:
                y2 = point.y
        print("x1:" + str(x1) + " y1:" + str(y1))
        print("x2:" + str(x2) + " y2:" + str(y2))
        if x1 != 0:
            correction_x = 0 - x1
        if y1 != 0:
            correction_y = 0 - y1
        frame_x = int((x2 + correction_x) * MAP_SCALE)
        frame_y = int((y2 + correction_y) * MAP_SCALE)
        frame = np.zeros((frame_y, frame_x), dtype=np.uint8)
        for elem in msg.markup_elements:
            for index in range(len(elem.pts) - 1):
                rr, cc = line(int((elem.pts[index].y + correction_y) * MAP_SCALE),
                              int((elem.pts[index].x + correction_x) * MAP_SCALE),
                              int((elem.pts[index + 1].y + correction_y) * MAP_SCALE),
                              int((elem.pts[index + 1].x + correction_x) * MAP_SCALE))
                frame[rr, cc] = 1
        for elem in msg.edges:
            for index in range(len(elem.pts) - 1):
                rr, cc = line(int((elem.pts[index].y + correction_y) * MAP_SCALE),
                              int((elem.pts[index].x + correction_x) * MAP_SCALE),
                              int((elem.pts[index + 1].y + correction_y) * MAP_SCALE),
                              int((elem.pts[index + 1].x + correction_x) * MAP_SCALE))
                frame[rr, cc] = 1
        break

print("correction_x:" + str(correction_x) + " correction_y:" + str(correction_y))
print("frame_x:" + str(frame_x) + " frame_y:" + str(frame_y))
print(frame)
fig = plt.figure(figsize=(20, 40))
plt.imshow(frame, origin='lower')
plt.show()
