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
        self.button_color = (0, 0, 255)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 30)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen.get_rect().center

        self.prep_msg(msg)

    def prep_msg(self, msg):
        self.msg_image = self.font.render(msg, True, self.text_color,
                                          self.button_color)

        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


class ZoomButton(Button):
    def __init__(self, settings, screen, msg):
        super().__init__(settings, screen, msg)

        self.button_color = (100, 100, 100)
        if msg == '+':
            x = self.settings.zoom_region['topleft'][0] + 0.3*self.settings.zoom_region['window_radius']
            y = self.settings.zoom_region['topleft'][1] + 2.2*self.settings.zoom_region['window_radius']
        elif msg == '-':
            x = self.settings.zoom_region['topleft'][0] + self.settings.zoom_region['window_radius']
            y = self.settings.zoom_region['topleft'][1] + 2.2*self.settings.zoom_region['window_radius']
        elif msg == 'R':
            x = self.settings.zoom_region['topleft'][0] + 1.7*self.settings.zoom_region['window_radius']
            y = self.settings.zoom_region['topleft'][1] + 2.2*self.settings.zoom_region['window_radius']
        else:
            raise ValueError('Undefined button message.')

        self.rect.center = (x, y)
        self.prep_msg(msg)
