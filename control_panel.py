# -*- coding: utf-8 -*-
# @File    : control_panel.py
# @Time    : 04/04/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame
import numpy as np
import cv2


class ControlPanel:
    def __init__(self, settings, screen, workspace, car):
        self.settings = settings
        self.screen = screen
        self.workspace = workspace
        self.car = car

        self.process_keyboard_imgs()
        self.img_steer = pygame.image.load(self.settings.steering_wheel['path'])

    def process_keyboard_imgs(self):
        imgs_arrow = [pygame.image.load(
            self.settings.keyboard_panel['arrows_path'][i]) for i in range(4)]
        imgs_arrow_pressed = [pygame.image.load(
            self.settings.keyboard_panel['arrows_pressed_path'][i]) for i in range(4)]
        img_space = pygame.image.load(
            self.settings.keyboard_panel['space_path'])
        img_space_pressed = pygame.image.load(
            self.settings.keyboard_panel['space_pressed_path'])

        w_arrow = self.settings.keyboard_panel['arrows_w']
        h_arrow = self.settings.keyboard_panel['arrows_h']
        w_space = self.settings.keyboard_panel['space_w']
        h_space = self.settings.keyboard_panel['space_h']

        self.imgs_arrow = [pygame.transform.scale(img, (w_arrow, h_arrow))
                           for img in imgs_arrow]
        self.imgs_arrow_pressed = [pygame.transform.scale(img, (w_arrow, h_arrow))
                                   for img in imgs_arrow_pressed]
        self.img_space = pygame.transform.scale(img_space, (w_space, h_space))
        self.img_space_pressed = pygame.transform.scale(img_space_pressed, (w_space, h_space))

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
        window_radius = self.settings.zoom_region['window_radius']
        zoom_factor = self.settings.zoom_region['factor']

        topleft = self.settings.zoom_region['topleft']
        w = window_radius * 2
        h = window_radius * 2

        zoom_map_sur = pygame.Surface((w, h))

        # Cropping settings
        if self.settings.zoom_region['3d']:
            zoom_radius = window_radius / zoom_factor / zoom_factor
            img = self.workspace.map3d.astype(np.uint8)
            car_center = self.car.car_origin2d
            calibration_angle = 90
        else:
            zoom_radius = window_radius / zoom_factor / 0.15
            img = self.workspace.map2d
            car_center = self.car.car_origin3d + self.workspace.pad_size
            car_center[0], car_center[1] = car_center[1], car_center[0]
            calibration_angle = 0

        if self.car.car_origin3d[0] < - zoom_radius or \
                self.car.car_origin3d[0] > self.settings.map_screen['xlim'] + zoom_radius or \
                self.car.car_origin3d[1] < - zoom_radius or \
                self.car.car_origin3d[1] > self.settings.map_screen['ylim'] + zoom_radius:
            # if the car outside the map (white area)
            zoom_map_sur.fill((255, 255, 255))
            pos = topleft
        else:
            # Pre-crop: (Rectangular)
            start_row = np.round(car_center[0] - zoom_radius).astype(np.int32)
            start_col = np.round(car_center[1] - zoom_radius).astype(np.int32)
            end_row = np.round(car_center[0] + zoom_radius).astype(np.int32)
            end_col = np.round(car_center[1] + zoom_radius).astype(np.int32)
            pre_cropped = img[start_row:end_row, start_col:end_col]

            # Resize
            scaled = cv2.resize(pre_cropped, (w, h),
                                interpolation=cv2.INTER_LINEAR)
            # Circular crop
            mask = np.zeros_like(scaled, dtype=np.uint8)
            mask = cv2.circle(mask, (w // 2, h // 2), window_radius, (255, 255, 255), -1)
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
            cropped = cv2.bitwise_and(scaled, scaled, mask=mask)

            # Convert black pixels caused by cropping to white
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            black_pixels = np.where(gray == 0)
            res = cropped.copy()
            res[black_pixels] = [255, 255, 255]

            if not self.settings.zoom_region['3d']:
                res = np.fliplr(res)

            # Fill image to surface
            pygame.surfarray.blit_array(zoom_map_sur, res)
            original_center = zoom_map_sur.get_rect().center

            if self.settings.zoom_region['car_fixed']:
                # Rotate zoomed-in map surface as car steering
                angle = self.car.car_orientation * 180 / np.pi + calibration_angle
                zoom_map_sur = pygame.transform.rotate(zoom_map_sur, angle)
            else:
                zoom_map_sur = pygame.transform.rotate(zoom_map_sur, calibration_angle - 90)

            # rotation will change the surface center as the surface is fixed at top left corner
            sur_w, sur_h = zoom_map_sur.get_size()
            pos = (topleft[0] + original_center[0] - sur_w // 2,
                   topleft[1] + original_center[1] - sur_h // 2)

        self.screen.blit(zoom_map_sur, pos)

        if self.settings.zoom_region['edge']:
            pygame.draw.circle(self.screen, (50, 50, 50), (topleft[0] + window_radius,
                                                           topleft[1] + window_radius),
                               window_radius, 3)

        if self.settings.zoom_region['debug_frame']:
            pygame.draw.line(self.screen, (0, 0, 0), (topleft[0], topleft[1] + window_radius),
                             (topleft[0] + w, topleft[1] + window_radius), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (topleft[0] + window_radius, topleft[1]),
                             (topleft[0] + window_radius, topleft[1] + w), 2)

            font = pygame.font.Font(None, 25)
            pos = (topleft[0] + window_radius, topleft[1] + window_radius)
            X = font.render('x', True, (0, 0, 0))
            text_width, text_height = X.get_size()
            pos = (pos[0] - text_width // 2, pos[1] - text_height // 2)
            self.screen.blit(X, pos)

    def draw(self):
        self.draw_zoomed_map()
        self.draw_steering_wheel()
        car_motion = [self.car.moving_fwd, self.car.moving_bwd,
                      self.car.turning_left, self.car.turning_right]
        for i in range(4):
            if car_motion[i]:
                img = self.imgs_arrow_pressed[i]
                # shift if pressed
                topleft = (self.settings.keyboard_panel['arrows_topleft'][i][0] + 2,
                           self.settings.keyboard_panel['arrows_topleft'][i][1] + 2)
            else:
                img = self.imgs_arrow[i]
                topleft = self.settings.keyboard_panel['arrows_topleft'][i]
            self.screen.blit(img, topleft)

        if self.car.brake:
            img = self.img_space_pressed
            topleft = (self.settings.keyboard_panel['space_topleft'][0] + 2,
                       self.settings.keyboard_panel['space_topleft'][1] + 2)
        else:
            img = self.img_space
            topleft = self.settings.keyboard_panel['space_topleft']
        self.screen.blit(img, topleft)
