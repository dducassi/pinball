import pygame
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    # Running as EXE - use temporary bundle directory
    base_dir = sys._MEIPASS
else:
    # Running as script - use normal script directory
    base_dir = script_dir

from settings import Settings
import random


class Ball():
    def __init__(self, bb_game):
        # Give ball screen, settings, start ball
        self.screen = bb_game.screen
        self.settings = bb_game.settings
        self.screen_rect = bb_game.screen.get_rect()
        self.reset()
    
    def reset(self):

        # Start in the center of the screen
        self.x = self.settings.screen_width // 2
        self.y = self.settings.br
        # Random initial direction up
        self.dx = self.settings.bs * random.choice([-2, -1, 1, 2])
        self.dy = self.settings.bs * 1.1

    def move(self):
        # Move the ball according to its speed, minus friction decay
        max_speed = 30
        self.x += self.dx 
        self.y += self.dy 

        # Account for gravity and friction causing loss of inertia
        self.dy += 0.0008 * (self.dy * -1)
        

        # If ball is falling, accelerate y speed
        if self.dy > 0:
            self.dy -= 0.02 * (self.dy * -1)
            
        
        # Always fall
        if self.y <= self.settings.screen_height:
            self.dy += 0.1

         # Cap the speed vector magnitude
        speed = (self.dx ** 2 + self.dy ** 2) ** 0.5
        if speed > max_speed:
            scale = max_speed / speed
            self.dx *= scale
            self.dy *= scale



    def check_collision(self):
        # Bounce off the left and right walls
        if self.x - self.settings.br <= 0:
            self.x = 0 + self.settings.br
            self.dx = abs(0.8 * self.dx)
            self.dy = self.dy * 0.8
        elif self.x >= self.settings.screen_width - self.settings.br:
            self.x = self.settings.screen_width - self.settings.br
            self.dx = -(abs(0.8 * self.dx))
            self.dy = self.dy * 0.8
        
        
        
        ### If the ball hits a 45 degree wall, dx an dy should trade places!

        # top left corner
        #if self.x <= 125:
            #if self.y <= 125:
                #self.dx, self.dy = -self.dy, self.dx
        
            
        # Bounce off the top wall or signal game over if it hits the bottom
        if self.y <= self.settings.br:
            self.y = self.settings.br
            self.dy = abs(0.8 * self.dy)
            self.dx = self.dx * 0.8
        elif self.y >= self.settings.screen_height + 1000:
            return True
        return False
    
    def draw_ball(self):
        pygame.draw.circle(self.screen, self.settings.slv, 
            (int(self.x), int(self.y)), self.settings.br)