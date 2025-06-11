# Class for obstacles

import pygame
import random
from settings import Settings

class Obstacle:
    def __init__(self, x, y, c):

        self.x = x
        self.y = y
        self.c = c
    
    def draw(self):
        pygame.draw.circle(self.screen, self.c, (self.x, self.y), self.settings.orad)