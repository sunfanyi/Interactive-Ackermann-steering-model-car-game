# -*- coding: utf-8 -*-
# @File    : car.py
# @Time    : 18/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import numpy as np

import game_function as gf


class Car:
    def __init__(self, settings, screen, scale=40):
        self.settings = settings
        self.screen = screen

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
        self.car_origin3d = np.array([0, 0, 0])  # generalised coordinates
        self.car_origin2d = gf.point_3d_to_2d(*self.car_origin3d)
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

    def update(self):
        """
        Capture car moving from keyboard input and move the T matrices for car and wheels.
        Y-axis was flipped, so anticlockwise becomes negative and clockwise becomes positive.
        """
        if self.moving_fwd:
            if self.turning_left:  # anticlockwise around z
                self.car_orientation -= self.settings.car_turning_speed
            if self.turning_right:  # clockwise around z
                self.car_orientation += self.settings.car_turning_speed

            self.car_origin3d[0] += self.settings.car_speed_factor * np.cos(self.car_orientation)  # x
            self.car_origin3d[1] += self.settings.car_speed_factor * np.sin(self.car_orientation)  # y
        if self.moving_bwd:
            if self.turning_left:  # clockwise around z
                self.car_orientation += self.settings.car_turning_speed
            if self.turning_right:  # anticlockwise around z
                self.car_orientation -= self.settings.car_turning_speed

            self.car_origin3d[0] -= self.settings.car_speed_factor * np.cos(self.car_orientation)  # x
            self.car_origin3d[1] -= self.settings.car_speed_factor * np.sin(self.car_orientation)  # y

        R = gf.rotation(self.car_orientation, 'z')
        car_origin = np.hstack([self.car_origin3d, 1])  # generalised form
        self.T_body = gf.add_translation(R, car_origin)
        self.T_wheels = [gf.add_translation(R, car_origin) for i in range(4)]
        self.car_origin2d = gf.point_3d_to_2d(*self.car_origin3d)

    def apply_transformations(self):
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
        self.apply_transformations()
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


class LargeCar(Car):
    def __init__(self, settings, screen, scale=40):
        zoomed_scale = scale * settings.zoom_region['factor']
        super().__init__(settings, screen, zoomed_scale)
        self.car_origin3d = np.array([0, 0, 0])

    def update_mat(self, car_orientation, wheels_orientation):
        if self.settings.zoom_region['car_fixed']:
            self.car_orientation = np.pi/2
        else:
            self.car_orientation = car_orientation
        self.wheels_orientation = wheels_orientation

        R = gf.rotation(self.car_orientation, 'z')
        car_origin = np.hstack([self.car_origin3d, 1])  # generalised form
        self.T_body = gf.add_translation(R, car_origin)
        self.T_wheels = [gf.add_translation(R, car_origin) for i in range(4)]
        self.car_origin2d = gf.point_3d_to_2d(*self.car_origin3d)

    def draw(self):
        centerx = self.settings.zoom_region['centerx']
        centery = self.settings.zoom_region['centery']
        self.apply_transformations()
        for line in self.body_lines:
            draw_line(self.screen, line, offset=(centerx, centery))
        for i in range(4):  # four wheels
            # each wheel has two line segments
            line1 = self.wheel_lines[i][0]
            line2 = self.wheel_lines[i][1]
            for j in range(len(line1)-1):  # iterate through points
                point1 = line1[j]
                point2 = line1[j+1]
                draw_line(self.screen, [point1, point2], (255, 0, 0),
                             offset=(centerx, centery))

                point1 = line2[j]
                point2 = line2[j+1]
                draw_line(self.screen, [point1, point2], (255, 0, 0),
                             offset=(centerx, centery))




import pygame
def draw_line(screen, line, color=(0, 0, 0), linewidth=1, offset=(0,0)):
    p1 = line[0]
    p2 = line[1]

    p1_2d = point_3d_to_2d(p1[0], p1[1], p1[2], offset)
    p2_2d = point_3d_to_2d(p2[0], p2[1], p2[2], offset)

    pygame.draw.line(screen, color, p1_2d, p2_2d, linewidth)

    return p1_2d, p2_2d


def point_3d_to_2d(x, y, z, offset):
    # flip y-axis for visualisation,
    # so anticlockwise becomes negative and clockwise becomes positive
    y = - y
    x *= 800/5000/1.6
    y *= 600/3600/1.2
    z *= 0.1

    # Trimetric projection fron 3d to 2d
    x_rotation = rotation(0/180 * np.pi, 'x')
    z_rotation = rotation(0/180 * np.pi, 'z')

    R = np.matmul(x_rotation, z_rotation)

    x_2d, y_2d, z_2d = np.matmul(R, np.array([x, y, z]))

    x_2d, y_2d = (offset[0] + x_2d, offset[1] - y_2d)

    return x_2d, y_2d


def rotation(theta, direction):
    if direction == 'x':
        R = np.array([[1, 0, 0],
                      [0, np.cos(theta), -np.sin(theta)],
                      [0, np.sin(theta), np.cos(theta)]])
    elif direction == 'y':
        R = np.array([[np.cos(theta), 0, np.sin(theta)],
                      [0, 1, 0],
                      [-np.sin(theta), 0, np.cos(theta)]])
    elif direction == 'z':
        R = np.array([[np.cos(theta), -np.sin(theta), 0],
                      [np.sin(theta), np.cos(theta), 0],
                      [0, 0, 1]])
    return R