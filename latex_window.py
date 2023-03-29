# -*- coding: utf-8 -*-
# @File    : latex_window.py
# @Time    : 28/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pygame
import numpy as np
import io


# class LatexWindow:
#     def __init__(self, settings, screen, car):
#         self.settings = settings
#         self.screen = screen
#
#         self.font = pygame.font.SysFont(None, 36)
#
#         self.symbols_surface = None
#         self.values_surface = None
#
#         self.render_symbols()
#         # self.update()
#
#     def render_symbols(self):
#         self.symbols_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA, 32)
#         self.symbols_surface = self.symbols_surface.convert_alpha()
#
#         symbol_text = "a =\nb =\nc ="
#         text_surface = self.font.render(symbol_text, True, (255, 255, 255))
#         self.symbols_surface.blit(text_surface, (20, 20))
#
#     def update(self, values=1):
#         values = {"a": 0, "b": 0, "c": 0}
#         self.values_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA, 32)
#         self.values_surface = self.values_surface.convert_alpha()
#
#         values_text = f"{values['a']}\n{values['b']}\n{values['c']}"
#         text_surface = self.font.render(values_text, True, (255, 255, 255))
#         self.values_surface.blit(text_surface, (60, 20))
#
#     def draw(self):
#         self.screen.blit(self.symbols_surface, (0, 0))
#         self.screen.blit(self.values_surface, (0, 0))


class LatexWindow:
    def __init__(self, settings, screen, car):
        self.settings = settings
        self.screen = screen
        self.car = car

        self.cache = {}
        self.render_symbols()

    def render_symbols(self):
        x_left = 0.2
        x_right = 0.9
        text_center_aligned = {
            '$V$': (x_left, 1 / 8),
            '$\\dot{\\psi}$': (x_left, 2 / 8),
            '$\\beta_{FL}$': (x_left, 4 / 8),
            '$\\dot{\\phi_{FL}}$': (x_left, 5 / 8),
            '$\\dot{\\phi_{RL}}$': (x_left, 6 / 8),

            '$\\dot{X}$': (x_right, 0.2 * 0.4),
            '$\\dot{Y}$': (x_right, 0.45 * 0.4),
            '$\\dot{\\theta}$': (x_right, 0.7 * 0.4),
            '$\\beta_{FR}$': (x_right, 4 / 8),
            '$\\dot{\\phi_{FR}}$': (x_right, 5 / 8),
            '$\\dot{\\phi_{RR}}$': (x_right, 6 / 8)
        }

        text_left_aligned = {
            'Inputs:': (0, 0),
            'Outputs:': (0, 3.1 / 8)
        }
        # adjust ratio to change figsize, fontsize, DPI to maximise speed
        ratio = 10
        fig = plt.figure(figsize=(20 * ratio, 20 * ratio))
        fig.patch.set_visible(False)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        for key, value in text_left_aligned.items():
            ax.text(value[0], 0.95 - value[1], key, ha='left', va='top', fontsize=108 * ratio)

        for key, value in text_center_aligned.items():
            ax.text(value[0], 0.95 - value[1], key, ha='center', va='top', fontsize=108 * ratio)

        # in-memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=10 // ratio, bbox_inches='tight', pad_inches=0)
        buf.seek(0)

        sur = pygame.image.load(buf)
        self.surface_rendered = sur
        # self.surface_rendered = pygame.transform.scale(sur, (self.settings.latex_region['w'],
        #                                                self.settings.latex_region['h']))

    def update(self):
        return
        # text = '$\\theta$ + %.2f' % 1
        # if text in self.cache:
        #     return
        #     # self.fig_surface = self.cache[text]
        # else:
        #     print('update')
        #     self.ax.clear()
        #     self.ax.axis('off')
        #     self.ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=36)
        #
        #     buf = io.BytesIO()
        #     plt.savefig(buf, format='png', dpi=80, bbox_inches='tight', pad_inches=0)
        #     buf.seek(0)
        #
        #     fig_surface = pygame.image.load(buf)
        #     self.cache[text] = fig_surface
        #     self.fig_surface = fig_surface

    def draw(self):
        self.screen.blit(self.surface_rendered, (0, 0))
