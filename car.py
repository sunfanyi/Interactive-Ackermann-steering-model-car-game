# -*- coding: utf-8 -*-
# @File    : car.py
# @Time    : 18/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import numpy as np

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
        self.get_wheel_lines()

        # Transform matrices
        self.T_body = np.eye(4)
        self.T_wheels = [np.eye(4)] * 4  # FL, FR, RL, RR

        # Used to update transform matrices
        self.car_origin = np.array([0, 0, 0, 1])  # generalised coordinates
        self.car_orientation = 0  # in radians
        self.wheels_orientation = [0, 0, 0, 0]  # in radians

        self.moving_fwd = False
        self.moving_bwd = False
        self.turning_left = False
        self.turning_right = False

    def get_body_lines(self):
        """
        Get a list of 12 lines segments representing the car body
        """
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

    def get_wheel_lines(self):
        """
        get a list of 4 representing each wheel
        each list contains two arrays of line segments
        """
        x_shift = np.array([(self.length - self.wheel_base) / 2, 0, 0])
        y_shift = np.array([0, self.wheel_width / 2, 0])
        z_shift = np.array([0, 0, -self.wheel_offset])

        self.wheel_lines_local = []
        self.get_each_wheel(self.top_front_left - x_shift + z_shift, y_shift)
        self.get_each_wheel(self.top_front_right - x_shift + z_shift, y_shift)
        self.get_each_wheel(self.top_rear_left + x_shift + z_shift, y_shift)
        self.get_each_wheel(self.top_rear_right + x_shift + z_shift, y_shift)

    def get_each_wheel(self, center, y_shift, num_points=20):
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

        self.wheel_lines_local.append([np.array([x1, y1, z1]), np.array([x2, y2, z2])])

    def car_moving(self):
        """
        Capture keyboard input and move the T matrices for car and wheels.
        Y-axis was flipped, so anticlockwise becomes negative and clockwise becomes positive.
        """
        if self.moving_fwd:
            if self.turning_left:  # anticlockwise around z
                self.car_orientation -= self.settings.car_turning_speed
            if self.turning_right:  # clockwise around z
                self.car_orientation += self.settings.car_turning_speed

            self.car_origin[0] += self.settings.car_speed_factor * np.cos(self.car_orientation)  # x
            self.car_origin[1] += self.settings.car_speed_factor * np.sin(self.car_orientation)  # y
        if self.moving_bwd:
            if self.turning_left:  # clockwise around z
                self.car_orientation += self.settings.car_turning_speed
            if self.turning_right:  # anticlockwise around z
                self.car_orientation -= self.settings.car_turning_speed

            self.car_origin[0] -= self.settings.car_speed_factor * np.cos(self.car_orientation)  # x
            self.car_origin[1] -= self.settings.car_speed_factor * np.sin(self.car_orientation)  # y

        R = gf.rotation(self.car_orientation, 'z')
        self.T_body = gf.add_translation(R, self.car_origin)
        self.T_wheels = [gf.add_translation(R, self.car_origin) for i in range(4)]

    def update(self):
        self.car_moving()
        self.body_lines = []
        self.wheel_lines = []

        # apply transformation matrix T to each body line segment
        for line in self.body_lines_local:
            line = line.T
            line = np.vstack([line, np.ones(line.shape[1])])
            line_universe = np.matmul(self.T_body, line)  # [4, 2], 4=[x, y, z, 1], 2=[p1, p2]
            self.body_lines.append(line_universe[:3, :].T)

        # apply transformation matrix T to each wheel line segment
        for i in range(4):
            line1 = self.wheel_lines_local[i][0]
            line2 = self.wheel_lines_local[i][1]
            line1 = np.vstack([line1, np.ones(line1.shape[1])])
            line2 = np.vstack([line2, np.ones(line2.shape[1])])
            lines1_universe = np.matmul(self.T_wheels[i], line1).astype('float')
            lines2_universe = np.matmul(self.T_wheels[i], line2).astype('float')
            self.wheel_lines.append([lines1_universe[:3, :].T, lines2_universe[:3, :].T])

    def draw(self):
        for line in self.body_lines:
            gf.draw_line(self.screen, line)
        for i in range(4):  # four wheels
            # each wheel has two line segments
            line1 = self.wheel_lines[i][0]
            line2 = self.wheel_lines[i][1]
            for j in range(len(line1)-1):  # iterate through points
                point1 = line1[j]
                point2 = line1[j+1]
                gf.draw_line(self.screen, [point1, point2], (255, 0, 0))

                point1 = line2[j]
                point2 = line2[j+1]
                gf.draw_line(self.screen, [point1, point2], (255, 0, 0))
