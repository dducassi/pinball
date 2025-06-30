# Class for the flippers

import pygame
import math
from settings import Settings

class Flipper:
    def __init__(self, x, y, length, angle, is_left=True):
        self.pivot = (x, y)
        self.length = length
        self.angle = angle
        self.target_angle = angle
        self.angular_vel = 0
        self.is_left = is_left
        self.active = False
        self.width = 5
        if self.is_left == False:
            self.length = -length

    def update(self):
        # Smooth rotation using angular velocity
        self.angular_vel += (self.target_angle - self.angle) * 0.2
        self.angular_vel *= 0.73  # Damping
        self.angle += self.angular_vel
        

    def activate(self):
        self.target_angle = self.angle - 1.0 if self.is_left else self.angle + 1.0

    def deactivate(self):
        if self.is_left:
            self.target_angle = 0.55
        else:
            self.target_angle = -0.55

    def get_end_pos(self):
        end_x = self.pivot[0] + math.cos(self.angle) * self.length
        end_y = self.pivot[1] + math.sin(self.angle) * self.length
        return (end_x, end_y)

    def draw(self, screen):
        end_pos = self.get_end_pos()
        pygame.draw.line(screen, (255, 255, 255), self.pivot, end_pos, 10)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.pivot[0]), int(self.pivot[1])), 4)



