import cv2
import numpy as np
import matplotlib.pyplot as plt
import game_function as gf

img = cv2.imread('CWMap.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

img_w = img.shape[1]
img_h = img.shape[0]

# Define the corner points
# From:


cornersA = np.float32([[0, 0],
                       [img_w, 0],
                       [0, img_h],
                       [img_w, img_h]])
# To:
cornersB = np.float32([[250., 200.],
                       [653.67975, 254.08282],
                       [144.17177, 397.47818],
                       [547.8515, 451.561]])

# cornersB = np.float32([gf.point_3d_to_2d(*point) for point in points3d])
# print(cornersA)
# print(cornersB)
M = cv2.getPerspectiveTransform(cornersA, cornersB)

warped = cv2.warpPerspective(img, M, (800,
                                      600))
# warped = np.flipud(warped)
# flipped = cv2.flip(warped, 1)
print(warped.shape)
# Convert black pixels caused by non-affine transformation to white
gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
black_pixels = np.where(gray == 0)
map_img2d = warped.copy()
map_img2d[black_pixels] = [255, 255, 255]

# show the output warped image
plt.imshow(map_img2d)
plt.show()
