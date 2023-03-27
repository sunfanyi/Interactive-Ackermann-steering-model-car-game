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


def check_event(car):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_event(event, car)
        elif event.type == pygame.KEYUP:
            check_keyup_event(event, car)


def check_keydown_event(event, car):
    check_car_moving(event, car)


def check_keyup_event(event, car):
    if event.key == pygame.K_UP:
        car.moving_fwd = False
    elif event.key == pygame.K_DOWN:
        car.moving_bwd = False
    elif event.key == pygame.K_LEFT:
        car.turning_left = False
    elif event.key == pygame.K_RIGHT:
        car.turning_right = False
    elif event.key == pygame.K_SPACE:
        car.accelerate = False


def check_car_moving(event, car):
    if event.key == pygame.K_UP:
        car.moving_fwd = True
    elif event.key == pygame.K_DOWN:
        car.moving_bwd = True
    elif event.key == pygame.K_LEFT:
        car.turning_left = True
    elif event.key == pygame.K_RIGHT:
        car.turning_right = True
    elif event.key == pygame.K_SPACE:
        car.accelerate = True


def update_screen(settings, screen, workspace, car, large_car, i):
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
    large_car.update_mat(car.car_orientation, car.wheels_orientation)
    large_car.draw()
    # zoomed_screen = pygame.transform.smoothscale(screen, (800-i, 600-i))
    # screen.blit(zoomed_screen, ((800-i)//2, (600-i)//2))

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
    return R


def add_translation(R, t=np.array([0, 0, 0, 1])):
    T = np.vstack([R, np.array([[0, 0, 0]])])
    T = np.hstack([T, t.reshape(-1, 1)])
    return T


# Trimetric projection fron 3d to 2d
x_rotation = rotation(-60 / 180 * np.pi, 'x')
z_rotation = rotation(-15 / 180 * np.pi, 'z')

R_trimetic = np.matmul(x_rotation, z_rotation)

def draw_line(screen, line, color=(0, 0, 0), linewidth=1, R=R_trimetic, offset=origin2d):
    p1 = line[0]
    p2 = line[1]

    p1_2d = point_3d_to_2d(p1[0], p1[1], p1[2], R, offset=offset)
    p2_2d = point_3d_to_2d(p2[0], p2[1], p2[2], R, offset=offset)

    pygame.draw.line(screen, color, p1_2d, p2_2d, linewidth)

    return p1_2d, p2_2d


def point_3d_to_2d(x, y, z, R=R_trimetic, offset=origin2d):
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



