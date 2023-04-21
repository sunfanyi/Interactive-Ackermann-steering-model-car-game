# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame
import time
import sys

import game_function as gf
from workspace import Workspace
from car import Car, LargeCar
from settings import Settings
from button import TextButton, ImgButton
from latex_window import LatexWindow
from game_stats import GameStats
from control_panel import ControlPanel
from message_box import MessageBox
from manipulator import Manipulator

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
    my_large_car = LargeCar(settings, screen2, game_stats, workspace)

    latex_window = LatexWindow(settings, screen2, my_car)
    control_panel = ControlPanel(settings, screen2, game_stats, workspace, my_car)
    msg_box = MessageBox(settings, screen1, game_stats)
    manipulator = Manipulator(settings, screen, game_stats, workspace, my_car)

    zoom_buttons = [TextButton(setting, screen) for setting in
                    [settings.but_zoom_in, settings.but_zoom_out, settings.but_zoom_reset]]
    restart_button = TextButton(settings.but_restart, screen)
    trimetric_button = TextButton(settings.but_trimetric, screen)
    axes_buttons = [ImgButton(setting, screen) for setting in settings.buts_rot_axes]
    switch_buttons = [ImgButton(setting, screen) for setting in settings.buts_switch]

    frame_rate = 60
    clock = pygame.time.Clock()

    # # Variables to track frame rate
    # frame_count = 0
    # frame_rate = 0
    # start_time = pygame.time.get_ticks()

    subwindow = None
    subwindow_topleft = (0, 0)

    avg = 0
    i = 0
    while True:
        start = time.time()

        screen.blit(screen1, settings.screen1['topleft'])
        screen.blit(screen2, settings.screen2['topleft'])
        # screen.fill((255, 255, 255))

        gf.check_event(settings, game_stats, workspace, my_car, my_large_car,
                       zoom_buttons, restart_button, trimetric_button,
                       axes_buttons, switch_buttons, manipulator)

        if not game_stats.manipulator:
            my_car.update()
            my_large_car.update_zoomed_map(my_car.car_orientation,
                                           my_car.wheels_orientation)
        else:
            manipulator.update()

        control_panel.update()
        latex_window.update()
        msg_box.update()

        gf.update_screen(settings, game_stats, screen1, screen2,
                         workspace, my_car, my_large_car, zoom_buttons, restart_button,
                         trimetric_button, axes_buttons, switch_buttons,
                         latex_window, control_panel, msg_box, manipulator)

        pygame.display.update()

        if manipulator.pause:
            time.sleep(2)
        clock.tick(frame_rate)


        # frame_count += 1
        # # Calculate the elapsed time and frame rate
        # elapsed_time = pygame.time.get_ticks() - start_time
        # if elapsed_time > 0:
        #     frame_rate = frame_count / (elapsed_time / 1000)

        # print("Frame rate:", frame_rate)
        # print(my_car.car_origin3d)
        # print(my_car.car_origin2d)
        # print(my_car.car_orientation)
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

