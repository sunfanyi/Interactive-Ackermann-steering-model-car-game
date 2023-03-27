# -*- coding: utf-8 -*-
# @File    : settings.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import numpy as np
import pygame


class Settings:
    def __init__(self):
        self.bg_color = (255, 255, 255)
        self.screen_width = 800
        self.screen_height = 600

        # axes settings:
        self.xlim = 5224
        self.ylim = 3680
        self.zlim = 500
        self.origin2d = (200, 220)
        self.origin3d = [0, 0, 0]
        self.xend = [self.xlim, 0, 0]  # X-axis range
        self.yend = [0, self.ylim, 0]  # Y-axis range
        self.zend = [0, 0, self.zlim]  # Z-axis range
        self.x_tick_interval = 500  # tick label interval for X-axes
        self.y_tick_interval = 500  # tick label interval for Y-axes
        self.z_tick_interval = 500  # tick label interval for Z-axes

        # zoom in region:
        radius = 100
        self.zoom_region = {'factor': 2,
                            'radius': radius,
                            'centerx': self.screen_width - 10 - radius,
                            'centery': 10 + radius,
                            '3d': False,
                            'car_fixed': True,
                            # '3d': True,
                            # 'car_fixed': False,
                            'edge': True}

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        # Scaling factors for plotting:
        # for x: 800 = screen length, 5000 = image length, 2 = scale factor (reduce to make larger)
        self.x_factor = 800/5000/1.6
        self.y_factor = 600/3600/1.2
        self.z_factor = 0.1

        self.car_speed_factor = 5
        self.speed_during_steering = self.car_speed_factor / 2
        self.car_turning_speed = 0.7/180*np.pi


    # def zoom_in(self):
    #     # self.zoom_factor += 0.001
    #     self.x_factor *= self.zoom_factor
    #     self.y_factor *= self.zoom_factor
    #     self.z_factor = 0.1



