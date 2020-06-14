from matplotlib import pyplot as plt


def meters_to_pixels(x_in_meters, scale, zero_x):
    return int((x_in_meters + zero_x) * scale)


def meters_to_pixels_reversed(y_in_meters, scale, zero_y, size_y):
    return size_y - int((y_in_meters + zero_y) * scale)


def save_array_as_png(img_array, file_name):
    plt.figure(figsize=(20, 40))
    plt.imsave('{}.png'.format(file_name), img_array)
