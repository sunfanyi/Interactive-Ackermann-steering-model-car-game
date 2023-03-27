# -*- coding: utf-8 -*-
# @File    : car.py
# @Time    : 27/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame.font


class Button:
    def __init__(self, settings, screen, msg):
        self.settings = settings
        self.screen = screen
        # self.screen_rect = self.screen.get_rect()

        self.width, self.height = 25, 25
        self.button_color = (100, 100, 100)
        self.text_color = (255, 255, 255)

        self.font = pygame.font.SysFont(None, 30)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        if msg == '+':
            x = self.settings.zoom_region['centerx'] - 0.7*self.settings.zoom_region['radius']
            y = self.settings.zoom_region['centery'] + 1.2*self.settings.zoom_region['radius']
        elif msg == '-':
            x = self.settings.zoom_region['centerx']
            y = self.settings.zoom_region['centery'] + 1.2*self.settings.zoom_region['radius']
        elif msg == 'R':
            x = self.settings.zoom_region['centerx'] + 0.7*self.settings.zoom_region['radius']
            y = self.settings.zoom_region['centery'] + 1.2*self.settings.zoom_region['radius']
        else:
            raise ValueError('Undefined button message.')

        self.rect.center = (x, y)

        self.prep_msg(msg)

    def prep_msg(self, msg):
        self.msg_image = self.font.render(msg, True, self.text_color,
                                          self.button_color)

        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)
