# -*- coding: utf-8 -*-
# @File    : settings.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import numpy as np


def center2global(button, screen):
    """
    Convert the position of a button from subscreen to the main screen.
    This is done because the input screen of a button should always be the main
    for MouseClick event, but the button positions are defined in the subscreens.
    """
    x = button['center'][0] + screen['topleft'][0]
    y = button['center'][1] + screen['topleft'][1]
    button['center'] = (x, y)


class Settings:
    main_screen = {
        'bg_color': (255, 255, 255),
        'w': 1250,
        'h': 600,
    }
    # ======================================== Screen 1 ======================================== #
    screen1 = {
        'topleft': (0, 0),
        'w': 850,
        'h': 600,
        'bg_color': (255, 255, 255),
    }

    # Main 3d map
    xlim = 5224
    ylim = 3680
    zlim = 500
    map_screen = {
        'topleft': np.array([0, 170]),
        'w': 850,
        'h': 400,
        'path': 'Figures/CWMap.jpg',
        'xlim': xlim,
        'ylim': ylim,
        'zlim': zlim,
        'origin3d': [0, 0, 0],
        'xend': [xlim, 0, 0],  # X-axis range
        'yend': [0, ylim, 0],  # Y-axis range
        'zend': [0, 0, zlim],  # Z-axis range
        'x_tick_interval': 500,  # tick label interval for X-axes
        'y_tick_interval': 500,  # tick label interval for Y-axes
        'z_tick_interval': 500,  # tick label interval for Z-axes

        'scale_factor': 0.135,  # Scaling factors for plotting:

        'description': 'Euler',  # 'Euler' or 'Fixed' angle rotation
        # 'description': 'Fixed',
    }

    message_box = {
        'w': 500,
        'h': 200,
        'topleft': (140, 10),
        'text_color': (0, 0, 0),
        'font_size': 35,
        'bg_color': (255, 255, 255),
    }

    # ======================================== Screen 2 ======================================== #
    screen2 = {
        'topleft': (850, 0),
        'w': 450,
        'h': 600,
        'bg_color': (255, 255, 255),
    }

    # latex region
    latex_region = {
        'topleft': (0, 0),
        'w': 400,
        'h': 200,
        'bg_color': (255, 255, 255),
    }

    # zoom in region
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

    # steering wheel region
    steering_wheel = {
        'topleft': (265, 260),
        'w': 100,
        'h': 100,
        'path': 'Figures/steering_wheel.png',
    }

    # Keyboard panel
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
        'arrows_topleft': [(275, y_aligned - 60), (275, y_aligned),
                           (215, y_aligned), (335, y_aligned)],
        'arrows_path': ['Figures/keyup.png', 'Figures/keydown.png',
                        'Figures/keyleft.png', 'Figures/keyright.png'],
        'arrows_pressed_path': ['Figures/keyup_pressed.png', 'Figures/keydown_pressed.png',
                                'Figures/keyleft_pressed.png', 'Figures/keyright_pressed.png'],
    }

    # ======================================== Image Buttons ======================================== #
    # axes rotation panel
    view_w = 50
    view_dx = 10
    view_dy = 5
    view_topleft = (650, 70)  # center of the topleft icon
    paths = ['Figures/x_anticlockwise.png',
             'Figures/x_clockwise.png',
             'Figures/y_anticlockwise.png',
             'Figures/y_clockwise.png',
             'Figures/z_anticlockwise.png',
             'Figures/z_clockwise.png']
    centers = [(view_topleft[0], view_topleft[1]),
               (view_topleft[0], view_topleft[1] + view_w + view_dy),
               (view_topleft[0] + view_w + view_dx, view_topleft[1]),
               (view_topleft[0] + view_w + view_dx, view_topleft[1] + view_w + view_dy),
               (view_topleft[0] + 2 * (view_w + view_dx), view_topleft[1]),
               (view_topleft[0] + 2 * (view_w + view_dx), view_topleft[1] + view_w + view_dy)]
    buts_rot_axes = []
    for i in range(6):
        buts_rot_axes.append({
            'path': paths[i],
            'center': centers[i],
            'w': view_w,
            'h': view_w,
            'bg_color': (150, 150, 150, 20)
        })
        center2global(buts_rot_axes[i], screen1)

    # switch between game and developer mode
    paths = ['Figures/switch_enable.png', 'Figures/switch_disable.png']
    buts_switch = []
    for i in range(2):
        buts_switch.append({
            'path': paths[i],
            'center': (100, 140),
            'w': 70,
            'h': 70,
        })
        center2global(buts_switch[i], screen1)

    # ======================================== Text Buttons ======================================== #
    # restart button
    but_restart = {
        'msg': 'Restart',
        'center': (100, 50),
        'w': 100,
        'h': 40,
        'bg_color': (0, 255, 0),
    }
    center2global(but_restart, screen1)

    # trimetric view reset button
    but_trimetric = {
        'msg': 'Trimetric Reset',
        'center': (view_topleft[0] + view_w + view_dx,
                   view_topleft[1] + 2 * view_w + view_dy),
        'w': 3 * view_w + 2 * view_dx - 10,
        'h': view_w - 15,
    }
    center2global(but_trimetric, screen1)

    # zoom buttons
    w = 25
    h = 25
    but_zoom_in = {
        'msg': '+',
        'center': (zoom_region['topleft'][0] + 0.3 * zoom_region['window_radius'],
                   zoom_region['topleft'][1] + 2.2 * zoom_region['window_radius']),
        'w': w,
        'h': h,
    }
    but_zoom_out = {
        'msg': '-',
        'center': (zoom_region['topleft'][0] + zoom_region['window_radius'],
                   zoom_region['topleft'][1] + 2.2 * zoom_region['window_radius']),
        'w': w,
        'h': h,
    }
    but_zoom_reset = {
        'msg': 'R',
        'center': (zoom_region['topleft'][0] + 1.7 * zoom_region['window_radius'],
                   zoom_region['topleft'][1] + 2.2 * zoom_region['window_radius']),
        'w': w,
        'h': h,
    }
    center2global(but_zoom_in, screen2)
    center2global(but_zoom_out, screen2)
    center2global(but_zoom_reset, screen2)

    # ======================================== Others ======================================== #
    # Car settings
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
