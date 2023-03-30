import numpy as np
import cv2
import matplotlib.pyplot as plt

from tools_cv import *



img = cv2.imread('Figures/CWMap.jpg')  # BGR
img_R, mask = extract_color(img, 'R')
# img_G = extract_color(img, 'G')
# img_B = extract_color(img, 'B')

show_img(img_R)
show_img(mask)
# show_img(img_G)
# show_img(img_B)
# show_img(img_R + img_G + img_B)

R_coords = mask2xy(img_R)
# G_coords = mask2xy(img_G)
# B_coords = mask2xy(img_B)

plt.scatter(R_coords[:, 0], R_coords[:, 1], c='r', s=0.1, linewidth=0.1)
# plt.scatter(G_coords[:, 0], G_coords[:, 1], c='g', s=0.1, linewidth=0.1)
# plt.scatter(B_coords[:, 0], B_coords[:, 1], c='b', s=0.1, linewidth=0.1)
plt.xlim([0, img.shape[1]])
plt.ylim([img.shape[0], 0])
plt.show()

for point in R_coords:
    x = point[0]
    y = point[1]
    count = 0
    if mask[x+1, y] != [0, 0, 0]:
        count += 1
    if mask[x-1, y] != [0, 0, 0]:
        count += 1
    if mask[x, y+1] != [0, 0, 0]:
        count += 1
    if mask[x, y-1] != [0, 0, 0]:
        count += 1
    if count == 1:
        print(x, y)

