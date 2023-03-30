import cv2
import numpy as np
import game_function as gf

img = cv2.imread('Figures/CWMap.jpg')


R = gf.trimetric_view()
# R = np.eye(3)
R = gf.rotation(np.pi/4, 'x')

img = img.astype(np.uint8)


img = cv2.resize(img, (800, 600),
                 interpolation=cv2.INTER_LINEAR)
# Apply the transformation matrix to the image
# transformed_img = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
img = cv2.warpPerspective(img, R, (img.shape[1], img.shape[0]))

# show image
cv2.imshow('image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()


# Define the trimetric projection matrix

#
# a = np.sqrt(2) / 2
# proj_matrix = np.array([[a, -a, 0, 0],
#                         [1/4, 1/4, -a/2, 0],
#                         [0, 0, 0, 0],
#                         [0, 0, 0, 1]], dtype=np.float32)
#
# proj_matrix = proj_matrix[:3, :3]
# proj_matrix[2,2] = 1
# proj_matrix = proj_matrix.astype(np.float32)
#
# # Apply the trimetric projection matrix to the image
# projected_img = cv2.warpPerspective(img.astype(np.uint8), proj_matrix, (img.shape[1], img.shape[0]))
#
# # Display the projected image
# cv2.imshow('Projected Image', projected_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()