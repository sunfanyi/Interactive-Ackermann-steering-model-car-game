import cv2
import numpy as np

# read image
img = cv2.imread('CWMap.jpg')
img = cv2.resize(img, None, fx=0.2, fy=0.2)
hh, ww = img.shape[:2]
hh2 = hh // 2
ww2 = ww // 2

# define circles
radius1 = 100
radius2 = 75
xc = hh // 2
yc = ww // 2

# draw filled circles in white on black background as masks
mask = np.zeros_like(img)
mask = cv2.circle(mask, (xc,yc), radius1, (255,255,255), -1)

# subtract masks and make into single channel
mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

# apply the mask to the image
result = cv2.bitwise_and(img, img, mask=mask)

gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
black_pixels = np.where(gray == 0)
final = result.copy()
final[black_pixels] = [255, 255, 255]


# save results
cv2.imshow('lena_circle_masks', final)

cv2.imshow('image', img)
cv2.imshow('mask', mask)
cv2.waitKey(0)
cv2.destroyAllWindows()
