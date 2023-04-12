# -*- coding: utf-8 -*-
# @File    : game_function.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import sys
import numpy as np
import pygame
import time

from settings import Settings

my_settings = Settings()

scale_factor = my_settings.map_screen['scale_factor']


def check_event(settings, game_stats, workspace, car, large_car,
                zoom_buttons, restart_button, trimetric_button,
                axes_buttons, switch_buttons):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_event(event, game_stats, workspace, car, large_car)
        elif event.type == pygame.KEYUP:
            check_keyup_event(event, car, large_car)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            check_mouse_click_event(settings, game_stats, workspace, car, large_car,
                                    zoom_buttons, restart_button, trimetric_button,
                                    axes_buttons, switch_buttons, mouse)


def check_mouse_click_event(settings, game_stats, workspace, car, large_car,
                            zoom_buttons, restart_button, trimetric_button,
                            axes_buttons, switch_buttons,
                            mouse):
    # zoom in
    if zoom_buttons[0].rect.collidepoint(mouse):
        settings.zoom_region['factor'] *= 1.1
        large_car.scale *= 1.1
        large_car.reset_dimensions()

    # zoom out
    if zoom_buttons[1].rect.collidepoint(mouse):
        settings.zoom_region['factor'] /= 1.1
        large_car.scale /= 1.1
        large_car.reset_dimensions()

    # zoom reset
    if zoom_buttons[2].rect.collidepoint(mouse):
        settings.zoom_region['factor'] = settings.initial_zoom_in_factor
        large_car.scale = settings.zoom_region['factor'] * 40
        large_car.reset_dimensions()

    # restart
    if restart_button.rect.collidepoint(mouse):
        restart_event(car, large_car, game_stats)

    # reset trimetric view
    if trimetric_button.rect.collidepoint(mouse):
        workspace.update_R(reset=True)

    # rotate view
    for i in range(6):
        if axes_buttons[i].rect.collidepoint(mouse):
            axis = ['x', 'y', 'z'][i // 2]
            rotation_angle = 0.1 if i % 2 == 0 else -0.1
            R = rotation(rotation_angle, axis)
            workspace.update_R(R)

    # switch between game and developer mode
    if switch_buttons[0].rect.collidepoint(mouse):
        game_stats.game_active = not game_stats.game_active
        restart_event(car, large_car, game_stats)


def check_keydown_event(event, game_stats, workspace, car, large_car):
    check_car_moving(event, game_stats, car, large_car)


def restart_event(car, large_car, game_stats):
    car.reset_positions()
    car.reset_motion()
    large_car.reset_zoomed_map()
    game_stats.car_freeze = False


def check_car_moving(event, game_stats, car, large_car):
    """
    Note Y-axis is flipped, so left key actually represents turning right
    car.turning_left and car.turning_right actually represent turning in the
    original coordinate system (following right-hand rule) before flipping.
    In the flipped coordinate system, they are opposite.
    """
    if event.key == pygame.K_UP:  # move forward
        car.moving_fwd = True
        large_car.moving_fwd = True
        if game_stats.car_freeze:
            car.step_back()
        game_stats.car_freeze = False
        # car.step_back()
    elif event.key == pygame.K_DOWN:  # move backward
        car.moving_bwd = True
        large_car.moving_bwd = True
        if game_stats.car_freeze:
            car.step_back()
        game_stats.car_freeze = False
        # car.step_back()
    elif event.key == pygame.K_RIGHT:  # turn left
        car.turning_left = True
        large_car.turning_left = True
    elif event.key == pygame.K_LEFT:  # turn right
        car.turning_right = True
        large_car.turning_right = True
    elif event.key == pygame.K_SPACE:  # brake
        car.brake = True
        large_car.brake = True
        if game_stats.car_freeze:
            car.step_back()
        game_stats.car_freeze = False
        # car.step_back()


def check_keyup_event(event, car, large_car):
    if event.key == pygame.K_UP:
        car.moving_fwd = False
        large_car.moving_fwd = False
    elif event.key == pygame.K_DOWN:
        car.moving_bwd = False
        large_car.moving_bwd = False
    elif event.key == pygame.K_RIGHT:
        car.turning_left = False
        large_car.turning_left = False
    elif event.key == pygame.K_LEFT:
        car.turning_right = False
        large_car.turning_right = False
    elif event.key == pygame.K_SPACE:
        car.brake = False
        large_car.brake = False


def detect_collision(game_stats, screen, car, large_car, red_line):
    if car.car_origin3d[0] < 1000 or car.car_origin3d[0] > 4000 or \
            car.car_origin3d[1] < 500 or car.car_origin3d[1] > 2500:
        return

    # get 3d corner points
    # FL = np.round(car.body_lines[0][0][:2]).astype(np.int32)  # FL
    # FR = np.round(car.body_lines[1][0][:2]).astype(np.int32)  # FR
    # RL = np.round(car.body_lines[3][0][:2]).astype(np.int32)  # RL
    # RR = np.round(car.body_lines[2][0][:2]).astype(np.int32)  # RR
    FL = car.body_lines[0][0][:2]
    FR = car.body_lines[1][0][:2]
    RL = car.body_lines[3][0][:2]
    RR = car.body_lines[2][0][:2]

    def _get_line(corner1, corner2):
        line = [np.linspace(corner1[0], corner2[0], 10),
                np.linspace(corner1[1], corner2[1], 10)]

        return np.round(line).astype(np.int32)

    edges = np.concatenate([_get_line(FL, FR),
                            _get_line(FR, RR),
                            _get_line(RR, RL),
                            _get_line(RL, FL)], axis=1).T

    pos2d = point_3d_to_2d(game_stats.collision_point[0], game_stats.collision_point[1], 0,
                           R=car.R_view, offset=car.offset)
    font = pygame.font.Font(None, 38)
    X = font.render('x', True, (0, 0, 0))
    text_width, text_height = X.get_size()
    topleft = (pos2d[0] - text_width // 2,
               pos2d[1] - text_height // 2)
    if game_stats.car_freeze:
        # if collision
        screen.blit(X, topleft)

    if np.any(red_line[edges[:, 1], edges[:, 0]]):
        collision_point = edges[np.argwhere(red_line[edges[:, 1], edges[:, 0]])][0][0]
        # print('collision detected: ' + str(collision_point))
        game_stats.collision_point = collision_point

        if game_stats.game_active:
            game_stats.car_freeze = True
            car.reset_motion()
            large_car.moving_fwd = False  # suppress wheel spinning
        else:  # short blit
            screen.blit(X, topleft)


def draw_switch(screen, switch_buttons, game_stats):
    if game_stats.game_active:  # developer mode disabled
        switch_buttons[1].draw_button()
    else:  # developer mode enabled
        switch_buttons[0].draw_button()
    font = pygame.font.Font(None, 25)
    text = font.render('Developer Mode', True, (0, 0, 0))
    text_width, text_height = text.get_size()
    pos = switch_buttons[0].center
    pos = (pos[0] - text_width // 2,
           pos[1] - text_height // 2 - 25)
    screen.blit(text, pos)


def update_screen(settings, game_stats, screen1, screen2,
                  workspace, car, large_car, zoom_buttons, restart_button,
                  trimetric_button, axes_buttons, switch_buttons,
                  latex_window, control_panel):
    screen1.fill(settings.screen1['bg_color'])
    screen2.fill(settings.screen2['bg_color'])

    # screen 1
    workspace.draw()
    car.draw()

    # screen 2
    control_panel.draw()
    large_car.draw()
    latex_window.draw()

    # buttons
    for button in zoom_buttons:
        button.draw_button()
    for button in axes_buttons:
        button.draw_button()
    draw_switch(screen1, switch_buttons, game_stats)
    restart_button.draw_button()
    trimetric_button.draw_button()

    detect_collision(game_stats, screen1, car, large_car,
                     workspace.red_line)


def rotation(theta, direction):
    if direction == 'x':
        R = np.array([[1, 0, 0],
                      [0, np.cos(theta), -np.sin(theta)],
                      [0, np.sin(theta), np.cos(theta)]])
    elif direction == 'y':
        R = np.array([[np.cos(theta), 0, np.sin(theta)],
                      [0, 1, 0],
                      [-np.sin(theta), 0, np.cos(theta)]])
    elif direction == 'z':
        R = np.array([[np.cos(theta), -np.sin(theta), 0],
                      [np.sin(theta), np.cos(theta), 0],
                      [0, 0, 1]])
    else:
        raise ValueError('Direction should be x, y or z')
    return R


def add_translation(R, t=np.array([0, 0, 0, 1])):
    if len(t) == 3:
        t = np.hstack([t, 1])
    T = np.vstack([R, np.array([[0, 0, 0]])])
    T = np.hstack([T, t.reshape(-1, 1)])
    return T


def trimetric_view():
    # Trimetric projection from 3d to 2d
    x_rotation = rotation(-60 / 180 * np.pi, 'x')
    z_rotation = rotation(-15 / 180 * np.pi, 'z')

    R_trimetic = np.matmul(x_rotation, z_rotation)
    # R_trimetic = np.eye(3)
    return R_trimetic


R_trimetic = trimetric_view()


def draw_line(screen, line, color=(0, 0, 0), linewidth=1, R=R_trimetic, offset=(0, 0)):
    p1 = line[0]
    p2 = line[1]

    p1_2d = point_3d_to_2d(p1[0], p1[1], p1[2], R, offset=offset)
    p2_2d = point_3d_to_2d(p2[0], p2[1], p2[2], R, offset=offset)

    pygame.draw.line(screen, color, p1_2d, p2_2d, linewidth)

    return p1_2d, p2_2d


def point_3d_to_2d(x, y, z, R=R_trimetic, offset=(0, 0)):
    # flip y-axis for visualisation,
    # so anticlockwise becomes negative and clockwise becomes positive
    y = - y
    x *= scale_factor
    y *= scale_factor
    z *= scale_factor

    x_2d, y_2d, z_2d = np.matmul(R, np.array([x, y, z]))

    x_2d, y_2d = (offset[0] + x_2d, offset[1] - y_2d)

    return x_2d, y_2d


def cv2_to_pygame(image):
    # Rotate and flip to convert cv2 to pygame
    image = np.fliplr(image)
    image = np.rot90(image)
    return image
