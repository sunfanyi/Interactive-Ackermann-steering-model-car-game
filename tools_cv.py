# -*- coding: utf-8 -*-
# @File    : tools_cv.py
# @Time    : 10/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import cv2
import numpy as np
import matplotlib.pyplot as plt


def extract_color(img, color):
    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    if color == 'R':
        lower_red = np.array([0, 210, 50])
        upper_red = np.array([15, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([165, 210, 50])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red)

        mask = mask1 + mask2
    else:
        if color == 'G':
            a = 45
            b = 75
        elif color == 'B':
            a = 90
            b = 120
        else:
            raise ValueError('Color not identified')
        lower = np.array([a, 180, 50])
        upper = np.array([b, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)

    # apply opening to remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Apply the mask to the original image
    result = img.copy()
    result[mask == 0, :] = [0, 0, 0]
    return result, mask.astype(np.bool)


def mask2xy(mask):
    """
    From mask to xy coordinates
    :param mask: [h, w], boolean
    :return: xy coordinates with shape [N, 2]
    """
    coords = np.argwhere(mask)
    coords = coords.reshape((-1, 2))  # N x 2
    coords = np.fliplr(coords)  # (y, x) to (x, y)
    return coords


def show_img(image, title=None):
    image = image.astype(np.uint8)

    plt.imshow(image)
    # plt.axis('off')
    if title is not None:
        plt.title(title)

    plt.show()


def plot_hist(img_grey, bins=256, range=(0, 255), title=None):
    hist, bins = np.histogram(img_grey.flatten(), bins=bins, range=range)

    plt.bar(bins[:-1], hist, width=bins[1] - bins[0],
            color='lightblue', edgecolor='navy')
    plt.xlim([0, 256])
    plt.xlabel('Pixel value')
    plt.ylabel('Frequency')
    if title is not None:
        plt.title(title)
    plt.show()
    return hist, bins



