import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path

# Define the four points
x = [1, 2, 3, 2]
y = [1, 2, 1, 0]

# Create a numpy array with the x and y coordinates of the points
pts = np.array([x, y]).T

# Create a closed path from the points
path = Path(pts, closed=True)

# Get the boundary polygon from the path
boundary = path.to_polygons()[0]

# Create a grid of coordinates for the mask image
x_coords = np.arange(np.min(x), np.max(x)+1)
y_coords = np.arange(np.min(y), np.max(y)+1)
xx, yy = np.meshgrid(x_coords, y_coords)
coords = np.vstack((xx.ravel(), yy.ravel())).T

# Create an empty mask array
mask = np.zeros((len(y_coords), len(x_coords)))

# Loop over the boundary lines and set mask values to 1
for i in range(len(boundary)-1):
    x0, y0 = boundary[i]
    x1, y1 = boundary[i+1]
    mask[int(y0), int(x0):int(x1)+1] = 1
    mask[int(y1), int(x0):int(x1)+1] = 1
    mask[int(y0):int(y1)+1, int(x0)] = 1
    mask[int(y0):int(y1)+1, int(x1)] = 1

# Plot the mask image
plt.imshow(mask, extent=[np.min(x), np.max(x), np.min(y), np.max(y)], cmap='gray')
plt.show()