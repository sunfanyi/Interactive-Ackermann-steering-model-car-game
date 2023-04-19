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

class Manipulator:
    zoom_duration = 2
    frame_rate = 60
    final_frames = int(zoom_duration * frame_rate)

    def __init__(self, settings, screen, game_stats, workspace, my_car):
        self.settings = settings
        self.screen = screen
        self.game_stats = game_stats
        self.workspace = workspace
        self.my_car = my_car

        self.current_frame = 0

        self.w = 850
        self.h = 400
        self.surface = pygame.Surface((self.w, self.h))
        self._get_3D_map()
        # self.surface.fill((255, 0, 0))
        # pygame.draw.circle(self.surface, (0, 255, 0), (200, 150), 100)

        # r = self.settings.zoom_region['window_radius']
        # zoom_factor = self.settings.zoom_region['factor']
        # zoom_radius = r / zoom_factor / zoom_factor
        # img = self.workspace.map3d.astype(np.uint8)
        # car_center = self.workspace.blue_end
        # calibration_angle = 90
        #
        # start_row = np.round(car_center[0] - zoom_radius).astype(np.int32)
        # start_col = np.round(car_center[1] - zoom_radius).astype(np.int32)
        # end_row = np.round(car_center[0] + zoom_radius).astype(np.int32)
        # end_col = np.round(car_center[1] + zoom_radius).astype(np.int32)
        # pre_cropped = img[start_row:end_row, start_col:end_col]
        #
        # # Resize
        # scaled = cv2.resize(pre_cropped, (w, h),
        #                     interpolation=cv2.INTER_LINEAR)
        #
        # # Fill image to surface
        # pygame.surfarray.blit_array(self.surface, scaled)
        
    def _get_3D_map(self):
        img = self.workspace.img
        img_w = img.shape[1]
        img_h = img.shape[0]

        # Apply non-affine transformation
        # corner points from:
        dx = 700
        dy = dx / 1.42
        x0 = 800
        y0 = 600
        cornersA = np.float32([[x0, y0],
                               [x0 + dx, y0],
                               [x0, y0 + dy],
                               [x0 + dx, y0 + dy]])
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

        self.map3d = map3d
        self.surface = pygame.surfarray.make_surface(map3d)
        self.surface = pygame.transform.scale(self.surface,
                                              (self.w, self.h))
        # self.surface = pygame.Surface((w, h))

    def update(self):
        if self.current_frame >= self.final_frames:
            return
        offset = (self.workspace.map_pos[0] + self.settings.map_screen['topleft'][0],
                  self.workspace.map_pos[1] + self.settings.map_screen['topleft'][1])
        center = self.workspace.blue_end
        (x0, y0) = gf.point_3d_to_2d(center[0], center[1], self.my_car.wheel_radius,
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
