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

        self.width, self.height = 25, 25
        self.center = (0, 0)
        self.button_color = (0, 0, 255)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 30)

        self.prep_button(msg)

    def prep_button(self, msg):
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.center

        self.msg_image = self.font.render(msg, True, self.text_color,
                                          self.button_color)

        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.center

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


class ZoomButton(Button):
    def __init__(self, settings, screen, msg, which_screen):
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

        self.center = pos_to_absolute((x, y), self.settings, which_screen)
        self.prep_button(msg)


class RestartButton(Button):
    def __init__(self, settings, screen, msg, which_screen):
        super().__init__(settings, screen, msg)

        self.width, self.height = 100, 40
        self.button_color = (0, 255, 0)

        self.center = pos_to_absolute((100, 50), self.settings, which_screen)
        self.prep_button(msg)


def pos_to_absolute(pos, settings, which_screem):
    """
    Convert the position of a button from subscreen to the main screen.
    This is done because the input screen of a button should always be the main
    for MouseClick event, but the button positions are defined in the subscreens.
    """
    if which_screem == '1':
        x = pos[0] + settings.screen1['topleft'][0]
        y = pos[1] + settings.screen1['topleft'][1]
    elif which_screem == '2':
        x = pos[0] + settings.screen2['topleft'][0]
        y = pos[1] + settings.screen2['topleft'][1]
    else:
        raise ValueError('Undefined screen number.')

    return (x, y)
