# -*- coding: utf-8 -*-
# @File    : game_function.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import sys
import numpy as np
import pygame
from settings import Settings

my_settings = Settings()

x_factor = my_settings.x_factor
y_factor = my_settings.y_factor
z_factor = my_settings.z_factor
origin2d = my_settings.origin2d


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
        settings.initialise_zoom_settings()
        large_car.scale = settings.zoom_region['factor'] * 40
        large_car.reset_dimensions()


def check_keydown_event(event, car, large_car):
    check_car_moving(event, car, large_car)


def check_keyup_event(event, car, large_car):
    if event.key == pygame.K_UP:
        car.moving_fwd = False
        large_car.moving_fwd = False
    elif event.key == pygame.K_DOWN:
        car.moving_bwd = False
        large_car.moving_bwd = False
    elif event.key == pygame.K_LEFT:
        car.turning_left = False
        large_car.turning_left = False
    elif event.key == pygame.K_RIGHT:
        car.turning_right = False
        large_car.turning_right = False
    elif event.key == pygame.K_SPACE:
        car.accelerate = False
        large_car.accelerate = False


def check_car_moving(event, car, large_car):
    if event.key == pygame.K_UP:
        car.moving_fwd = True
        large_car.moving_fwd = True
    elif event.key == pygame.K_DOWN:
        car.moving_bwd = True
        large_car.moving_bwd = True
    elif event.key == pygame.K_LEFT:
        car.turning_left = True
        large_car.turning_left = True
    elif event.key == pygame.K_RIGHT:
        car.turning_right = True
        large_car.turning_right = True
    elif event.key == pygame.K_SPACE:
        car.accelerate = True
        large_car.accelerate = True


def update_screen(settings, screen, workspace, car, large_car, zoom_buttons, i):
    # global x_factor
    # global y_factor
    # global z_factor
    # global origin2d
    # settings.zoom_in()
    # x_factor = settings.x_factor
    # y_factor = settings.y_factor
    # z_factor = settings.z_factor
    # origin2d = settings.origin2d
    screen.fill(settings.bg_color)

    workspace.draw()
    car.draw()
    large_car.draw()
    # zoomed_screen = pygame.transform.smoothscale(screen, (800-i, 600-i))
    # screen.blit(zoomed_screen, ((800-i)//2, (600-i)//2))

    for button in zoom_buttons:
        button.draw_button()

    pygame.display.flip()


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
    x *= x_factor
    y *= y_factor
    z *= z_factor

    x_2d, y_2d, z_2d = np.matmul(R, np.array([x, y, z]))

    x_2d, y_2d = (offset[0] + x_2d, offset[1] - y_2d)

    return x_2d, y_2d


def cv2_to_pygame(image):
    # Rotate and flip to convert cv2 to pygame
    image = np.fliplr(image)
    image = np.rot90(image)
    return image



