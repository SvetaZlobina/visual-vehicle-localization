from skimage.draw import line


def draw_line(img, point1_x, point1_y, point2_x, point2_y):
    # print("point1_x = {}, point1_y = {}, point2_x = {}, point2_y = {}".format(point1_x, point1_y, point2_x, point2_y))
    rr, cc = line(point1_y, point1_x, point2_y, point2_x)
    # print(str(img[rr, cc].shape))
    img[rr, cc] = 255
