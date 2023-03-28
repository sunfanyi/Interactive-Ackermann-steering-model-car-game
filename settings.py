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
        self.main_screen = {
            'bg_color': (255, 255, 255),
            'w': 1200,
            'h': 600,
        }

        # Main screen with 3d map:
        map_screen_width = 800
        map_screen_height = 600
        xlim = 5224
        ylim = 3680
        zlim = 500
        self.map_screen = {
            'topleft': (0, 0),
            'w': map_screen_width,
            'h': map_screen_height,
            'bg_color': (255, 255, 255),
            'xlim': xlim,
            'ylim': ylim,
            'zlim': zlim,
            'origin2d': (200, 220),
            'origin3d': [0, 0, 0],
            'xend': [xlim, 0, 0],  # X-axis range
            'yend': [0, ylim, 0],  # Y-axis range
            'zend': [0, 0, zlim],  # Z-axis range
            'x_tick_interval': 500,  # tick label interval for X-axes
            'y_tick_interval': 500,  # tick label interval for Y-axes
            'z_tick_interval': 500,  # tick label interval for Z-axes

            # Scaling factors for plotting:
            # for x: 800 = screen length, 5000 = image length, 2 = scale factor (reduce to make larger)
            'x_factor': 800 / 5000 / 1.6,
            'y_factor': 600 / 3600 / 1.2,
            'z_factor': 0.1,
        }

        # zoom in region:
        zoom_radius = 100
        self.initial_zoom_in_factor = 2
        self.zoom_region = {
            'topleft': (map_screen_width - 10 - 2 * zoom_radius, 10),
            'w': zoom_radius * 2 + 10,
            'h': zoom_radius * 2 + 10,
            'radius': zoom_radius,
            'factor': self.initial_zoom_in_factor,  # dynamic value
            '3d': False,
            'car_fixed': True,
            # '3d': True,
            # 'car_fixed': False,
            'edge': True
        }

        # Car settings:
        speed = 5
        self.car = {
            'speed': speed,
            'speed_during_steering': speed / 2,
            'turning_speed': 0.7 / 180 * np.pi,
        }

