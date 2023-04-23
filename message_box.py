# -*- coding: utf-8 -*-
# @File    : message_box.py
# @Time    : 19/04/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import pygame


class MessageBox:
    def __init__(self, settings, screen, game_stats):
        self.settings = settings.message_box
        self.screen = screen
        self.game_stats = game_stats

        self.font = pygame.font.SysFont(None, self.settings['font_size'])
        self.surface = pygame.Surface((self.settings['w'], self.settings['h']),
                                      pygame.SRCALPHA)

    def update(self):
        if self.game_stats.car_freeze:
            msg = 'Collision detected at: {}\n' \
                  'Press up/down/space'.format(self.game_stats.collision_point)
        else:
            if self.game_stats.started:
                msg = 'Driving to the end point...'

                end_time = pygame.time.get_ticks()
                timer_msg = (end_time - self.game_stats.start_time) / 1000
                msg = msg + '\nTime: {:.2f} s'.format(timer_msg)
            else:
                msg = 'Driving to the start point...'
        if self.game_stats.manipulator:
            msg = 'Watching manipulator moving...\n' \
                    '(Press Esc to stop)'

        if self.game_stats.best_time_score is not None:
            msg = msg + '\nBest time: {:.2f} s'.format(self.game_stats.best_time_score/1000)
        self.surface.fill(self.settings['bg_color'])

        # Split the text into separate lines
        lines = msg.split('\n')
        text_surfaces = [self.font.render(line, True, self.settings['text_color'])
                         for line in lines]
        text_height = text_surfaces[0].get_height()

        for i, text_surface in enumerate(text_surfaces):
            label_rect = text_surface.get_rect()
            label_rect.centerx = self.surface.get_rect().center[0]
            label_rect.centery = 20 + i * text_height
            self.surface.blit(text_surface, label_rect)

    def show_msg(self):
        self.screen.blit(self.surface, self.settings['topleft'])
