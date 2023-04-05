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
from tools_cv import extract_color


class Workspace:
    def __init__(self, settings, screen, car):
        self.screen = screen
        self.settings = settings
        self.car = car

        img = cv2.imread(self.settings.map_screen['path'])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.get_3D_map(img)
        self.map2d = self.pad_2D_map(img)

        _, self.red_line = extract_color(img, 'R')
        # self.red_line = self.pad_2D_map(red_line)

    def get_3D_map(self, img):
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
        M = cv2.getPerspectiveTransform(cornersA, cornersB)
        warped = cv2.warpPerspective(img, M, (self.settings.map_screen['w'],
                                              self.settings.map_screen['h']))
        warped = gf.cv2_to_pygame(warped)

        # Convert black pixels caused by non-affine transformation to white
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        black_pixels = np.where(gray == 0)
        self.map3d = warped.copy()
        self.map3d[black_pixels] = [255, 255, 255]

    def pad_2D_map(self, img):
        """
        Pad edges with zero for cropping the zoomed in region
        when the car is in the boundary of the map
        """
        pad_size = 1000
        img = img
        pad = np.full((img.shape[0] + 2 * pad_size,
                       img.shape[1] + 2 * pad_size,
                       3), 255, dtype=np.uint8)
        pad[pad_size:pad_size + img.shape[0],
        pad_size:pad_size + img.shape[1]] = img
        self.pad_size = pad_size

        return pad

    def draw(self):
        self.draw_map()
        self.draw_axes()

    def draw_map(self):
        map_surface = pygame.surfarray.make_surface(self.map3d)
        self.screen.blit(map_surface, (0, 0))

    def draw_axes(self):
        origin3d = self.settings.map_screen['origin3d']

        xend = self.settings.map_screen['xend']
        yend = self.settings.map_screen['yend']
        zend = self.settings.map_screen['zend']
        x_tick_interval = self.settings.map_screen['x_tick_interval']
        y_tick_interval = self.settings.map_screen['y_tick_interval']
        z_tick_interval = self.settings.map_screen['z_tick_interval']

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
        for i in range(0, xend[0], x_tick_interval):
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
        for i in range(y_tick_interval, yend[1], y_tick_interval):
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
