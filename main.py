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
        (settings.main_screen['w'], settings.main_screen['h']))
    pygame.display.set_caption('Mobile Robot')

    screen1 = pygame.Surface((settings.map_screen['w'],
                              settings.map_screen['h']),
                             pygame.SRCALPHA)
    screen2 = pygame.Surface((140, 180))

    my_car = Car(settings, screen1)

    my_large_car = LargeCar(settings, screen1)
    workspace = Workspace(settings, screen1, my_car)
    zoom_buttons = [Button(settings, screen1, label)
                    for label in ['+', '-', 'R']]

    i = 0
    while True:
        gf.check_event(settings, my_car, my_large_car, zoom_buttons)

        my_car.update()

        my_large_car.update_zoomed_map(my_car.car_orientation,
                                       my_car.wheels_orientation)
        gf.update_screen(settings, screen1, workspace, my_car, my_large_car, zoom_buttons, i)

        screen.blit(screen1, settings.map_screen['topleft'])
        screen.blit(screen2, (800, 0))
        pygame.display.update()

        i += 1
        # print('next')
        # time.sleep(0.1)

run_game()
