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
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    if color == 'R':
        lower_red = np.array([0, 180, 50])
        upper_red = np.array([15, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([165, 180, 50])
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
        lower = np.array([a, 180, 50])
        upper = np.array([b, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)

    # Apply the mask to the original image
    result = img.copy()
    result[mask == 0, :] = [0, 0, 0]
    #     result[mask!=0, :] = [255, 255, 255]

    # apply opening to remove noise
    kernel = np.ones((5, 5), np.uint8)
    result = cv2.morphologyEx(result, cv2.MORPH_OPEN, kernel)

    return result


def show_img(image, title=None):
    image = image.astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

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



