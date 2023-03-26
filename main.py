# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame

import game_function as gf
from workspace import Workspace
from car import Car
from settings import Settings


def run_game():
    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode(
        (settings.screen_width, settings.screen_height))
    pygame.display.set_caption('Mobile Robot')

    my_car = Car(settings, screen)
    workspace = Workspace(settings, screen)

    while True:
        gf.check_event(my_car)

        my_car.update()

        gf.update_screen(settings, screen, workspace, my_car)


run_game()

