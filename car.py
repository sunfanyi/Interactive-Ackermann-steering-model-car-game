# -*- coding: utf-8 -*-
# @File    : car.py
# @Time    : 18/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import numpy as np
import pygame

import game_function as gf


class Car:
    def __init__(self, settings, screen):

        self.settings = settings
        self.screen = screen

        scale = 40
        self.length = 5 * scale
        self.width = 2 * scale
        self.height = 1.5 * scale
        self.wheel_radius = 0.5 * scale
        self.wheel_width = 0.3 * scale
        self.wheel_offset = 0.2 * scale
        self.wheel_base = 3 * scale

        self.get_body_lines()

        # Transform matrix
        self.T_body = np.eye(4)

        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False



    def get_body_lines(self):
        # corner points of the cuboid
        self.top_front_left = np.array([self.length / 2, self.width / 2, 0])
        self.top_front_right = np.array([self.length / 2, -self.width / 2, 0])
        self.top_rear_left = np.array([-self.length / 2, self.width / 2, 0])
        self.top_rear_right = np.array([-self.length / 2, -self.width / 2, 0])
        self.bot_front_left = np.array([self.length / 2, self.width / 2, self.height])
        self.bot_front_right = np.array([self.length / 2, -self.width / 2, self.height])
        self.bot_rear_left = np.array([-self.length / 2, self.width / 2, self.height])
        self.bot_rear_right = np.array([-self.length / 2, -self.width / 2, self.height])

        # line segments for the car body
        self.body_lines_local = [
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

    def update_T(self, T):
        self.T_body = np.matmul(T, self.T_body)

    def update(self):

        self.car_moving()
        self.body_lines = []

        # apply transformation matrix T to each line segment
        for line in self.body_lines_local:
            line = line.T
            line = np.vstack([line, np.ones(line.shape[1])])
            line_universe = np.matmul(self.T_body, line)  # [4, 2], 4=[x, y, z, 1], 2=[p1, p2]
            self.body_lines.append(line_universe[:3, :].T)

    def car_moving(self):
        T_new = np.eye(4)
        if self.moving_right:
            T_new[0, 3] = self.settings.car_speed_factor
        if self.moving_left:
            T_new[0, 3] = -self.settings.car_speed_factor
        if self.moving_up:
            T_new[1, 3] = -self.settings.car_speed_factor
        if self.moving_down:
            T_new[1, 3] = self.settings.car_speed_factor

        self.update_T(T_new)

    def draw(self):
        for line in self.body_lines:
            gf.draw_line(self.screen, line)
'''
    def plot_wheels(self, T):
        x_shift = np.array([(self.length - self.wheel_base) / 2, 0, 0])
        y_shift = np.array([0, self.wheel_width / 2, 0])
        z_shift = np.array([0, 0, -self.wheel_offset])

        self.plot_wheel(ax, self.top_front_left - x_shift + z_shift, y_shift, T)
        self.plot_wheel(ax, self.top_front_right - x_shift + z_shift, y_shift, T)
        self.plot_wheel(ax, self.top_rear_left + x_shift + z_shift, y_shift, T)
        self.plot_wheel(ax, self.top_rear_right + x_shift + z_shift, y_shift, T)

    def plot_wheel(self, center, y_shift, T, num_points=20):
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
        lines1_universe = np.matmul(T, lines1).astype('float')
        x1 = lines1_universe[0]
        y1 = lines1_universe[1]
        z1 = lines1_universe[2]

        lines2 = np.array([x2, y2, z2, np.ones_like(x2)])
        lines2_universe = np.matmul(T, lines2).astype('float')
        x2 = lines2_universe[0]
        y2 = lines2_universe[1]
        z2 = lines2_universe[2]

        # ax.plot(x1, y1, z1, 'r')
        # ax.plot(x2, y2, z2, 'r')



        # fill cylinder circular surface
        # ax.plot_surface(np.vstack([x1, x2]), np.vstack([y1, y2]),
        #                 np.vstack([z1, z2]), color='r', alpha=0.7)

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
'''