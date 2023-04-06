# -*- coding: utf-8 -*-
# @File    : game_stats.py
# @Time    : 30/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm


class GameStats:
    def __init__(self):
        self.game_active = True

        # for collision detection
        self.car_freeze = False
        self.collision_point = [0, 0, 0]
