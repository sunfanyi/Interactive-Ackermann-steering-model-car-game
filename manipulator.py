# -*- coding: utf-8 -*-
# @File    : manipulator.py
# @Time    : 19/04/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm


import pygame
import numpy as np
import game_function as gf
import cv2

from car import Car


class Manipulator:
    zoom_duration = 2
    frame_rate = 60
    final_frames = int(zoom_duration * frame_rate)

    def __init__(self, settings, screen, game_stats, workspace, car):
        self.settings = settings
        self.screen = screen
        self.game_stats = game_stats
        self.workspace = workspace
        self.car = car

        self.current_frame = 0

        self.w = 850
        self.h = 400
        self.surface = pygame.Surface((self.w, self.h))
        self._get_3D_map()

        self._get_zoomed_car()

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
        cornersB = np.float32([gf.point_3d_to_2d(*point, self.workspace.R_view) for point in points3d])
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

        self.surface = pygame.surfarray.make_surface(map3d)
        self.surface = pygame.transform.scale(self.surface,
                                              (self.w, self.h))

        point = self.workspace.blue_end
        homo = np.array([point[0] - x0, point[1] - y0, 1])

        # Multiply the homography matrix
        transformed_point = np.matmul(M, homo)

        # Convert homogeneous to cartesian coordinates
        transformed_point = transformed_point[:2] / transformed_point[2]
        print(transformed_point)
        # pygame.draw.circle(self.surface, (255, 0, 0), (transformed_point[0], transformed_point[1]), 10)
        self.car_origin2d = transformed_point

    def _get_zoomed_car(self):
        zoomed_car = Car(self.settings, self.surface, self.game_stats, self.workspace)
        zoomed_car.scale *= self.zoom_factor
        zoomed_car.reset_dimensions()
        zoomed_car.car_origin3d = np.float32([0, 0, zoomed_car.wheel_radius])
        zoomed_car.R_view = self.workspace.R_view
        zoomed_car.offset = self.car_origin2d
        zoomed_car.car_orientation = -3.264
        zoomed_car.apply_transformations()
        zoomed_car.draw()

    def update(self):
        if self.current_frame >= self.final_frames:
            return
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
        self.surface_scaled = pygame.transform.scale(self.surface, (scaled_width, scaled_height))

        self.topleft = (int(x0 + scale_factor * (xf - x0)) + 0,
                        int(y0 + scale_factor * (yf - y0)) + 170)

        self.current_frame += 1

    def draw(self):
        self.screen.blit(self.surface_scaled, self.topleft)

