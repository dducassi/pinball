import pygame
import math

class Flipper:
    def __init__(self, x, y, length, angle, is_left=True, bevel=True):
        self.pivot = (x, y)
        self.length = length
        self.angle = angle
        self.target_angle = angle
        self.angular_vel = 0
        self.is_left = is_left
        self.active = False
        self.width = 3
        self.bevel = bevel
        if not self.is_left:
            self.length = -length  # negative for right flipper

    def update(self):
        self.angular_vel += (self.target_angle - self.angle) * 0.06
        self.angular_vel *= 0.8
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
        # Draw main flipper
        pygame.draw.line(screen, (255, 255, 255), self.pivot, end_pos, 10)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.pivot[0]), int(self.pivot[1])), 4)

        # Bevel effect (if enabled)
        if self.bevel:
            # Compute unit direction vector from pivot to tip
            dx = end_pos[0] - self.pivot[0]
            dy = end_pos[1] - self.pivot[1]
            length = math.hypot(dx, dy)
            if length > 0:
                dir_x = dx / length
                dir_y = dy / length
                # Perpendicular vector (rotate 90° clockwise)
                perp_x = -dir_y
                perp_y = dir_x
                # For right flipper, flip the side (since its direction is reversed)
                side = 1 if self.is_left else -1
                offset = 2
                # Top edge (shifted in perp direction)
                top_start = (self.pivot[0] + side * perp_x * offset, self.pivot[1] + side * perp_y * offset)
                top_end = (end_pos[0] + side * perp_x * offset, end_pos[1] + side * perp_y * offset)
                # Bottom edge (shifted opposite)
                bottom_start = (self.pivot[0] - side * perp_x * offset, self.pivot[1] - side * perp_y * offset)
                bottom_end = (end_pos[0] - side * perp_x * offset, end_pos[1] - side * perp_y * offset)
                # Draw highlight (white) on top edge
                pygame.draw.line(screen, (55, 55, 255), top_start, top_end, 1)
                # Draw shadow (dark gray) on bottom edge
                pygame.draw.line(screen, (255, 255, 255), bottom_start, bottom_end, 1)