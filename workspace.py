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
from tools_cv import extract_color, mask2xy


class Workspace:
    def __init__(self, settings, screen):
        self.screen = screen
        self.settings = settings
        self.map_settings = settings.map_screen

        asset_url = gf.resource_path(self.map_settings['path'])
        img = cv2.imread(asset_url)
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # self.img = np.ones([3680, 5224, 3]).astype(np.uint8)

        self.R_view = gf.trimetric_view()
        self._get_3D_map()
        self.map2d = self._pad_2D_map()
        self._get_axes()

        self._extract_map_features()

    def _get_3D_map(self):
        img = self.img
        img_w = img.shape[1]
        img_h = img.shape[0]

        # Apply non-affine transformation
        # corner points from:
        cornersA = np.float32([[0, 0],
                               [img_w, 0],
                               [0, img_h],
                               [img_w, img_h]])
        # corner points to:
        points3d = [self.map_settings['origin3d'],
                    self.map_settings['xend'],
                    self.map_settings['yend'],
                    [self.map_settings['xlim'], self.map_settings['ylim'], 0]]
        cornersB = np.float32([gf.point_3d_to_2d(*point, self.R_view) for point in points3d])
        # shift negative points:
        cornersB[:, 0] += abs(min(cornersB[:, 0])) + 10
        cornersB[:, 1] += abs(min(cornersB[:, 1])) + 80
        self.map_pos = cornersB[0]  # top left corner of the map

        M = cv2.getPerspectiveTransform(cornersA, cornersB)
        warped = cv2.warpPerspective(img, M, (self.map_settings['w'],
                                              self.map_settings['h']))
        warped = gf.cv2_to_pygame(warped)

        # Convert black pixels caused by non-affine transformation to white
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        black_pixels = np.where(gray == 0)
        map3d = warped.copy()
        map3d[black_pixels] = [255, 255, 255]

        self.map3d = map3d
        self.map3d_surf = pygame.surfarray.make_surface(map3d)

    def _pad_2D_map(self):
        """
        Pad edges with zero for cropping the zoomed in region
        when the car is in the boundary of the map
        """
        pad_size = 1000
        img = self.img
        pad = np.full((img.shape[0] + 2 * pad_size,
                       img.shape[1] + 2 * pad_size,
                       3), 255, dtype=np.uint8)
        pad[pad_size:pad_size + img.shape[0],
        pad_size:pad_size + img.shape[1]] = img
        self.pad_size = pad_size

        return pad

    def _get_axes(self):
        self.axes = pygame.surface.Surface((self.map_settings['w'],
                                            self.map_settings['h']),
                                           pygame.SRCALPHA)

        origin3d = self.map_settings['origin3d']

        xend = self.map_settings['xend']
        yend = self.map_settings['yend']
        zend = self.map_settings['zend']
        x_tick_interval = self.map_settings['x_tick_interval']
        y_tick_interval = self.map_settings['y_tick_interval']
        z_tick_interval = self.map_settings['z_tick_interval']

        axes_font = pygame.font.Font(None, 24)  # font for axes labels
        tick_font = pygame.font.Font(None, 18)  # font for tick labels
        axes_color = (0, 0, 0)
        tick_color = (100, 100, 100)

        # Draw X-axis
        line = [origin3d, xend]
        _, xpoint_2d = gf.draw_line(self.axes, line, axes_color, 2,
                                    self.R_view, self.map_pos)
        # X-axis label
        x_label = axes_font.render("X", True, axes_color)
        self.axes.blit(x_label, xpoint_2d)
        # X-axis ticks
        for i in range(0, xend[0], x_tick_interval):
            tick_x, tick_y = gf.point_3d_to_2d(i, 0, 0, self.R_view, self.map_pos)
            tick_label = tick_font.render(str(i), True, tick_color)
            self.axes.blit(tick_label, (tick_x, tick_y))

        # Draw Y-axis
        line = [origin3d, yend]
        _, ypoint_2d = gf.draw_line(self.axes, line, axes_color, 2,
                                    self.R_view, self.map_pos)
        # Y-axis label
        y_label = axes_font.render("Y", True, axes_color)
        self.axes.blit(y_label, ypoint_2d)
        # Y-axis ticks
        for i in range(y_tick_interval, yend[1], y_tick_interval):
            tick_x, tick_y = gf.point_3d_to_2d(0, i, 0, self.R_view, self.map_pos)
            tick_label = tick_font.render(str(i), True, tick_color)
            self.axes.blit(tick_label, (tick_x, tick_y))

        # Draw Z-axis
        line = [origin3d, zend]
        _, zpoint_2d = gf.draw_line(self.axes, line, axes_color, 2,
                                    self.R_view, self.map_pos)
        # Z-axis label
        z_label = axes_font.render("Z", True, axes_color)
        self.axes.blit(z_label, zpoint_2d)
        # Z-axis ticks
        for i in range(z_tick_interval, zend[2] + z_tick_interval, z_tick_interval):
            tick_x, tick_y = gf.point_3d_to_2d(0, 0, i, self.R_view, self.map_pos)
            tick_label = tick_font.render(str(i), True, tick_color)
            self.axes.blit(tick_label, (tick_x, tick_y))

    def _extract_map_features(self):
        """
        Extract features of the map, including red line, blue start line,
        blue end line, green end line.
        # return:
        red_line: binary mask of the red line
        blue_start: xy central coordinates of the bottom right blue circle
        blue_end: xy central coordinates of the top left blue circle
        start_mask: binary mask of the blue start circle
        end_mask: binary mask of the blue end circle
        green_end: xy central coordinates of the green circle for the manipulator
        """
        _, mask_R = extract_color(self.img, 'R')
        _, mask_G = extract_color(self.img, 'G')
        _, mask_B = extract_color(self.img, 'B')

        G_coords = mask2xy(mask_G)
        B_coords = mask2xy(mask_B)

        # Red
        self.red_line = mask_R

        # Blue
        circle1 = B_coords[B_coords[:, 0] < 2000]  # left
        circle2 = B_coords[B_coords[:, 0] > 2000]  # right

        self.blue_end = np.mean(circle1, axis=0)
        self.blue_start = np.mean(circle2, axis=0)

        self.start_mask = mask_B.copy()
        self.start_mask[:2000, :] = False

        self.end_mask = mask_B.copy()
        self.end_mask[2000:, :] = False

        # Green
        self.green_end = np.mean(G_coords, axis=0)

    def update_R(self, R=np.eye(3), reset=False):
        if reset:
            self.R_view = gf.trimetric_view()
        else:
            if self.map_settings['description'] == 'Euler':
                self.R_view = np.matmul(self.R_view, R)
            elif self.map_settings['description'] == 'Fixed':
                self.R_view = np.matmul(R, self.R_view)
            else:
                raise ValueError("Unknown description of orientation")
        self._get_3D_map()
        self._get_axes()

    def draw(self):
        self.screen.blit(self.map3d_surf, self.map_settings['topleft'])
        self.screen.blit(self.axes, self.map_settings['topleft'])
