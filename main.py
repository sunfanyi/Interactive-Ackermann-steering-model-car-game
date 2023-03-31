# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame
import time

import game_function as gf
from workspace import Workspace
from car import Car, LargeCar
from settings import Settings
from button import ZoomButton
from latex_window import LatexWindow
from game_stats import GameStats

import numpy as np


def run_game():
    pygame.init()
    settings = Settings()
    game_stats = GameStats()
    screen = pygame.display.set_mode(
        (settings.main_screen['w'], settings.main_screen['h']))
    pygame.display.set_caption('Mobile Robot')

    screen1 = pygame.Surface((settings.map_screen['w'],
                              settings.map_screen['h']),
                             pygame.SRCALPHA)
    screen2 = pygame.Surface((settings.latex_region['w'],
                              settings.latex_region['h']),
                             pygame.SRCALPHA)
    # screen1 = screen
    my_car = Car(settings, screen1, game_stats)

    my_large_car = LargeCar(settings, screen1)
    workspace = Workspace(settings, screen1, my_car)
    zoom_buttons = [ZoomButton(settings, screen1, label)
                    for label in ['+', '-', 'R']]
    latex_window = LatexWindow(settings, screen2, my_car)

    avg = 0
    i = 0
    while True:
        start = time.time()

        # must be before update()
        gf.detect_collision(game_stats, screen,
                            my_car, my_large_car, workspace.red_line)
        screen.fill((255, 255, 255))

        gf.check_event(settings, game_stats, my_car, my_large_car, zoom_buttons)

        my_car.update()
        my_large_car.update_zoomed_map(my_car.car_orientation,
                                       my_car.wheels_orientation)
        latex_window.update()

        gf.update_screen(settings, game_stats, screen1, screen2,
                         workspace, my_car, my_large_car, zoom_buttons, latex_window, i)

        screen.blit(screen1, settings.map_screen['topleft'])
        screen.blit(screen2, settings.latex_region['topleft'])
        pygame.display.update()

        # i += 1
        # end = time.time()
        # last = avg
        # new = end - start
        # avg = (last*(i-1) + new)/i
        # print('average time interval: ', avg)
        # if i == 1000:
        #     i = 0
        #     for j in range(10):
        #         print('reset')


run_game()

