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

        # steering wheel
        self.img_steer = pygame.image.load(self.settings.steering_wheel['path'])

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
        self.draw_zoomed_map()
        self.draw_axes()
        self.draw_steering_wheel()

    def draw_steering_wheel(self):
        angle = self.settings.car['steering_ratio'] * self.car.steering_angle * 180 / np.pi
        img_rotated = pygame.transform.rotate(self.img_steer,
                                              -angle)
        img_scaled = pygame.transform.scale(img_rotated,
                                            (self.settings.steering_wheel['w'],
                                             self.settings.steering_wheel['h']))
        self.screen.blit(img_scaled,
                         self.settings.steering_wheel['topleft'])

    def draw_zoomed_map(self):
        if self.settings.zoom_region['3d']:
            zoom_factor = self.settings.zoom_region['factor']
            img = self.map3d.astype(np.uint8)
            car_center = self.car.car_origin2d
            calibration_angle = 90
        else:
            zoom_factor_x = self.settings.zoom_region['factor'] * \
                            self.settings.map_screen['x_factor']
            zoom_factor_y = self.settings.zoom_region['factor'] * \
                            self.settings.map_screen['y_factor']
            img = self.map2d
            car_center = self.car.car_origin3d + self.pad_size
            car_center[0], car_center[1] = car_center[1], car_center[0]
            calibration_angle = 0
        radius = self.settings.zoom_region['zoom_radius']
        topleft = self.settings.zoom_region['topleft']
        print(self.car.car_origin3d)
        # Pre-crop: (Rectangular)
        # crop_size_w = radius / zoom_factor_x
        # crop_size_h = radius / zoom_factor_y
        crop_size_w = radius
        crop_size_h = radius
        start_row = np.round(car_center[0] - crop_size_w).astype(np.int)
        start_col = np.round(car_center[1] - crop_size_h).astype(np.int)
        end_row = np.round(car_center[0] + crop_size_w).astype(np.int)
        end_col = np.round(car_center[1] + crop_size_h).astype(np.int)
        pre_cropped = img[start_row:end_row, start_col:end_col]
        # Resize
        # scaled = cv2.resize(pre_cropped, None, fx=zoom_factor, fy=zoom_factor,
        #                     interpolation=cv2.INTER_CUBIC)

        scaled = cv2.resize(pre_cropped, (self.settings.zoom_region['w'],
                                       self.settings.zoom_region['h']),
                                 interpolation=cv2.INTER_LINEAR)
        # pad to avoid index error caused by floating rounding
        # Define the desired output size
        output_size = (self.settings.zoom_region['w'],
                       self.settings.zoom_region['h'], 3)

        # Pad at the center
        pad_y = max(0, output_size[0] - scaled.shape[0])
        pad_x = max(0, output_size[1] - scaled.shape[1])

        padding = [(pad_y // 2, pad_y - pad_y // 2),
                   (pad_x // 2, pad_x - pad_x // 2),
                   (0, 0)]
        padding = [(round(pad_y / 2), round(pad_y - pad_y / 2)),
                   (round(pad_x / 2), round(pad_x - pad_x / 2)),
                   (0, 0)]
        # Pad the image
        padded = np.pad(scaled, padding, mode='constant', constant_values=0)
        # padded = np.ones((self.settings.zoom_region['w'],
        #                   self.settings.zoom_region['h'], 3)) * 255
        # padded[:scaled.shape[0], :scaled.shape[1], :] = scaled
        # padded = padded.astype(np.uint8)
        padded = scaled
        # Circular crop
        xc = padded.shape[0] // 2
        yc = padded.shape[1] // 2
        mask = np.zeros_like(padded, dtype=np.uint8)
        radius = self.settings.zoom_region['window_radius']
        mask = cv2.circle(mask, (xc, yc), radius, (255, 255, 255), -1)
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        cropped = cv2.bitwise_and(padded, padded, mask=mask)
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        black_pixels = np.where(gray == 0)
        res = cropped.copy()
        res[black_pixels] = [255, 255, 255]
        if not self.settings.zoom_region['3d']:
            res = np.fliplr(res)


        # if self.settings.zoom_region['3d']:
        #     zoom_factor = self.settings.zoom_region['factor']
        #     img = self.map3d.astype(np.uint8)
        #     car_center = self.car.car_origin2d
        #     calibration_angle = 90
        # else:
        #     zoom_factor = self.settings.zoom_region['factor'] / 5
        #     img = self.map2d
        #     car_center = self.car.car_origin3d + self.pad_size
        #     car_center[0], car_center[1] = car_center[1], car_center[0]
        #     calibration_angle = 0
        # radius = self.settings.zoom_region['radius']
        # topleft = self.settings.zoom_region['topleft']
        #
        #
        # # another method
        # xc = int(car_center[0])
        # yc = int(car_center[1])
        #
        # mask = np.zeros_like(img, dtype=np.uint8)
        # mask = cv2.circle(mask, (xc, yc), radius, (255, 255, 255), -1)
        # mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        #
        # cropped = cv2.bitwise_and(img, img, mask=mask)
        #
        # # Extract the region of interest (ROI)
        # roi = cropped[yc - radius: yc + radius, xc - radius: xc + radius]
        #
        # # Resize the ROI to the desired size
        # resized_roi = cv2.resize(roi, (self.settings.zoom_region['w'],
        #                                self.settings.zoom_region['h']),
        #                          interpolation=cv2.INTER_CUBIC)
        #
        # # Replace black pixels with white pixels
        # gray = cv2.cvtColor(resized_roi, cv2.COLOR_BGR2GRAY)
        # black_pixels = np.where(gray == 0)
        # res = resized_roi.copy()
        # res[black_pixels] = [255, 255, 255]
        #
        # if not self.settings.zoom_region['3d']:
        #     res = np.fliplr(res)
        # print(res.shape)

        # Create surface
        zoom_map_sur = pygame.Surface((self.settings.zoom_region['w'],
                                       self.settings.zoom_region['h']))
        # pygame.surfarray.blit_array(zoom_map_sur, scaled)
        pygame.surfarray.blit_array(zoom_map_sur, res)
        original_center = zoom_map_sur.get_rect().center

        if self.settings.zoom_region['edge']:
            pygame.draw.circle(zoom_map_sur, (50, 50, 50), (xc, yc), radius, 3)

        if self.settings.zoom_region['car_fixed']:
            # Rotate zoomed-in map surface as car steering
            aligned_surface = pygame.transform.rotate(zoom_map_sur,
                              self.car.car_orientation*180/np.pi + calibration_angle)
        else:
            if self.settings.zoom_region['3d']:
                aligned_surface = pygame.transform.rotate(zoom_map_sur, calibration_angle)
            else:
                aligned_surface = pygame.transform.rotate(zoom_map_sur, -90)
            # aligned_surface = zoom_map_sur

        rotated_center = aligned_surface.get_rect().center
        rotated_topleft = aligned_surface.get_rect().topleft

        # rotation will change the surface center as the surface is fixed at top left corner
        sur_w, sur_h = aligned_surface.get_size()
        pos = (topleft[0] + original_center[0] - sur_w // 2,
               topleft[1] + original_center[1] - sur_h // 2)
        # screen1.blit(X, pos)
        # original_center
        # aligned_topleft = (topleft[0] - (rotated_center[0] - original_center[0]),
        #                    topleft[1] - (rotated_center[1] - original_center[1]))

        # self.screen.blit(aligned_surface, aligned_topleft)
        self.screen.blit(aligned_surface, pos)

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





