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
from button import TextButton, ImgButton
from latex_window import LatexWindow
from game_stats import GameStats
from control_panel import ControlPanel

import numpy as np


def run_game():
    pygame.init()
    settings = Settings()
    game_stats = GameStats()
    screen = pygame.display.set_mode(
        (settings.main_screen['w'], settings.main_screen['h']))
    pygame.display.set_caption('Mobile Robot')

    screen1 = pygame.Surface((settings.screen1['w'],
                              settings.screen1['h']),
                             pygame.SRCALPHA)
    screen2 = pygame.Surface((settings.screen2['w'],
                              settings.screen2['h']),
                             pygame.SRCALPHA)

    workspace = Workspace(settings, screen1)
    my_car = Car(settings, screen1, game_stats, workspace)
    my_large_car = LargeCar(settings, screen2, workspace)

    latex_window = LatexWindow(settings, screen2, my_car)
    control_panel = ControlPanel(settings, screen2, game_stats, workspace, my_car)

    zoom_buttons = [TextButton(setting, screen) for setting in
                    [settings.but_zoom_in, settings.but_zoom_out, settings.but_zoom_reset]]
    restart_button = TextButton(settings.but_restart, screen)
    trimetric_button = TextButton(settings.but_trimetric, screen)
    axes_buttons = [ImgButton(setting, screen) for setting in settings.buts_rot_axes]
    switch_buttons = [ImgButton(setting, screen) for setting in settings.buts_switch]

    avg = 0
    i = 0
    while True:
        start = time.time()

        screen.blit(screen1, settings.screen1['topleft'])
        screen.blit(screen2, settings.screen2['topleft'])
        # screen.fill((255, 255, 255))

        gf.check_event(settings, game_stats, workspace, my_car, my_large_car,
                       zoom_buttons, restart_button, trimetric_button,
                       axes_buttons, switch_buttons)

        my_car.update()

        if not game_stats.car_freeze:
            # keep it frozen
            my_large_car.update_zoomed_map(my_car.car_orientation,
                                           my_car.wheels_orientation)

        control_panel.update()
        latex_window.update()

        gf.update_screen(settings, game_stats, screen1, screen2,
                         workspace, my_car, my_large_car, zoom_buttons, restart_button,
                         trimetric_button, axes_buttons, switch_buttons, latex_window, control_panel)

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

