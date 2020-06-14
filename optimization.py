from map import Map
from bag import Bag
from frame import Frame

map = Map('localization_data/map/map_info.json')
# map.save_as_png('map')

bag = Bag('localization_data/bags/2019-03-29-18-40-33_0.bag')
for topic, msg, t in bag.file.read_messages():
    if topic == '/vision/front/left/road_recognition' and msg.header.stamp.nsecs == 988421689:
        frame = Frame(msg, map.scale)
        # frame.save_as_png('frame')
        frame_sum = frame.frame_as_img.sum()
        print(frame_sum)
        break
