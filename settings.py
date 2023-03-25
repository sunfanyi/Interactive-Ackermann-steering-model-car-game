# -*- coding: utf-8 -*-
# @File    : settings.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm


import pygame


class Settings:
    def __init__(self):
        self.bg_color = (255, 255, 255)
        self.screen_width = 800
        self.screen_height = 600

        self.origin = (250, 200)
        self.car_speed_factor = 10

        # Scaling factors for plotting:
        # for x: 800 = screen length, 5000 = image length, 2 = scale factor (reduce to make larger)
        self.x_factor = 800/5000/2
        self.y_factor = 600/3600/1.5
        self.z_factor = 0.1

        # axes settings:
        self.origin2d = (250, 200)
        self.origin3d = [0, 0, 0]
        self.xaxis = [5224, 0, 0]  # X-axis range
        self.yaxis = [0, 3680, 0]  # Y-axis range
        self.zaxis = [0, 0, 500]  # Z-axis range
        self.x_tick_interval = 500  # tick label interval for X-axes
        self.y_tick_interval = 500  # tick label interval for Y-axes
        self.z_tick_interval = 500  # tick label interval for Z-axes
