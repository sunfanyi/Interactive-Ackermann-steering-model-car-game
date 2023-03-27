# -*- coding: utf-8 -*-
# @File    : workspace.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame
import numpy as np
import cv2

import game_function as gf


class Workspace:
    def __init__(self, settings, screen, car):
        self.screen = screen
        self.settings = settings
        self.car = car

        img = cv2.imread('CWMap.jpg')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.img_w = img.shape[1]
        self.img_h = img.shape[0]

        # Apply non-affine transformation
        # corner points from:
        cornersA = np.float32([[0, 0],
                               [self.img_w, 0],
                               [0, self.img_h],
                               [self.img_w, self.img_h]])
        # corner points to:
        points3d = [self.settings.origin3d,
                    self.settings.xend,
                    self.settings.yend,
                    [self.settings.xlim, self.settings.ylim, 0]]
        cornersB = np.float32([gf.point_3d_to_2d(*point) for point in points3d])
        M = cv2.getPerspectiveTransform(cornersA, cornersB)
        warped = cv2.warpPerspective(img, M, (self.settings.screen_width,
                                              self.settings.screen_height))

        warped = gf.cv2_to_pygame(warped)

        # Convert black pixels caused by non-affine transformation to white
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        black_pixels = np.where(gray == 0)
        self.map_img2d = warped.copy()
        self.map_img2d[black_pixels] = [255, 255, 255]

    def draw(self):
        self.draw_map()
        self.draw_axes()

    def draw_map(self):
        merged_surface = pygame.Surface((self.settings.screen_width,
                                         self.settings.screen_height), pygame.SRCALPHA)

        map_surface = pygame.surfarray.make_surface(self.map_img2d)
        merged_surface.blit(map_surface, (0, 0))

        # for the zoomed in map:
        window_w = self.settings.zoom_region['window_width']
        window_h = self.settings.zoom_region['window_height']
        zoom_factor = self.settings.zoom_region['factor']
        crop_size_w = window_w / zoom_factor / 2
        crop_size_h = window_h / zoom_factor / 2

        zoomed_map_surface = pygame.Surface((window_w+2, window_h+2))

        # Crop:
        start_row = int(self.car.car_origin2d[0] - crop_size_w)
        start_col = int(self.car.car_origin2d[1] - crop_size_h)
        end_row = int(self.car.car_origin2d[0] + crop_size_w)
        end_col = int(self.car.car_origin2d[1] + crop_size_h)
        cropped = self.map_img2d[start_row:end_row, start_col:end_col]

        # Resize
        scaled = cv2.resize(cropped, None, fx=zoom_factor, fy=zoom_factor,
                            interpolation=cv2.INTER_CUBIC)

        # Embed cropped window
        leftx = self.settings.screen_width - window_w - 2
        rightx = self.settings.screen_width
        topy = 0
        boty = window_h + 2

        # pad to avoid index error caused by floating rounding
        padded = np.ones((window_w+2, window_h+2, 3)) * 255
        padded[:scaled.shape[0], :scaled.shape[1], :] = scaled
        pygame.surfarray.blit_array(zoomed_map_surface, padded)

        # aligned = pygame.transform.rotate(zoomed_map_surface, 90)

        # # aligned = pygame.transform.rotate(self.map_img2d, 1)
        merged_surface.blit(zoomed_map_surface, (leftx, topy))
        self.screen.blit(merged_surface, (0, 0))

        pygame.draw.line(self.screen, (0, 0, 0), (leftx, topy), (rightx, topy), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (leftx, topy), (leftx, boty), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (rightx, topy), (rightx, boty), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (leftx, boty), (rightx, boty), 2)

    def draw_axes(self):
        origin3d = self.settings.origin3d

        xend = self.settings.xend
        yend = self.settings.yend
        zend = self.settings.zend
        x_tick_interval = self.settings.x_tick_interval
        y_tick_interval = self.settings.y_tick_interval
        z_tick_interval = self.settings.z_tick_interval

        axes_font = pygame.font.Font(None, 24)  # font for axes labels
        tick_font = pygame.font.Font(None, 18)  # font for tick labels
        axes_color = (0, 0, 0)
        tick_color = (100, 100, 100)

        # Draw X-axis
        line = [origin3d, xend]
        _, xpoint_2d = gf.draw_line(self.screen, line, axes_color, 2)
        # X-axis label
        x_label = axes_font.render("X", True, axes_color)
        self.screen.blit(x_label, xpoint_2d)
        # X-axis ticks
        for i in range(0, xend[0] + x_tick_interval, x_tick_interval):
            tick_x, tick_y = gf.point_3d_to_2d(i, 0, 0)
            tick_label = tick_font.render(str(i), True, tick_color)
            self.screen.blit(tick_label, (tick_x, tick_y))

        # Draw Y-axis
        line = [origin3d, yend]
        _, ypoint_2d = gf.draw_line(self.screen, line, axes_color, 2)

        # Y-axis label
        y_label = axes_font.render("Y", True, axes_color)
        self.screen.blit(y_label, ypoint_2d)
        # Y-axis ticks
        for i in range(y_tick_interval, yend[1] + y_tick_interval, y_tick_interval):
            tick_x, tick_y = gf.point_3d_to_2d(0, i, 0)
            tick_label = tick_font.render(str(i), True, tick_color)
            self.screen.blit(tick_label, (tick_x, tick_y))

        # Draw Z-axis
        line = [origin3d, zend]
        _, zpoint_2d = gf.draw_line(self.screen, line, axes_color, 2)
        # Z-axis label
        z_label = axes_font.render("Z", True, axes_color)
        self.screen.blit(z_label, zpoint_2d)
        # Z-axis ticks
        for i in range(z_tick_interval, zend[2] + z_tick_interval, z_tick_interval):
            tick_x, tick_y = gf.point_3d_to_2d(0, 0, i)
            tick_label = tick_font.render(str(i), True, tick_color)
            self.screen.blit(tick_label, (tick_x, tick_y))





