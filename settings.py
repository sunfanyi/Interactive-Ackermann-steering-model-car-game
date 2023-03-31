# -*- coding: utf-8 -*-
# @File    : settings.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import numpy as np


class Settings:
    main_screen = {
        'bg_color': (255, 255, 255),
        'w': 1200,
        'h': 600,
    }

    # Main 3d map:
    map_screen_width = 1200
    map_screen_height = 600
    xlim = 5224
    ylim = 3680
    zlim = 500
    map_screen = {
        'topleft': (0, 0),
        'w': map_screen_width,
        'h': map_screen_height,
        'bg_color': (255, 255, 255),
        'path': 'Figures/CWMap.jpg',
        'xlim': xlim,
        'ylim': ylim,
        'zlim': zlim,
        'origin2d': (160, 220),
        'origin3d': [0, 0, 0],
        'xend': [xlim, 0, 0],  # X-axis range
        'yend': [0, ylim, 0],  # Y-axis range
        'zend': [0, 0, zlim],  # Z-axis range
        'x_tick_interval': 500,  # tick label interval for X-axes
        'y_tick_interval': 500,  # tick label interval for Y-axes
        'z_tick_interval': 500,  # tick label interval for Z-axes

        # Scaling factors for plotting:
        'scale_factor': 0.14,
    }

    # zoom in region:
    initial_zoom_in_factor = 2
    zoom_region = {
        'topleft': (600, 0),
        'window_radius': 100,
        'factor': initial_zoom_in_factor,  # dynamic value
        '3d': False,
        'car_fixed': True,
        # '3d': True,
        # 'car_fixed': False,
        'edge': True,
        'debug_frame': True
    }

    # steering wheel region:
    steering_wheel = {
        'topleft': (450, 40),
        'w': 100,
        'h': 100,
        'bg_color': (255, 255, 255),
        'path': 'Figures/steering_wheel.png',
    }

    # latex region
    latex_region = {
        'topleft': (850, 0),
        'w': 400,
        'h': 250,
        'bg_color': (255, 255, 255),
    }

    # Car settings:
    # acceleration = 0.08
    acceleration = 0.2
    car = {
        'acc': acceleration,   # acceleration (m/s2)
        'steering_speed': 0.4 / 180 * np.pi,  # phi (rad/s), for steering wheel, not theta
        'max_steer': 45 / 180 * np.pi,  # rad
        # 'max_speed': 20,  # m/s
        'max_speed': 50,  # m/s
        'steering_ratio': 10,  # between steering wheel and wheels
    }