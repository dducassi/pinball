import pygame

class Plunger:
    def __init__(self, x, y, max_pull=100, pull_speed=5, max_launch_speed=15):
        self.x = x
        self.y = y
        self.max_pull = max_pull
        self.pull_speed = pull_speed
        self.max_launch_speed = max_launch_speed
        self.current_pull = 0
        self.pulling = False

    def start_pull(self):
        self.pulling = True

    def stop_pull(self):
        self.pulling = False

    def update(self, dt):
        if self.pulling and self.current_pull < self.max_pull:
            self.current_pull += self.pull_speed * dt
            if self.current_pull > self.max_pull:
                self.current_pull = self.max_pull

    def release(self):
        launch_speed = (self.current_pull / self.max_pull) * self.max_launch_speed
        self.current_pull = 0
        self.pulling = False
        return launch_speed

    def reset(self):
        self.current_pull = 0
        self.pulling = False

    def draw(self, screen, color=(255,255,255)):
        # Draw a vertical line that extends upward as pull increases
        pull_height = self.current_pull / self.max_pull * 50
        start = (self.x, self.y)
        end = (self.x, self.y - pull_height)
        #pygame.draw.line(screen, color, start, end, 5)
        #pygame.draw.circle(screen, color, (int(end[0]), int(end[1])), 3)