import pygame

def tint_image(image, color):
    tinted = image.copy()
    color_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    color_surface.fill(color)
    tinted.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

class Light:
    def __init__(self, x, y, base_radius, color, image=None):
        self.x = x
        self.y = y
        self.base_radius = base_radius
        self.color = color
        self.original_image = image
        self.on = False
        self.on_time = 0
        self.duration = 200
        self.image = None
        self._update_image()

    def _update_image(self):
        """Create or update the base‑sized image with the current color."""
        if self.original_image:
            size = int(self.base_radius * 2)
            scaled = pygame.transform.scale(self.original_image, (size, size))
            # If color is white (or very close), don't tint; use original scaled image.
            if self.color == (255,255,255):
                self.image = scaled
            else:
                self.image = tint_image(scaled, self.color)
        else:
            self.image = None

    def reset(self, initial_color):
        """Turn off light and set color to initial."""
        self.on = False
        self.color = initial_color
        self._update_image()

    def set_color(self, new_color):
        self.color = new_color
        self._update_image()

    def turn_on(self, current_time):
        self.on = True
        self.on_time = current_time

    def update(self, current_time):
        if self.on and current_time - self.on_time > self.duration:
            self.on = False

    def draw(self, screen):
        radius = self.base_radius * 1.1 if self.on else self.base_radius
        if self.image:
            if self.on:
                # Scale up for the active state
                size = int(radius * 2)
                scaled = pygame.transform.scale(self.image, (size, size))
                rect = scaled.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(scaled, rect)
            else:
                rect = self.image.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(self.image, rect)
        else:
            # Fallback to a circle if no image
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(radius))