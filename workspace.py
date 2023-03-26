# -*- coding: utf-8 -*-
# @File    : workspace.py
# @Time    : 25/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame

import game_function as gf


class Workspace:
    def __init__(self, settings, screen):
        self.screen = screen
        self.settings = settings

    def draw(self):
        self.draw_axes()

    def draw_axes(self):
        origin_x, origin_y = self.settings.origin2d
        origin3d = self.settings.origin3d

        xend = self.settings.xend
        yend = self.settings.yend
        zend = self.settings.zend
        x_tick_interval = self.settings.x_tick_interval
        y_tick_interval = self.settings.y_tick_interval
        z_tick_interval = self.settings.z_tick_interval

        axes_font = pygame.font.Font(None, 24)  # font for axes labels
        tick_font = pygame.font.Font(None, 18)  # font for tick labels
        axes_color = (0, 0, 0)
        tick_color = (100, 100, 100)

        # Draw X-axis
        line = [origin3d, xend]
        _, xpoint_2d = gf.draw_line(self.screen, line, axes_color, 2)
        # X-axis label
        x_label = axes_font.render("X", True, axes_color)
        self.screen.blit(x_label, xpoint_2d)
        # X-axis ticks
        for i in range(0, xend[0] + x_tick_interval, x_tick_interval):
            tick_x, tick_y = gf.point_3d_to_2d(i, 0, 0)
            tick_label = tick_font.render(str(i), True, tick_color)
            self.screen.blit(tick_label, (origin_x + tick_x - 10, origin_y - tick_y))

        # Draw Y-axis
        line = [origin3d, yend]
        _, ypoint_2d = gf.draw_line(self.screen, line, axes_color, 2)

        # Y-axis label
        y_label = axes_font.render("Y", True, axes_color)
        self.screen.blit(y_label, ypoint_2d)
        # Y-axis ticks
        for i in range(0, yend[1] + y_tick_interval, y_tick_interval):
            tick_x, tick_y = gf.point_3d_to_2d(0, i, 0)
            tick_label = tick_font.render(str(i), True, tick_color)
            self.screen.blit(tick_label, (origin_x + tick_x - 10, origin_y - tick_y))

        # Draw Z-axis
        line = [origin3d, zend]
        _, zpoint_2d = gf.draw_line(self.screen, line, axes_color, 2)
        # Z-axis label
        z_label = axes_font.render("Z", True, axes_color)
        self.screen.blit(z_label, zpoint_2d)
        # Z-axis ticks
        for i in range(0, zend[2] + z_tick_interval, z_tick_interval):
            tick_x, tick_y = gf.point_3d_to_2d(0, 0, i)
            tick_label = tick_font.render(str(i), True, tick_color)
            self.screen.blit(tick_label, (origin_x + tick_x - 10, origin_y - tick_y))


        line = [origin3d, [0, 1000, 0]]
        gf.draw_line(self.screen, line, (255, 0, 0), 2)





