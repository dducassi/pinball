import pygame

def tint_image(image, color):
    tinted = image.copy()
    color_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    color_surface.fill(color)
    tinted.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

class Bumper:
    def __init__(self, x, y, color, radius, image=None):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.image = image
        self.tinted_images = {}   # cache: color -> tinted surface
        self.glow_start_time = 0
        self.glow_duration = 200

        if image:
            size = int(radius * 2)
            scaled = pygame.transform.scale(image, (size, size))
            # Circular mask
            mask = pygame.Surface((size, size), pygame.SRCALPHA)
            mask.fill((0,0,0,0))
            pygame.draw.circle(mask, (255,255,255,255), (size//2, size//2), radius)
            circular = scaled.copy()
            circular.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
            self.original_circular = circular
            # Pre‑tint for the initial color
            self.tinted_images[color] = tint_image(self.original_circular, color)
        else:
            self.original_circular = None

    def set_color(self, new_color):
        """Change bumper color and update tinted image if needed."""
        if self.color == new_color:
            return
        self.color = new_color
        if self.original_circular and new_color not in self.tinted_images:
            self.tinted_images[new_color] = tint_image(self.original_circular, new_color)

    def hit(self):
        self.glow_start_time = pygame.time.get_ticks()

    def draw(self, screen):
        # Draw base colored circle (optional, keep for fallback)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius * 0.95)

        # Draw image on top if available
        if self.original_circular:
            # Get tinted image for current color (create if missing)
            if self.color not in self.tinted_images:
                self.tinted_images[self.color] = tint_image(self.original_circular, self.color)
            img = self.tinted_images[self.color]
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect)