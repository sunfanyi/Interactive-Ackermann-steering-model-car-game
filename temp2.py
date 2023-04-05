from tools_cv import *

# Read the image from file
img = cv2.imread('Figures/CWMap.jpg')

img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

img_R, mask = extract_color(img, 'R')

R_coords = mask2xy(mask)

plt.scatter(R_coords[:, 0], R_coords[:, 1], c='r', s=1, linewidth=1)
plt.xlim([0, img.shape[1]])
plt.ylim([img.shape[0], 0])
plt.show()
