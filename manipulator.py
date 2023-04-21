# -*- coding: utf-8 -*-
# @File    : manipulator.py
# @Time    : 19/04/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import time
import pygame
import numpy as np
import game_function as gf
import cv2

from car import Car
from trajectory_planning import get_path, do_trajectory_planning


class Manipulator:
    zoom_duration = 1
    frame_rate = 60
    final_frames = int(zoom_duration * frame_rate)

    res = 20  # resolution of trajectory points

    def __init__(self, settings, screen, game_stats, workspace, car):
        self.settings = settings
        self.screen = screen
        self.game_stats = game_stats
        self.workspace = workspace
        self.car = car

        self.current_frame = 0
        self.pause = False

        self.w = 850
        self.h = 400
        self.sur_map = pygame.Surface((self.w, self.h))
        self.sur_robot = pygame.Surface((self.w, self.h),
                                        pygame.SRCALPHA)

        self._get_3D_map()
        self._get_zoomed_car()

        # a = [0.5 * zoomed_car.wheel_base * np.cos(-3.264),
        #      0.5 * zoomed_car.wheel_base * np.sin(-3.264),]
        self.pointer = 0
        self.end_memory = []
        end_point = self.workspace.green_end - self.workspace.blue_end
        end_point = np.array([end_point[0] - 0.5 * car.wheel_base * np.cos(-3.264),
                              end_point[1] - 0.5 * car.wheel_base * np.sin(-3.264),
                              -(self.car.height+self.car.wheel_radius)], dtype=np.float32)
        # print(np.sqrt(end_point[0] ** 2 + end_point[1] ** 2))
        # print(self.car.height+self.car.wheel_radius)
        self.paths = do_trajectory_planning(end_point, self.res)
        self.P_coordinates = self.paths[4]
        # print(self.paths[0])
        # print(self.P_coordinates)
        self.num_points = len(self.paths[0])

    def _get_3D_map(self):
        img = self.workspace.img

        # pre-cropped:
        dx = 700
        dy = int(dx / 1.42)
        x0 = 800
        y0 = 600
        self.zoom_factor = img.shape[0] / dy

        img = img[y0:y0 + dy, x0:x0 + dx]

        img_w = img.shape[1]
        img_h = img.shape[0]

        # Apply non-affine transformation
        # corner points from:
        cornersA = np.float32([[0, 0],
                               [img_w, 0],
                               [0, img_h],
                               [img_w, img_h]])
        # corner points to:
        points3d = [self.settings.map_screen['origin3d'],
                    self.settings.map_screen['xend'],
                    self.settings.map_screen['yend'],
                    [self.settings.map_screen['xlim'], self.settings.map_screen['ylim'], 0]]
        cornersB = np.float32([gf.point_3d_to_2d(*point) for point in points3d])
        # shift negative points:
        cornersB[:, 0] += abs(min(cornersB[:, 0])) + 10
        cornersB[:, 1] += abs(min(cornersB[:, 1])) + 80
        self.map_pos = cornersB[0]  # top left corner of the map

        M = cv2.getPerspectiveTransform(cornersA, cornersB)
        warped = cv2.warpPerspective(img, M, (self.settings.map_screen['w'],
                                              self.settings.map_screen['h']))
        warped = gf.cv2_to_pygame(warped)

        # Convert black pixels caused by non-affine transformation to white
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        black_pixels = np.where(gray == 0)
        map3d = warped.copy()
        map3d[black_pixels] = [255, 255, 255]

        self.sur_map = pygame.surfarray.make_surface(map3d)
        self.sur_map = pygame.transform.scale(self.sur_map,
                                              (self.w, self.h))

        # find blue end position after warp perspective transformation
        point = self.workspace.blue_end
        # blue end poisition relative to the cropped image
        homo = np.array([point[0] - x0, point[1] - y0, 1])

        # Multiply the homography matrix
        transformed_point = np.matmul(M, homo)

        # Convert homogeneous to cartesian coordinates
        transformed_point = transformed_point[:2] / transformed_point[2]
        self.car_origin2d = transformed_point

    def _get_zoomed_car(self):
        zoomed_car = Car(self.settings, self.sur_map, self.game_stats, self.workspace)
        zoomed_car.scale *= self.zoom_factor
        zoomed_car.reset_dimensions()
        zoomed_car.car_origin3d = np.float32([0, 0, zoomed_car.wheel_radius])
        zoomed_car.R_view = self.workspace.R_view
        zoomed_car.offset = self.car_origin2d
        zoomed_car.car_orientation = -3.264
        zoomed_car.apply_transformations()
        zoomed_car.draw()

        # get manipulator origin
        origin = [0.5 * zoomed_car.wheel_base * np.cos(-3.264),
                  0.5 * zoomed_car.wheel_base * np.sin(-3.264),
                  zoomed_car.height + zoomed_car.wheel_radius]
        self.manipulator_origin2d = gf.point_3d_to_2d(*origin, offset=self.car_origin2d)

    def update(self):
        self.sur_robot.fill((0, 0, 0, 0))
        if self.current_frame >= self.final_frames:
            self.pause = False
            # zooming-in finish, manipulator moving

            joints = get_path(self.paths, self.pointer, self.end_memory)
            if self.pointer == self.num_points - 1:
                self.P_coordinates[-1] = self.end_memory[0]

            for end_pos in self.end_memory:
                end_pos = end_pos * self.zoom_factor
                pos2d = gf.point_3d_to_2d(*end_pos, offset=self.manipulator_origin2d)
                pygame.draw.circle(self.sur_robot, (255, 0, 0), pos2d, 3)

            # plot via points
            last_via_points = self.P_coordinates[self.pointer // self.res:
                                                 self.pointer // self.res + 2, :]
            for point in last_via_points:
                point = point * self.zoom_factor
                pos2d = gf.point_3d_to_2d(*point, offset=self.manipulator_origin2d)
                pygame.draw.circle(self.sur_robot, (0, 0, 0), pos2d, 5)

            joints = [joint * self.zoom_factor for joint in joints]
            joints = [gf.point_3d_to_2d(*joint, offset=self.manipulator_origin2d)
                      for joint in joints]

            for i in range(len(joints) - 1):
                P1 = joints[i]
                P2 = joints[i + 1]
                # plot links
                pygame.draw.line(self.sur_robot, (0, 0, 255), P1, P2, 2)
                # plot joints
                pygame.draw.circle(self.sur_robot, (0, 0, 0), P1, 3)

            self.pointer += 1
            if self.pointer >= self.num_points:
                self.pause = True
                self.pointer = 0

        else:  # zooming
            offset = (self.workspace.map_pos[0] + self.settings.map_screen['topleft'][0],
                      self.workspace.map_pos[1] + self.settings.map_screen['topleft'][1])
            center = self.workspace.blue_end
            (x0, y0) = gf.point_3d_to_2d(center[0], center[1], self.car.wheel_radius,
                                         self.workspace.R_view, offset)
            (xf, yf) = (0, 0)

            scale_factor = self.current_frame / self.final_frames

            # Scale the subwindow
            scaled_width = int(self.w * scale_factor)
            scaled_height = int(self.h * scale_factor)
            self.sur_map_scaled = pygame.transform.scale(
                self.sur_map, (scaled_width, scaled_height))

            self.topleft = (int(x0 + scale_factor * (xf - x0)) + 0,
                            int(y0 + scale_factor * (yf - y0)) + 170)

            self.current_frame += 1

    def draw(self):
        self.screen.blit(self.sur_map_scaled, self.topleft)
        self.screen.blit(self.sur_robot, self.topleft)

