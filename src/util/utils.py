from matplotlib import pyplot as plt
import math


def meters_to_pixels(x_in_meters, scale, zero_x):
    return int((x_in_meters + zero_x) * scale)


def meters_to_pixels_reversed(y_in_meters, scale, zero_y, size_y):
    value = size_y - int((y_in_meters + zero_y) * scale)
    if value >= size_y:
        value = size_y - 1
    return value


def rotate_on_angle(x, y, angle, ox, oy):
    """ Rotate point with coordinates (x,y) on angle clockwise around origin point with coordinates (ox,oy) """
    cos = math.cos(angle)
    sin = math.sin(angle)
    x_rotated = ox + (x - ox) * cos - (y - oy) * sin
    y_rotated = oy + (x - ox) * sin + (y - oy) * cos
    return int(y_rotated), int(x_rotated)


def save_array_as_png(img_array, file_name):
    plt.figure(figsize=(20, 40))
    plt.imsave('{}.png'.format(file_name), img_array)
    plt.close()
