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
    def __init__(self, settings, screen, scale=40):
        self.settings = settings
        self.screen = screen
        self.scale = scale

        self.reset_dimensions()

        # indicator of how many cycles the wheels have turned
        self.wheel_phi_counter = 0

        # Transform matrices
        self.T_body = np.eye(4)
        self.T_wheels = [np.eye(4)] * 4  # FL, FR, RL, RR

        # Used to update transform matrices
        self.car_origin3d = np.float32([0., 0., 0.])
        self.car_origin2d = gf.point_3d_to_2d(*self.car_origin3d)
        self.car_orientation = 0  # in radians
        self.wheels_orientation = np.float32([0, 0, 0, 0])  # in radians, 4 wheels

        # View
        self.R_view = gf.trimetric_view()
        self.offset = self.settings.map_screen['origin2d']

        # Car control
        self.moving_fwd = False
        self.moving_bwd = False
        self.turning_left = False
        self.turning_right = False
        self.accelerate = False

    def reset_dimensions(self):
        self.length = 3.6 * self.scale
        self.width = 2.6 * self.scale
        self.height = 1.5 * self.scale
        self.wheel_radius = 0.6 * self.scale
        self.wheel_width = 0.5 * self.scale
        self.wheel_offset = 0.2 * self.scale
        self.wheel_base = 2 * self.scale

        self.get_body_lines()
        self.get_wheel_lines()

    def get_body_lines(self):
        """
        Get a list of 12 lines segments representing the car body, in car frame
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

        self.wheel_curves_local = []
        self.wheel_centers_local = np.array([self.top_front_left - x_shift + z_shift,
                                             self.top_front_right - x_shift + z_shift,
                                             self.top_rear_left + x_shift + z_shift,
                                             self.top_rear_right + x_shift + z_shift])

        def get_each_wheel(center, y_shift, num_points=20):
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
            self.wheel_curves_local.append([np.array([x1, y1, z1]), np.array([x2, y2, z2])])

        get_each_wheel(self.wheel_centers_local[0], y_shift)
        get_each_wheel(self.wheel_centers_local[1], y_shift)
        get_each_wheel(self.wheel_centers_local[2], y_shift)
        get_each_wheel(self.wheel_centers_local[3], y_shift)


    def wheel_rotating_animation(self):
        """
        Drawing lines from wheels curves, in the direction of wheel width,
        to simulate rotating wheels.
        Each wheel has two curves, each curve has 20 points.
        Take 4 points from each curve, and draw lines between them.
        """
        wheel_line_interval = int(20/4)
        if self.moving_fwd or self.moving_bwd:
            # update wheel lines
            self.wheel_phi_counter += 1
            if self.wheel_phi_counter == wheel_line_interval:
                # 20 is the wheel line density
                self.wheel_phi_counter = 0
        j = self.wheel_phi_counter

        self.wheel_lines = []
        for i in range(4):  # four wheels
            # wheel lines in width direction
            # Keep four lines, keep updating
            curve1 = self.wheel_curves[i][0]
            curve2 = self.wheel_curves[i][1]

            points1 = np.array([curve1[j],
                                curve1[j + wheel_line_interval * 1],
                                curve1[j + wheel_line_interval * 2],
                                curve1[j + wheel_line_interval * 3]])
            points2 = np.array([curve2[j],
                                curve2[j + wheel_line_interval * 1],
                                curve2[j + wheel_line_interval * 2],
                                curve2[j + wheel_line_interval * 3]])

            self.wheel_lines.append([points1, points2])

    def update_trans_mat(self):
        """
        For each wheel:
            T_1: wheel frame (rotation)
            T_2: wheel frame to car frame (translation)
            T_body: car frame to global frame
        """
        R = gf.rotation(self.car_orientation, 'z')
        self.T_body = gf.add_translation(R, self.car_origin3d)
        for i in range(4):
            R = gf.rotation(self.wheels_orientation[i], 'z')  # clockwise is positive
            # R = gf.rotation(0, 'z')  # clockwise is positive
            T_1 = gf.add_translation(R)

            T_2 = gf.add_translation(np.eye(3), -self.wheel_centers_local[i])
            T_CW = np.matmul(T_2, T_1)
            self.T_wheels[i] = np.matmul(self.T_body, T_CW)

        self.car_origin2d = gf.point_3d_to_2d(*self.car_origin3d)

    def apply_transformations(self):
        self.update_trans_mat()

        self.body_lines = []
        self.wheel_curves = []

        # apply transformation matrix T to each body line segment
        for line in self.body_lines_local:
            line = line.T
            line = np.vstack([line, np.ones(line.shape[1])])
            line_universe = np.matmul(self.T_body, line)  # [4, 2], 4=[x, y, z, 1], 2=[p1, p2]
            self.body_lines.append(line_universe[:3, :].T)

        # apply transformation matrix T to each wheel curve
        for i in range(4):
            # all points shoule be in wheel frame
            curve1 = self.wheel_curves_local[i][0] - self.wheel_centers_local[i].reshape(3, 1)
            curve2 = self.wheel_curves_local[i][1] - self.wheel_centers_local[i].reshape(3, 1)
            curve1 = np.vstack([curve1, np.ones(curve1.shape[1])])
            curve2 = np.vstack([curve2, np.ones(curve2.shape[1])])
            curve1_universe = np.matmul(self.T_wheels[i], curve1).astype('float')
            curve2_universe = np.matmul(self.T_wheels[i], curve2).astype('float')
            self.wheel_curves.append([curve1_universe[:3, :].T, curve2_universe[:3, :].T])

    def update(self):
        """
        Capture car moving from keyboard input and move the T matrices for car and wheels.
        Y-axis was flipped, so anticlockwise becomes negative and clockwise becomes positive.
        """

        if self.turning_left or self.turning_right:
            speed = self.settings.car['speed_during_steering']
        else:
            speed = self.settings.car['speed']

        if self.accelerate:
            speed *= 2

        if self.moving_fwd:
            if self.turning_left:  # anticlockwise around z
                self.car_orientation -= self.settings.car['turning_speed']
                self.wheels_orientation = self.wheels_orientation - 0.1
            if self.turning_right:  # clockwise around z
                self.car_orientation += self.settings.car['turning_speed']
                self.wheels_orientation = self.wheels_orientation + 0.1

            self.car_origin3d[0] += speed * np.cos(self.car_orientation)  # x
            self.car_origin3d[1] += speed * np.sin(self.car_orientation)  # y
        if self.moving_bwd:
            if self.turning_left:  # clockwise around z
                self.car_orientation += self.settings.car['turning_speed']
                self.wheels_orientation = self.wheels_orientation + 0.1
            if self.turning_right:  # anticlockwise around z
                self.car_orientation -= self.settings.car['turning_speed']
                self.wheels_orientation = self.wheels_orientation - 0.1

            self.car_origin3d[0] -= speed * np.cos(self.car_orientation)  # x
            self.car_origin3d[1] -= speed * np.sin(self.car_orientation)  # y

        self.apply_transformations()

    def draw(self):
        self.wheel_rotating_animation()
        for line in self.body_lines:
            gf.draw_line(self.screen, line, R=self.R_view,
                         offset=self.offset)
        for i in range(4):  # four wheels
            # wheel curves
            # each wheel has two line segments
            curve1 = self.wheel_curves[i][0]
            curve2 = self.wheel_curves[i][1]
            for j in range(len(curve1)-1):  # iterate through points
                point1 = curve1[j]
                point2 = curve1[j+1]
                gf.draw_line(self.screen, [point1, point2], (255, 0, 0), R=self.R_view,
                             offset=self.offset)

                point1 = curve2[j]
                point2 = curve2[j+1]
                gf.draw_line(self.screen, [point1, point2], (255, 0, 0), R=self.R_view,
                             offset=self.offset)

            # wheel lines
            line1 = self.wheel_lines[i][0]
            line2 = self.wheel_lines[i][1]
            for j in range(4):
                point1 = line1[j]
                point2 = line2[j]
                gf.draw_line(self.screen, [point1, point2], (0, 0, 255), R=self.R_view,
                             offset=self.offset)


class LargeCar(Car):
    def __init__(self, settings, screen, scale=40):
        zoomed_scale = scale * settings.zoom_region['factor']
        super().__init__(settings, screen, zoomed_scale)
        self.car_origin3d = np.array([0, 0, 0])

        if self.settings.zoom_region['3d']:  # trimetric view
            self.R_view = gf.trimetric_view()
        else:  # top view
            self.R_view = np.eye(3)

        topleft = self.settings.zoom_region['topleft']
        self.offset = (topleft[0] + self.settings.zoom_region['radius'] + 5,
                       topleft[1] + self.settings.zoom_region['radius'] + 5)

    def update_zoomed_map(self, car_orientation, wheels_orientation):
        if self.settings.zoom_region['car_fixed']:
            self.car_orientation = np.pi/2
        else:
            self.car_orientation = car_orientation
        self.wheels_orientation = wheels_orientation

        self.apply_transformations()
