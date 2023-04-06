# -*- coding: utf-8 -*-
# @File    : car.py
# @Time    : 27/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame.font


class TextButton:
    def __init__(self, settings, screen, msg):
        self.settings = settings
        self.screen = screen

        self.width, self.height = 50, 50
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


class ImgButton:
    def __init__(self, settings, screen, img_path):
        self.settings = settings
        self.screen = screen

        self.width, self.height = 50, 50
        self.center = (0, 0)

        self.img = pygame.image.load(img_path)
        self.bg_color = (255, 255, 255, 0)

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


class ZoomButton(TextButton):
    def __init__(self, settings, screen, msg, which_screen):
        super().__init__(settings, screen, msg)

        self.width, self.height = 25, 25
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


class RestartButton(TextButton):
    def __init__(self, settings, screen, msg, which_screen):
        super().__init__(settings, screen, msg)

        self.width, self.height = 100, 40
        self.button_color = (0, 255, 0)

        self.center = pos_to_absolute((100, 50), self.settings, which_screen)
        self.prep_button(msg)


class TrimetricButton(TextButton):
    def __init__(self, settings, screen, msg, which_screen):
        super().__init__(settings, screen, msg)

        self.width = self.settings.axes_rotation['trimetric_w']
        self.height = self.settings.axes_rotation['trimetric_h']
        center = self.settings.axes_rotation['trimetric_center']
        self.center = pos_to_absolute(center, self.settings, which_screen)

        self.button_color = self.settings.axes_rotation['bg_color']

        self.prep_button(msg)


def get_axes_rotation_buttons(settings, screen, which_screen):
    axes_buttons = []
    paths = settings.axes_rotation['path']
    center = settings.axes_rotation['center']
    for i in range(6):
        button = ImgButton(settings, screen, paths[i])
        button.width = settings.axes_rotation['icon_w']
        button.height = settings.axes_rotation['icon_w']
        button.center = pos_to_absolute(center[i], settings, which_screen)
        button.bg_color = settings.axes_rotation['bg_color']
        button.prep_button()

        # draw boundary
        # bdry = pygame.Rect(0, 0, button.width, button.height)
        # pygame.draw.rect(button.img, (0, 0, 0), bdry, 1)
        axes_buttons.append(button)
    return axes_buttons


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

