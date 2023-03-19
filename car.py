# -*- coding: utf-8 -*-
# @File    : car.py
# @Time    : 18/02/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d


class Car:
    def __init__(self, length, width, height,
                 wheel_radius, wheel_width, wheel_offset, wheel_base=None):
        self.length = length
        self.width = width
        self.height = height
        self.wheel_radius = wheel_radius
        self.wheel_width = wheel_width
        self.wheel_offset = wheel_offset
        if wheel_base is None:
            self.wheel_base = self.length - 2 * self.wheel_radius
        else:
            self.wheel_base = wheel_base

        self.get_cuboid_corners()

    def update_plot(self, ax, T=np.eye(4)):
        self.plot_body(ax, T)
        self.plot_wheels(ax, T)

    def get_cuboid_corners(self):
        # corner points of the cuboid
        self.top_front_left = np.array([self.length / 2, self.width / 2, 0])
        self.top_front_right = np.array([self.length / 2, -self.width / 2, 0])
        self.top_rear_left = np.array([-self.length / 2, self.width / 2, 0])
        self.top_rear_right = np.array([-self.length / 2, -self.width / 2, 0])
        self.bot_front_left = np.array([self.length / 2, self.width / 2, self.height])
        self.bot_front_right = np.array([self.length / 2, -self.width / 2, self.height])
        self.bot_rear_left = np.array([-self.length / 2, self.width / 2, self.height])
        self.bot_rear_right = np.array([-self.length / 2, -self.width / 2, self.height])

    def plot_body(self, ax, T):
        # line segments for the car body
        body_lines = [
            np.array([self.top_front_left, self.top_front_right]),
            np.array([self.top_front_right, self.top_rear_right]),
            np.array([self.top_rear_right, self.top_rear_left]),
            np.array([self.top_rear_left, self.top_front_left]),
            np.array([self.bot_front_left, self. bot_front_right]),
            np.array([self.bot_front_right, self. bot_rear_right]),
            np.array([self.bot_rear_right, self.bot_rear_left]),
            np.array([self.bot_rear_left, self.bot_front_left]),
            np.array([self.top_front_left, self.bot_front_left]),
            np.array([self.top_front_right, self.bot_front_right]),
            np.array([self.top_rear_right, self.bot_rear_right]),
            np.array([self.top_rear_left, self.bot_rear_left])
        ]
        for line in body_lines:
            line = line.T
            line = np.vstack([line, np.ones(line.shape[1])])
            line_universe = np.matmul(T, line)
            ax.plot(line_universe[0], line_universe[1], line_universe[2], 'b')

    def plot_wheels(self, ax, T):
        x_shift = np.array([(self.length - self.wheel_base) / 2, 0, 0])
        y_shift = np.array([0, self.wheel_width / 2, 0])
        z_shift = np.array([0, 0, -self.wheel_offset])

        self.plot_wheel(ax, self.top_front_left - x_shift + z_shift, y_shift, T)
        self.plot_wheel(ax, self.top_front_right - x_shift + z_shift, y_shift, T)
        self.plot_wheel(ax, self.top_rear_left + x_shift + z_shift, y_shift, T)
        self.plot_wheel(ax, self.top_rear_right + x_shift + z_shift, y_shift, T)

    def plot_wheel(self, ax, center, y_shift, T, num_points=20):
        r = self.wheel_radius

        center1 = center + y_shift
        center2 = center - y_shift

        # points on circles
        t = np.linspace(0, 2 * np.pi, num_points)
        x1 = center1[0] + r * np.cos(t)
        y1 = center1[1] * np.ones_like(t)
        z1 = center1[2] + r * np.sin(t)
        x2 = center2[0] + r * np.cos(t)
        y2 = center2[1] * np.ones_like(t)
        z2 = center2[2] + r * np.sin(t)

        lines1 = np.array([x1, y1, z1, np.ones_like(x1)])
        lines_universe = np.matmul(T, lines1).astype('float')
        x1 = lines_universe[0]
        y1 = lines_universe[1]
        z1 = lines_universe[2]

        lines2 = np.array([x2, y2, z2, np.ones_like(x2)])
        lines_universe = np.matmul(T, lines2).astype('float')
        x2 = lines_universe[0]
        y2 = lines_universe[1]
        z2 = lines_universe[2]

        ax.plot(x1, y1, z1, 'r')
        ax.plot(x2, y2, z2, 'r')

        # fill cylinder circular surface
        ax.plot_surface(np.vstack([x1, x2]), np.vstack([y1, y2]),
                        np.vstack([z1, z2]), color='r', alpha=0.7)

        # # fill cylinder circular bases
        # center1 = np.hstack([center1, 1])
        # center1 = np.matmul(a, center1).astype('float')
        # center2 = np.hstack([center2, 1])
        # center2 = np.matmul(a, center2).astype('float')
        # circle1 = plt.Circle((center1[0], center1[2]), r, color='r', alpha=0.3)
        # circle2 = plt.Circle((center2[0], center2[2]), r, color='r', alpha=0.3)
        # ax.add_patch(circle1)
        # ax.add_patch(circle2)
        # art3d.pathpatch_2d_to_3d(circle1, z=center1[1], zdir="y")
        # art3d.pathpatch_2d_to_3d(circle2, z=center2[1], zdir="y")


if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    car = Car(length=5, width=2, height=1.5,
              wheel_radius=0.5, wheel_width=0.3,
              wheel_offset=0.2, wheel_base=3)
    from tools_kinematics import rotation, add_translation
    R = rotation(np.pi / 3, 'z')
    T = add_translation(R)
    car.update_plot(ax, T)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    ax.set_zlim([-2, 2])

    plt.show()
