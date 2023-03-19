import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d

import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d
from sympy import Matrix

from car import Car
from tools_cv import *
from tools_kinematics import rotation, add_translation
matplotlib.use('TkAgg')

img = cv2.imread('CWMap.jpg')  # BGR

img_R = extract_color(img, 'R')
img_G = extract_color(img, 'G')
img_B = extract_color(img, 'B')
R_coords = mask2xy(img_R)
G_coords = mask2xy(img_G)
B_coords = mask2xy(img_B)

import matplotlib.animation as animation

def update(frame, ax):
    R = rotation(np.pi, 'z')
    print(frame)
    T = add_translation(R, Matrix([frame * 10, 3000, 0, 1]))
    mycar.update_plot(ax, T)


fig = plt.figure(figsize=[8, 6])
ax = fig.add_subplot(projection='3d')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.set_xlim([0, img.shape[1]])
ax.set_ylim([img.shape[0], 0])
ax.set_zlim([0, 1000])

ax.scatter(R_coords[:, 0], R_coords[:, 1], 0, c='r', s=0.1, linewidth=0.1)
ax.scatter(G_coords[:, 0], G_coords[:, 1], 0, c='g', s=0.1, linewidth=0.1)
ax.scatter(B_coords[:, 0], B_coords[:, 1], 0, c='b', s=0.1, linewidth=0.1)

x, y = np.meshgrid(np.linspace(0, img.shape[1], 1000), np.linspace(0, img.shape[0], 1000))
z = np.zeros_like(x)
ax.plot_surface(x, y, z, alpha=0.2)

# draw the car:

scalr = 40
mycar = Car(length=5 * scalr, width=2 * scalr, height=1.5 * scalr,
            wheel_radius=0.5 * scalr, wheel_width=0.3 * scalr,
            wheel_offset=0.2 * scalr, wheel_base=3 * scalr)

ani = animation.FuncAnimation(fig, update, fargs=(ax,), frames=np.arange(0, 100), interval=20, repeat=True)

plt.show()

