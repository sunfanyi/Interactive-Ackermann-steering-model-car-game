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

        self.car_speed_factor = 15
        self.car_turning_speed = 2/180*np.pi

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
        self.zoom_region = {'factor': 2,
                            'window_width': 300,
                            'window_height': 200,
                            'edge': True}


        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        # Scaling factors for plotting:
        # for x: 800 = screen length, 5000 = image length, 2 = scale factor (reduce to make larger)
        self.x_factor = 800/5000/1.6
        self.y_factor = 600/3600/1.2
        self.z_factor = 0.1


    # def zoom_in(self):
    #     # self.zoom_factor += 0.001
    #     self.x_factor *= self.zoom_factor
    #     self.y_factor *= self.zoom_factor
    #     self.z_factor = 0.1



