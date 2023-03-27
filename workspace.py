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
        self.map3d = warped.copy()
        self.map3d[black_pixels] = [255, 255, 255]

        self.pad_size = 10000
        img = img.astype(np.uint8)
        # pad edges with zero for cropping
        pad = np.full((img.shape[0] + 2 * self.pad_size,
                       img.shape[1] + 2 * self.pad_size, 3), 255, dtype=np.uint8)
        pad[self.pad_size:self.pad_size + img.shape[0],
            self.pad_size:self.pad_size + img.shape[1]] = img
        self.map2d = pad
        # self.map2d = gf.cv2_to_pygame(pad)

    def draw(self):
        self.draw_map()
        self.draw_axes()

    def draw_map(self):
        merged_surface = pygame.Surface((self.settings.screen_width,
                                         self.settings.screen_height), pygame.SRCALPHA)

        map_surface = pygame.surfarray.make_surface(self.map3d)
        merged_surface.blit(map_surface, (0, 0))

        # For the zoomed in map:
        if self.settings.zoom_region['3d']:
            zoom_factor = self.settings.zoom_region['factor']
            img = self.map3d.astype(np.uint8)
            car_center = self.car.car_origin2d
            calibration_angle = 90
        else:
            zoom_factor = self.settings.zoom_region['factor'] / 5
            img = self.map2d
            car_center = self.car.car_origin3d + self.pad_size
            car_center[0], car_center[1] = car_center[1], car_center[0]
            calibration_angle = 0

        radius = self.settings.zoom_region['radius']
        centerx = self.settings.zoom_region['centerx']
        centery = self.settings.zoom_region['centery']
        window_w = radius * 2 + 2
        window_h = radius * 2 + 2

        # Pre-crop: (Rectangular)
        crop_size_w = radius / zoom_factor
        crop_size_h = radius / zoom_factor
        topleft = (centerx - radius, centery - radius)

        start_row = int(car_center[0] - crop_size_w)
        start_col = int(car_center[1] - crop_size_h)
        end_row = int(car_center[0] + crop_size_w)
        end_col = int(car_center[1] + crop_size_h)
        pre_cropped = img[start_row:end_row, start_col:end_col]

        # Resize
        scaled = cv2.resize(pre_cropped, None, fx=zoom_factor, fy=zoom_factor,
                            interpolation=cv2.INTER_CUBIC)

        # pad to avoid index error caused by floating rounding
        padded = np.ones((window_w, window_h, 3)) * 255
        padded[:scaled.shape[0], :scaled.shape[1], :] = scaled

        padded = padded.astype(np.uint8)

        # Circular crop
        xc = padded.shape[0] // 2
        yc = padded.shape[1] // 2
        mask = np.zeros_like(padded, dtype=np.uint8)
        mask = cv2.circle(mask, (xc, yc), radius, (255, 255, 255), -1)

        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        cropped = cv2.bitwise_and(padded, padded, mask=mask)

        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        black_pixels = np.where(gray == 0)
        res = cropped.copy()
        res[black_pixels] = [255, 255, 255]

        if not self.settings.zoom_region['3d']:
            res = np.fliplr(res)

        # Create surface
        zoomed_map_surface = pygame.Surface((window_w, window_h))
        pygame.surfarray.blit_array(zoomed_map_surface, res)
        original_center = zoomed_map_surface.get_rect().center

        if self.settings.zoom_region['edge']:
            pygame.draw.circle(zoomed_map_surface, (50, 50, 50), (xc, yc), radius, 3)

        # Rotate zoomed-in map surface as car steering

        if self.settings.zoom_region['car_fixed']:
            aligned_surface = pygame.transform.rotate(zoomed_map_surface,
                                          self.car.car_orientation*180/np.pi + calibration_angle)
        else:
            aligned_surface = zoomed_map_surface

        rotated_center = aligned_surface.get_rect().center
        # rotation will change the surface center as the surface is fixed at top left corner
        aligned_topleft = (topleft[0] - (rotated_center[0] - original_center[0]),
                           topleft[1] - (rotated_center[1] - original_center[1]))

        merged_surface.blit(aligned_surface, aligned_topleft)

        self.screen.blit(merged_surface, (0, 0))

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





