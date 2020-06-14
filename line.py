from skimage.draw import line


def draw_line(img, point1_x, point1_y, point2_x, point2_y):
    rr, cc = line(point1_y, point1_x, point2_y, point2_x)
    img[rr, cc] = 1

