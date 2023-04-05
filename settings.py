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
        'w': 1250,
        'h': 600,
    }

    # Screen 1
    screen1 = {
        'topleft': (0, 0),
        'w': 850,
        'h': 600,
        'bg_color': (255, 255, 255),
    }

    # Main 3d map (screen 1)
    xlim = 5224
    ylim = 3680
    zlim = 500
    map_screen = {
        'topleft': (0, 0),
        'w': 850,
        'h': 600,
        'path': 'Figures/CWMap.jpg',
        'xlim': xlim,
        'ylim': ylim,
        'zlim': zlim,
        'origin2d': (150, 230),
        'origin3d': [0, 0, 0],
        'xend': [xlim, 0, 0],  # X-axis range
        'yend': [0, ylim, 0],  # Y-axis range
        'zend': [0, 0, zlim],  # Z-axis range
        'x_tick_interval': 500,  # tick label interval for X-axes
        'y_tick_interval': 500,  # tick label interval for Y-axes
        'z_tick_interval': 500,  # tick label interval for Z-axes

        # Scaling factors for plotting:
        'scale_factor': 0.135,
    }

    # Screen 2
    screen2 = {
        'topleft': (850, 0),
        'w': 450,
        'h': 600,
        'bg_color': (255, 255, 255),
    }

    # latex region (screen 2)
    latex_region = {
        'topleft': (0, 0),
        'w': 400,
        'h': 200,
        'bg_color': (255, 255, 255),
    }

    # zoom in region (screen 2)
    initial_zoom_in_factor = 2
    zoom_region = {
        'topleft': (10, 220),
        'window_radius': 100,
        'factor': initial_zoom_in_factor,  # dynamic value
        '3d': False,
        'car_fixed': True,
        # '3d': True,
        # 'car_fixed': False,
        'edge': True,
        'debug_frame': True
    }

    # steering wheel region (screen 2)
    steering_wheel = {
        'topleft': (265, 260),
        'w': 100,
        'h': 100,
        'path': 'Figures/steering_wheel.png',
    }

    # Keyboard panel (screen 2)
    y_aligned = 505
    keyboard_panel = {
        'space_topleft': (30, y_aligned),
        'space_w': 150,
        'space_h': 50,
        'space_path': 'Figures/keyspace.png',
        'space_pressed_path': 'Figures/keyspace_pressed.png',

        'arrows_w': 50,
        'arrows_h': 50,
        # lists for up, down, left, right:
        'arrows_topleft': [(275, y_aligned-60), (275, y_aligned),
                           (215, y_aligned), (335, y_aligned)],
        'arrows_path': ['Figures/keyup.png', 'Figures/keydown.png',
                        'Figures/keyleft.png', 'Figures/keyright.png'],
        'arrows_pressed_path': ['Figures/keyup_pressed.png', 'Figures/keydown_pressed.png',
                                'Figures/keyleft_pressed.png', 'Figures/keyright_pressed.png'],
    }

    # Car settings:
    # acceleration = 0.08
    acceleration = 0.2
    car = {
        'acc': acceleration,  # acceleration (m/s2)
        'steering_speed': 0.4 / 180 * np.pi,  # phi (rad/s), for steering wheel, not theta
        'max_steer': 45 / 180 * np.pi,  # rad
        # 'max_speed': 20,  # m/s
        'max_speed': 50,  # m/s
        'steering_ratio': 10,  # between steering wheel and wheels
    }
