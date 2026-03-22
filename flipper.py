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
        self.width = 3          # for collision (kept as rectangle thickness)
        self.bevel = bevel
        if not self.is_left:
            self.length = -length   # negative for right flipper (drawing)

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
        end_x = self.pivot[0] + math.cos(self.angle) * abs(self.length)
        end_y = self.pivot[1] + math.sin(self.angle) * abs(self.length)
        return (end_x, end_y)

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
        self.width = 3          # used for collision (rectangle thickness)
        self.bevel = bevel
        if not self.is_left:
            self.length = -length   # negative for right flipper (drawing)

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
        # Tip position using self.length (may be negative for right flipper)
        tip_x = self.pivot[0] + math.cos(self.angle) * self.length
        tip_y = self.pivot[1] + math.sin(self.angle) * self.length

        # Visual dimensions (narrow at pivot, wide at tip)
        w_pivot = 16
        w_tip = 8

        # Direction vector from pivot to tip
        dx = tip_x - self.pivot[0]
        dy = tip_y - self.pivot[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        dir_x = dx / length
        dir_y = dy / length

        # Perpendicular (rotate 90° counter‑clockwise)
        perp_x = -dir_y
        perp_y = dir_x

        # Mirror perpendicular for right flipper
        side = 1 if self.is_left else -1

        half_pivot = w_pivot / 2
        half_tip = w_tip / 2

        # Four corners of the tapered shape
        pivot_bottom = (self.pivot[0] - side * half_pivot * perp_x,
                        self.pivot[1] - side * half_pivot * perp_y)
        pivot_top    = (self.pivot[0] + side * half_pivot * perp_x,
                        self.pivot[1] + side * half_pivot * perp_y)
        tip_top      = (tip_x + side * half_tip * perp_x,
                        tip_y + side * half_tip * perp_y)
        tip_bottom   = (tip_x - side * half_tip * perp_x,
                        tip_y - side * half_tip * perp_y)

        # Draw the flipper body
        pygame.draw.polygon(screen, (255, 255, 255),
                            [pivot_bottom, pivot_top, tip_top, tip_bottom])

        # Draw rounded ends
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(self.pivot[0]), int(self.pivot[1])), int(w_pivot//2))
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(tip_x), int(tip_y)), int(w_tip//2))

        # Bevel effect
        if self.bevel:
            # Light line on top edge
            pygame.draw.line(screen, (210, 210, 210), pivot_top, tip_top, 1)
            # Dark line on bottom edge
            pygame.draw.line(screen, (80, 80, 80), pivot_bottom, tip_bottom, 1)