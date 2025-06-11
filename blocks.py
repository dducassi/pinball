# Class for blocks

import pygame
import random
from settings import Settings

class Block:
    def __init__(self, x1, y1, x2, y2, x3, y3, x4, y4, c):

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.x4 = x4
        self.y4 = y4
        self.c = c
    
    def draw_block(self):
        pygame.draw.polygon(self.screen, self.c, [(self.x1, self.y1), (self.x2, self.y2), (self.x3, self.y3), (self.x4, self.y4)])



#[(0, self.settings.screen_height), (100, self.settings.screen_height), (0, self.settings.screen_height - 120), (100, self.settings.screen-height - 20)]