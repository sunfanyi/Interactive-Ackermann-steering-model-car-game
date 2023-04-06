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
    def __init__(self, settings, screen, game_stats, workspace, car):
        self.settings = settings
        self.screen = screen
        self.game_stats = game_stats
        self.workspace = workspace
        self.car = car
        
        self.key_settings = settings.keyboard_panel
        self.zoom_settings = settings.zoom_region

        self.process_keyboard_imgs()
        self.img_steer = pygame.image.load(self.settings.steering_wheel['path'])

        self.draw_frame()

    def process_keyboard_imgs(self):
        imgs_arrow = [pygame.image.load(
            self.key_settings['arrows_path'][i]) for i in range(4)]
        imgs_arrow_pressed = [pygame.image.load(
            self.key_settings['arrows_pressed_path'][i]) for i in range(4)]
        img_space = pygame.image.load(
            self.key_settings['space_path'])
        img_space_pressed = pygame.image.load(
            self.key_settings['space_pressed_path'])

        w_arrow = self.key_settings['arrows_w']
        h_arrow = self.key_settings['arrows_h']
        w_space = self.key_settings['space_w']
        h_space = self.key_settings['space_h']

        self.imgs_arrow = [pygame.transform.scale(img, (w_arrow, h_arrow))
                           for img in imgs_arrow]
        self.imgs_arrow_pressed = [pygame.transform.scale(img, (w_arrow, h_arrow))
                                   for img in imgs_arrow_pressed]
        self.img_space = pygame.transform.scale(img_space, (w_space, h_space))
        self.img_space_pressed = pygame.transform.scale(img_space_pressed, (w_space, h_space))

    def draw_frame(self):
        r = self.zoom_settings['window_radius']
        self.frame = pygame.Surface((2*r, 2*r), pygame.SRCALPHA)

        if self.zoom_settings['edge']:
            pygame.draw.circle(self.frame, (50, 50, 50), (r, r),
                               r, 3)

        if self.zoom_settings['debug_frame']:
            pygame.draw.line(self.frame, (0, 0, 0), (0, r),
                             (2*r, r), 2)
            pygame.draw.line(self.frame, (0, 0, 0), (r, 0),
                             (r, 2*r), 2)

            # font = pygame.font.Font(None, 25)
            # pos = (r, r)
            # X = font.render('x', True, (0, 0, 0))
            # text_width, text_height = X.get_size()
            # pos = (pos[0] - text_width // 2, pos[1] - text_height // 2)
            # self.frame.blit(X, pos)

    def update_steering_wheel(self):
        angle = self.settings.car['steering_ratio'] * self.car.steering_angle * 180 / np.pi
        img_rotated = pygame.transform.rotate(self.img_steer,
                                              -angle)
        img_scaled = pygame.transform.scale(img_rotated,
                                            (self.settings.steering_wheel['w'],
                                             self.settings.steering_wheel['h']))
        self.steering_wheel_sur = img_scaled

    def update_zoomed_map(self):
        r = self.zoom_settings['window_radius']
        w = r * 2
        h = r * 2
        topleft = self.zoom_settings['topleft']
        zoom_factor = self.zoom_settings['factor']

        zoom_map_sur = pygame.Surface((w, h))

        # Cropping settings
        if self.zoom_settings['3d']:
            zoom_radius = r / zoom_factor / zoom_factor
            img = self.workspace.map3d.astype(np.uint8)
            car_center = self.car.car_origin2d
            calibration_angle = 90
        else:
            zoom_radius = r / zoom_factor / 0.15
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
            mask = cv2.circle(mask, (w // 2, h // 2), r, (255, 255, 255), -1)
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
            cropped = cv2.bitwise_and(scaled, scaled, mask=mask)

            # Convert black pixels caused by cropping to white
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            black_pixels = np.where(gray == 0)
            res = cropped.copy()
            res[black_pixels] = [255, 255, 255]

            if not self.zoom_settings['3d']:
                res = np.fliplr(res)

            # Fill image to surface
            pygame.surfarray.blit_array(zoom_map_sur, res)

            if self.zoom_settings['car_fixed']:
                # Rotate zoomed-in map surface as car steering
                angle = self.car.car_orientation * 180 / np.pi + calibration_angle
                zoom_map_sur = pygame.transform.rotate(zoom_map_sur, angle)
            else:
                zoom_map_sur = pygame.transform.rotate(zoom_map_sur, calibration_angle - 90)

        # rotation will change the surface center if the surface is aligned at top left corner
        self.zoom_map_rect = zoom_map_sur.get_rect()
        self.zoom_map_rect.center = (topleft[0] + r,
                                     topleft[1] + r)
        self.zoom_map_sur = zoom_map_sur

    def update(self):
        self.update_zoomed_map()
        if not self.game_stats.car_freeze:
            self.update_steering_wheel()

    def draw(self):
        self.screen.blit(self.steering_wheel_sur,
                         self.settings.steering_wheel['topleft'])

        self.screen.blit(self.zoom_map_sur, self.zoom_map_rect)
        self.screen.blit(self.frame, self.zoom_settings['topleft'])

        self.draw_keyboard_panel()

    def draw_keyboard_panel(self):
        car_motion = [self.car.moving_fwd, self.car.moving_bwd,
                      self.car.turning_right, self.car.turning_left]
        for i in range(4):
            if car_motion[i]:
                img = self.imgs_arrow_pressed[i]
                # shift if pressed
                topleft = (self.key_settings['arrows_topleft'][i][0] + 2,
                           self.key_settings['arrows_topleft'][i][1] + 2)
            else:
                img = self.imgs_arrow[i]
                topleft = self.key_settings['arrows_topleft'][i]
            self.screen.blit(img, topleft)

        if self.car.brake:
            img = self.img_space_pressed
            topleft = (self.key_settings['space_topleft'][0] + 2,
                       self.key_settings['space_topleft'][1] + 2)
        else:
            img = self.img_space
            topleft = self.key_settings['space_topleft']
        self.screen.blit(img, topleft)
