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
from button import Button


def run_game():
    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode(
        (settings.screen_width, settings.screen_height))
    pygame.display.set_caption('Mobile Robot')

    my_car = Car(settings, screen)

    my_large_car = LargeCar(settings, screen)
    workspace = Workspace(settings, screen, my_car)
    zoom_buttons = [Button(settings, screen, label)
                    for label in ['+', '-', 'R']]

    i = 0
    while True:
        gf.check_event(settings, my_car, my_large_car, zoom_buttons)

        my_car.update()

        my_large_car.update_zoomed_map(my_car.car_orientation,
                                       my_car.wheels_orientation)
        gf.update_screen(settings, screen, workspace, my_car, my_large_car, zoom_buttons, i)
        i += 1
        # print('next')
        # time.sleep(0.1)

run_game()

