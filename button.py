# -*- coding: utf-8 -*-
# @File    : car.py
# @Time    : 27/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame.font


class TextButton:
    def __init__(self, settings, screen):
        self.settings = settings
        self.screen = screen

        self.width = settings['w']
        self.height = settings['h']
        self.center = settings['center']

        self.bg_color = settings['bg_color'] \
            if 'bg_color' in settings else (100, 100, 100)
        self.text_color = settings['text_color'] \
            if 'text_color' in settings else (255, 255, 255)
        font_size = settings['font_size'] \
            if 'font_size' in settings else 30

        self.font = pygame.font.SysFont(None, font_size)

        self.prep_button(settings['msg'])

    def prep_button(self, msg):
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.center

        self.msg_image = self.font.render(msg, True, self.text_color,
                                          self.bg_color)

        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.center

    def draw_button(self):
        self.screen.fill(self.bg_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


class ImgButton:
    def __init__(self, settings, screen):
        self.settings = settings
        self.screen = screen

        self.width = settings['w']
        self.height = settings['h']
        self.center = settings['center']

        self.path = settings['path']
        self.img = pygame.image.load(self.path)

        self.bg_color = settings['bg_color'] \
            if 'bg_color' in settings else (255, 255, 255, 0)

        self.prep_button()

    def prep_button(self):
        self.bg = pygame.Surface((self.width, self.height))
        self.bg.fill(self.bg_color)
        # Set the colorkey and the alpha value for the gray_overlay Surface
        self.bg.set_colorkey((0, 0, 0))
        self.bg.set_alpha(self.bg_color[3])

        self.img = pygame.transform.smoothscale(self.img, (self.width, self.height))

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.center

    def draw_button(self):
        self.screen.blit(self.img, self.rect)
        self.screen.blit(self.bg, self.rect)


