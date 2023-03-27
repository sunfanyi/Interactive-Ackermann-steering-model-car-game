# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame

import game_function as gf
from workspace import Workspace
from car import Car, LargeCar
from settings import Settings


def run_game():
    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode(
        (settings.screen_width, settings.screen_height))
    pygame.display.set_caption('Mobile Robot')

    my_car = Car(settings, screen)
    my_large_car = LargeCar(settings, screen)
    workspace = Workspace(settings, screen, my_car)
    i = 0
    while True:
        gf.check_event(my_car)

        my_car.update()
        my_large_car.update_mat(my_car.car_orientation, my_car.wheels_orientation)

        gf.update_screen(settings, screen, workspace, my_car, my_large_car, i)
        i += 1
        # print('next')

run_game()

