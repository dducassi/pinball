import pygame
import sys
import os
import random
import math
from settings import Settings

script_dir = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = script_dir


class Ball:
    def __init__(self, bb_game):
        self.screen = bb_game.screen
        self.settings = bb_game.settings
        self.screen_rect = bb_game.screen.get_rect()
        self.lane_x_center = None
        self.lane_bottom = None
        self.launched = False
        self.trapped = False
        self.lost = False
        self.reset()

    def reset(self):
        if self.lane_x_center is not None and self.lane_bottom is not None:
            self.x = self.lane_x_center
            self.y = self.lane_bottom - self.settings.br
        else:
            self.x = self.settings.screen_width // 2
            self.y = self.settings.br
        self.dx = 0
        self.dy = 0
        self.launched = False
        self.trapped = False
        self.lost = False

    def move(self):
        if self.trapped or not self.launched:
            return

        # Friction (from original)
        self.dy += (0.0008 * abs(self.dy)) / self.settings.phys_runs
        if self.dx > 0:
            self.dx -= (0.00045 * abs(self.dy)) / self.settings.phys_runs
        elif self.dx < 0:
            self.dx += (0.00045 * abs(self.dy)) / self.settings.phys_runs

        # Gravity
        if self.y <= self.settings.screen_height:
            self.dy += 0.05 / self.settings.phys_runs

        # Speed cap
        speed = math.hypot(self.dx, self.dy)
        if speed > self.settings.bsmax:
            scale = self.settings.bsmax / speed
            self.dx *= scale
            self.dy *= scale

        max_dy = 40
        if abs(self.dy) > max_dy:
            print(f"!!! Abnormal dy detected: {self.dy}.")

        self.x += self.dx
        self.y += self.dy

    def draw_ball(self):
        pygame.draw.circle(self.screen, self.settings.slv,
                           (int(self.x), int(self.y)), self.settings.br)