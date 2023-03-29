# -*- coding: utf-8 -*-
# @File    : latex_window.py
# @Time    : 28/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import matplotlib
# non-interactive backend to optimise speed
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pygame
import numpy as np
import io


class LatexWindow:
    def __init__(self, settings, screen, car):
        self.settings = settings
        self.screen = screen
        self.car = car

        self.render_symbols()

    def render_symbols(self):
        x_left = 0.2
        x_right = 0.9
        text_center_aligned = {
            '$V$': (x_left, 1 / 8),
            '$\\dot{\\psi}$': (x_left, 2 / 8),

            '$\\dot{X}$': (x_right, 0.2 * 0.4),
            '$\\dot{Y}$': (x_right, 0.45 * 0.4),
            '$\\dot{\\theta}$': (x_right, 0.7 * 0.4),

            '$\\beta_{FL}$': (x_left, 4 / 8),
            '$\\dot{\\phi_{FL}}$': (x_left, 5 / 8),
            '$\\dot{\\phi_{RL}}$': (x_left, 6 / 8),

            '$\\beta_{FR}$': (x_right, 4 / 8),
            '$\\dot{\\phi_{FR}}$': (x_right, 5 / 8),
            '$\\dot{\\phi_{RR}}$': (x_right, 6 / 8)
        }

        self.symbol_pos = list(text_center_aligned.values())

        text_left_aligned = {
            'Inputs:': (0, 0),
            'Outputs:': (0, 3.1 / 8)
        }

        # adjust ratio to change figsize, fontsize, DPI to optimise speed
        ratio = 10
        fig = plt.figure(figsize=(22 * ratio, 20 * ratio))
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

        self.surface_rendered = pygame.image.load(buf)

    def update(self):
        """
        The car is flipped with Y-axis, so left key actually represents turning right
        Therefore:
            1. Clockwise rotation around Z-axis is positive.
            2. Left wheels become right wheels, and vice versa.
            3. Wheels' orientation change sign as left turn becomes right turn.
        """
        self.surface_updating = pygame.Surface((self.settings.latex_region['w'],
                                                self.settings.latex_region['h']),
                                               pygame.SRCALPHA)

        values = [self.car.car_speed,  # V
                  -self.car.P_i_dot[3],  # dot_psi

                  self.car.P_i_dot[0],  # x dot
                  self.car.P_i_dot[1],  # y dot
                  - self.car.P_i_dot[2],  # theta dot

                  - self.car.wheels_orientation[1] * 180 / np.pi,  # beta_FL
                  self.car.wheels_speed[1],  # phi_FL dot
                  self.car.wheels_speed[3],  # phi_RL dot

                  - self.car.wheels_orientation[0] * 180 / np.pi,  # beta_FR
                  self.car.wheels_speed[0],  # phi_FR dot
                  self.car.wheels_speed[2]]  # phi_RR dot

        units = ['m/s', 'rad/s', 'm/s', 'm/s', 'rad/s',
                 'deg', 'rad/s', 'rad/s', 'deg', 'rad/s', 'rad/s']

        font = pygame.font.Font(None, 24)
        rect = self.surface_rendered.get_rect()
        w = rect.width
        h = rect.height
        for i, (val, unit) in enumerate(zip(values, units)):
            if unit == 'rad/s':
                text = '=  %.3f' % val + ' ' + unit
            else:
                text = '=  %.2f' % val + ' ' + unit
            label = font.render(text, True, (0, 0, 0))

            label_width = label.get_width()
            label_height = label.get_height()
            pos_x = int((self.symbol_pos[i][0] + 0.08) * w)
            pos_y = int((self.symbol_pos[i][1] + 0.02) * h + label_height / 2)
            pos = (pos_x, pos_y)

            self.surface_updating.blit(label, pos)

    def draw(self):
        self.screen.blit(self.surface_rendered, (0, 0))
        self.screen.blit(self.surface_updating, (0, 0))
