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
origin2d = my_settings.map_screen['origin2d']


def check_event(settings, car, large_car, zoom_buttons):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_event(event, car, large_car)
        elif event.type == pygame.KEYUP:
            check_keyup_event(event, car, large_car)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_mouse_click_event(settings, large_car,
                                    zoom_buttons, mouse_x, mouse_y)


def check_mouse_click_event(settings, large_car,
                            zoom_buttons, mouse_x, mouse_y):
    button_zoom_in, button_zoom_out, button_reset = zoom_buttons
    zoom_in_click = button_zoom_in.rect.collidepoint(mouse_x, mouse_y)
    zoom_out_click = button_zoom_out.rect.collidepoint(mouse_x, mouse_y)
    reset_click = button_reset.rect.collidepoint(mouse_x, mouse_y)

    if zoom_in_click:
        settings.zoom_region['factor'] *= 1.1
        large_car.scale *= 1.1
        large_car.reset_dimensions()
    if zoom_out_click:
        settings.zoom_region['factor'] /= 1.1
        large_car.scale /= 1.1
        large_car.reset_dimensions()
    if reset_click:
        settings.zoom_region['factor'] = settings.initial_zoom_in_factor
        large_car.scale = settings.zoom_region['factor'] * 40
        large_car.reset_dimensions()


def check_keydown_event(event, car, large_car):
    check_car_moving(event, car, large_car)


def check_car_moving(event, car, large_car):
    """
    Note Y-axis is flipped, so left key actually represents turning right
    car.turning_left and car.turning_right actually represent turning in the
    original coordinate system (following right-hand rule) before flipping.
    In the flipped coordinate system, they are opposite.
    """
    if event.key == pygame.K_UP:
        car.moving_fwd = True
        large_car.moving_fwd = True
    elif event.key == pygame.K_DOWN:
        car.moving_bwd = True
        large_car.moving_bwd = True
    elif event.key == pygame.K_RIGHT:  # turn left
        car.turning_left = True
        large_car.turning_left = True
    elif event.key == pygame.K_LEFT:   # turn right
        car.turning_right = True
        large_car.turning_right = True
    elif event.key == pygame.K_SPACE:
        car.brake = True
        large_car.brake = True


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


def update_screen(settings, screen1, screen2,
                  workspace, car, large_car, zoom_buttons, latex_window, i):
    screen1.fill(settings.map_screen['bg_color'])
    screen2.fill(settings.latex_region['bg_color'])

    workspace.draw()
    car.draw()
    large_car.draw()
    latex_window.draw()

    font = pygame.font.Font(None, 38)
    X = font.render('x', True, (0, 0, 0))
    text_width, text_height = X.get_size()
    pos = car.pos
    pos = (pos[0] - text_width // 2, pos[1] - text_height // 2)
    screen1.blit(X, pos)

    for button in zoom_buttons:
        button.draw_button()


def detect_collision(screen, car, red_line):
    # get 2d corner points
    x1, y1 = (car.body_lines[0][0][:2]).astype(int)  # FL
    x2, y2 = (car.body_lines[1][0][:2]).astype(int)  # FR
    x3, y3 = (car.body_lines[3][0][:2]).astype(int)  # RL
    x4, y4 = (car.body_lines[2][0][:2]).astype(int)  # RR

    if red_line[y1, x1] or red_line[y2, x2] or red_line[y3, x3] or red_line[y4, x4]:
        car.car_origin3d = np.float32([1400.4116, 1086.3021, car.wheel_radius])
        car.car_speed = 0
        if red_line[y1, x1]:
            pos = point_3d_to_2d(x1, y1, 0)
            print('FL')
            print(x1, y1)
        if red_line[y2, x2]:
            pos = point_3d_to_2d(x2, y2, 0)
            print('FR')
            print(x2, y2)
        if red_line[y3, x3]:
            pos = point_3d_to_2d(x3, y3, 0)
            print('RL')
            print(x3, y3)
        if red_line[y4, x4]:
            pos = point_3d_to_2d(x4, y4, 0)
            print('RR')
            print(x4, y4)
        car.pos = pos
        # pygame.draw.circle(screen, (0, 0, 0), pos, 20)

        print('collision detected' + str(np.random.rand(1)))
        time.sleep(3)


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


def rotation_around_point(theta, direction, point):
    """
    Returns a function that can be used to transform a matrix of points or a tensor
    of lines by rotating them around a pivot point by an angle along an arbitrary
    axis represented by a unit vector.
    """
    a, b, c = point
    cos = np.cos(theta)
    sin = np.sin(theta)

    if direction == 'x':
        u, v, w = 1, 0, 0
    elif direction == 'y':
        u, v, w = 0, 1, 0
    elif direction == 'z':
        u, v, w = 0, 0, 1
    else:
        raise ValueError("Invalid direction. Must be 'x', 'y', or 'z'.")

    # Rotation matrix
    R = np.array([[cos + (1 - cos) * u**2,     u * (1 - cos) * v - w * sin,  u * (1 - cos) * w + v * sin,  0],
                  [u * (1 - cos) * v + w * sin, cos + (1 - cos) * v**2,      v * (1 - cos) * w - u * sin,  0],
                  [u * (1 - cos) * w - v * sin, v * (1 - cos) * w + u * sin,  cos + (1 - cos) * w**2,     0],
                  [0,                        0,                        0,                        1]])

    # Translation matrix
    T = np.array([[1, 0, 0, a*(1-cos) + b*(1-cos)*u + c*(1-cos)*(-u**2-v**2)],
                  [0, 1, 0, b*(1-cos) + c*(1-cos)*v + a*(1-cos)*(-u**2-v**2)],
                  [0, 0, 1, c*(1-cos) + a*(1-cos)*u + b*(1-cos)*(-u**2-v**2)],
                  [0, 0, 0, 1]])

    # Combined transformation matrix
    M = np.dot(T, R)

    def transform(points):
        """
        Transforms a matrix of points or a tensor of lines by rotating them around
        a pivot point by an angle along an arbitrary axis represented by a unit vector.
        """
        # Convert input to homogeneous coordinates
        points_homog = np.concatenate([points, np.ones((points.shape[0], 1))], axis=1)
        transformed_homog = np.dot(M, points_homog.T).T
        transformed = transformed_homog[:, :3] / transformed_homog[:, 3:4] # Divide by w
        return transformed

    return transform


def trimetric_view():
    # Trimetric projection fron 3d to 2d
    x_rotation = rotation(-60 / 180 * np.pi, 'x')
    z_rotation = rotation(-15 / 180 * np.pi, 'z')

    R_trimetic = np.matmul(x_rotation, z_rotation)
    # R_trimetic = np.eye(3)
    return R_trimetic


def draw_line(screen, line, color=(0, 0, 0), linewidth=1, R=trimetric_view(), offset=origin2d):
    p1 = line[0]
    p2 = line[1]

    p1_2d = point_3d_to_2d(p1[0], p1[1], p1[2], R, offset=offset)
    p2_2d = point_3d_to_2d(p2[0], p2[1], p2[2], R, offset=offset)

    pygame.draw.line(screen, color, p1_2d, p2_2d, linewidth)

    return p1_2d, p2_2d


def point_3d_to_2d(x, y, z, R=trimetric_view(), offset=origin2d):
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


