import pygame
import math

class Flipper:
    def __init__(self, x, y, length, angle, is_left=True, bevel=True, image=None):
        self.pivot = (x, y)
        self.length = length          # can be negative for right flipper
        self.angle = angle
        self.target_angle = angle
        self.angular_vel = 0
        self.is_left = is_left
        self.active = False
        self.pivot_width = 10
        self.tip_width = 5         
        self.width = 5         # for collision (original constant)
        self.bevel = bevel
        self.image = None

        # If an image is provided, scale it to match the flipper's visual size.
        # We'll use absolute length for width, and the pivot_width for height.
        if self.image:
            # Determine desired dimensions
            target_width = abs(length)
            target_height = self.pivot_width * 2   # approximate visual height
            self.original_image = self.image
            self.image = pygame.transform.scale(self.image, (int(target_width), int(target_height)))

        if not self.is_left:
            self.length = -length   # negative for right flipper (drawing)

    def reset(self):
        """Reset flipper to deactivated state and default angle."""
        self.active = False
        self.angular_vel = 0
        if self.is_left:
            self.target_angle = 0.55
        else:
            self.target_angle = -0.55
        self.angle = self.target_angle

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

    def get_edges(self):
        """Return the four edges of the tapered flipper in world coordinates."""
        tip_x, tip_y = self.get_end_pos()
        w_pivot = self.pivot_width
        w_tip = self.tip_width

        dx = tip_x - self.pivot[0]
        dy = tip_y - self.pivot[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return []
        dir_x = dx / length
        dir_y = dy / length
        perp_x = -dir_y
        perp_y = dir_x
        side = 1 if self.is_left else -1
        half_pivot = w_pivot / 2
        half_tip = w_tip / 2

        pivot_bottom = (self.pivot[0] - side * half_pivot * perp_x,
                        self.pivot[1] - side * half_pivot * perp_y)
        pivot_top    = (self.pivot[0] + side * half_pivot * perp_x,
                        self.pivot[1] + side * half_pivot * perp_y)
        tip_top      = (tip_x + side * half_tip * perp_x,
                        tip_y + side * half_tip * perp_y)
        tip_bottom   = (tip_x - side * half_tip * perp_x,
                        tip_y - side * half_tip * perp_y)

        # Edges in order: pivot_bottom -> tip_bottom, tip_bottom -> tip_top, tip_top -> pivot_top, pivot_top -> pivot_bottom
        return [
            (pivot_bottom, tip_bottom),
            (tip_bottom, tip_top),
            (tip_top, pivot_top),
            (pivot_top, pivot_bottom)
        ]

    def draw(self, screen):
        # If we have an image, draw it rotated around the pivot.
        if self.image:
            # Calculate the angle in degrees (pygame uses degrees for rotation)
            angle_deg = math.degrees(self.angle)
            # Rotate the image
            rotated = pygame.transform.rotate(self.image, angle_deg)
            # Position so that the left edge of the image is at the pivot.
            # For a left flipper, the pivot is at the left end; for right, at the right end.
            # We'll assume the image's left edge corresponds to the pivot point.
            rect = rotated.get_rect(midleft=(self.pivot[0], self.pivot[1]))
            screen.blit(rotated, rect)
        else:
            visual_length = self.length * 0.93
            tip_x = self.pivot[0] + math.cos(self.angle) * visual_length
            tip_y = self.pivot[1] + math.sin(self.angle) * visual_length

            w_pivot = 20
            w_tip = 10

            dx = tip_x - self.pivot[0]
            dy = tip_y - self.pivot[1]
            length = math.hypot(dx, dy)
            if length == 0:
                return
            dir_x = dx / length
            dir_y = dy / length
            perp_x = -dir_y
            perp_y = dir_x
            side = 1 if self.is_left else -1

            half_pivot = w_pivot / 2
            half_tip = w_tip / 2

            pivot_bottom = (self.pivot[0] - side * half_pivot * perp_x,
                            self.pivot[1] - side * half_pivot * perp_y + self.width)
            pivot_top    = (self.pivot[0] + side * half_pivot * perp_x,
                            self.pivot[1] + side * half_pivot * perp_y + self.width)
            tip_top      = (tip_x + side * half_tip * perp_x,
                            tip_y + side * half_tip * perp_y + self.width)
            tip_bottom   = (tip_x - side * half_tip * perp_x,
                            tip_y - side * half_tip * perp_y + self.width)

            pygame.draw.polygon(screen, (255, 255, 255),
                                [pivot_bottom, pivot_top, tip_top, tip_bottom])

            pygame.draw.circle(screen, (255, 255, 255),
                               (int(self.pivot[0]), int(self.pivot[1] + self.width)),
                               int(w_pivot//2))
            pygame.draw.circle(screen, (255, 255, 255),
                               (int(tip_x), int(tip_y + self.width)),
                               int(w_tip//2))