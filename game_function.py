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
origin2d = my_settings.origin


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
    # if event.key == pygame.K_q:
    #     quit_game(stats)
    # elif event.key == pygame.K_p:
    #     start_game(settings, stats, sb, screen, ship, bullets, aliens)
    # elif event.key == pygame.K_SPACE and stats.game_active:
    #     fire_bullet(settings, screen, ship, bullets)
    # else:
    check_car_moving(event, car)


def check_keyup_event(event, car):
    if event.key == pygame.K_RIGHT:
        car.moving_right = False
    elif event.key == pygame.K_LEFT:
        car.moving_left = False
    elif event.key == pygame.K_UP:
        car.moving_up = False
    elif event.key == pygame.K_DOWN:
        car.moving_down = False


def check_car_moving(event, car):
    if event.key == pygame.K_RIGHT:
        car.moving_right = True
    elif event.key == pygame.K_LEFT:
        car.moving_left = True
    elif event.key == pygame.K_UP:
        car.moving_up = True
    elif event.key == pygame.K_DOWN:
        car.moving_down = True


def update_screen(settings, screen, workspace, my_car):

    screen.fill(settings.bg_color)

    workspace.draw()
    # for
    my_car.draw()

    pygame.display.flip()


def draw_line(screen, line, color=(0, 0, 0), linewidth=1):
    p1 = line[0]
    p2 = line[1]

    x1_2d, y1_2d = point_3d_to_2d(p1[0], p1[1], p1[2])
    x2_2d, y2_2d = point_3d_to_2d(p2[0], p2[1], p2[2])

    p1_2d = (origin2d[0] + x1_2d, origin2d[1] - y1_2d)
    p2_2d = (origin2d[0] + x2_2d, origin2d[1] - y2_2d)

    pygame.draw.line(screen, color, p1_2d, p2_2d, linewidth)

    return p1_2d, p2_2d


def point_3d_to_2d(x, y, z):
    x *= x_factor
    y *= y_factor
    z *= z_factor

    # Trimetric projection fron 3d to 2d
    x_rotation = rotation(120/180 * np.pi, 'x').T
    z_rotation = rotation(-15/180 * np.pi, 'z').T

    R = np.matmul(x_rotation, z_rotation)

    x_2d, y_2d, z_2d = np.matmul(R, np.array([x, y, z]))

    return x_2d, y_2d





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