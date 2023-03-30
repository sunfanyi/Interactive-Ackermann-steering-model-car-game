# -*- coding: utf-8 -*-
# @File    : settings.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import numpy as np


class Settings:
    def __init__(self):
        self.main_screen = {
            'bg_color': (255, 255, 255),
            'w': 1200,
            'h': 600,
        }

        # Main 3d map:
        map_screen_width = 800
        map_screen_width = 1000
        map_screen_height = 600
        xlim = 5224
        ylim = 3680
        zlim = 500
        self.map_screen = {
            'topleft': (0, 0),
            'w': map_screen_width,
            'h': map_screen_height,
            'bg_color': (255, 255, 255),
            'path': 'Figures/CWMap.jpg',
            'xlim': xlim,
            'ylim': ylim,
            'zlim': zlim,
            # 'origin2d': (180, 200),
            'origin2d': (180, 220),
            'origin3d': [0, 0, 0],
            'xend': [xlim, 0, 0],  # X-axis range
            'yend': [0, ylim, 0],  # Y-axis range
            'zend': [0, 0, zlim],  # Z-axis range
            'x_tick_interval': 500,  # tick label interval for X-axes
            'y_tick_interval': 500,  # tick label interval for Y-axes
            'z_tick_interval': 500,  # tick label interval for Z-axes

            # Scaling factors for plotting:
            # for x: 800 = screen length, 5000 = image length, 1.6 = scale factor (reduce to make larger)
            # 'x_factor': 800 / 5224 / 1.4,
            # 'y_factor': 600 / 3680 / 1.4,
            'x_factor': 0.1,
            'y_factor': 0.1,
            'z_factor': 0.1,
        }

        # zoom in region:
        zoom_radius = 200
        self.initial_zoom_in_factor = 2
        self.zoom_region = {
            # 'topleft': (map_screen_width - 10 - 2 * zoom_radius, 0),
            'topleft': (600, 0),
            'w': 200,
            'h': 200,
            'zoom_radius': zoom_radius,
            'window_radius': 100,
            'factor': self.initial_zoom_in_factor,  # dynamic value
            '3d': False,
            # 'car_fixed': True,
            # '3d': True,
            'car_fixed': False,
            'edge': True
        }

        # steering wheel region:
        self.steering_wheel = {
            # 'topleft': (1000, 300),
            'topleft': (450, 40),
            'w': 100,
            'h': 100,
            'bg_color': (255, 255, 255),
            'path': 'Figures/steering_wheel.png',
        }

        # latex region
        self.latex_region = {
            'topleft': (850, 0),
            'w': 400,
            'h': 250,
            'bg_color': (255, 255, 255),
        }

        # Car settings:
        acceleration = 0.08
        self.car = {
            'acc': acceleration,   # acceleration (m/s2)
            'steering_speed': 0.4 / 180 * np.pi,  # phi (rad/s), for steering wheel, not theta
            'max_steer': 45 / 180 * np.pi,  # rad
            'max_speed': 20,  # m/s
            'steering_ratio': 10,  # between steering wheel and wheels
        }