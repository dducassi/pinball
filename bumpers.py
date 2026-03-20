import pygame
import time

def tint_image(image, color):
    """Return a tinted copy of the image using the given color."""
    tinted = image.copy()
    # Create a color surface of the same size
    color_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    color_surface.fill(color)
    # Multiply using blend mode
    tinted.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

class Bumper:
    def __init__(self, x, y, color, radius, image=None):
        self.x = x
        self.y = y
        self.color = color  # current color
        self.radius = radius
        self.image = image
        self.tinted_images = {}  # cache: color -> tinted surface
        self.glow_start_time = 0
        self.glow_duration = 0

        if image:
            # Pre‑scale original image to size
            size = int(radius * 2)
            self.original_scaled = pygame.transform.scale(image, (size, size))
            # Pre‑tint for each color we might need
            # You can add colors as needed; ScoreManager uses red, blue, yellow
            for col in [(255,0,0), (0,100,255), (255,255,0)]:
                self.tinted_images[col] = tint_image(self.original_scaled, col)
        else:
            self.original_scaled = None
    def hit(self):
        """Called when bumper is hit. Start glow effect."""
        self.glow_start_time = pygame.time.get_ticks()
        self.glow_duration = 200  # milliseconds

    def draw(self, screen):
        now = pygame.time.get_ticks()
        glow_active = (now - self.glow_start_time) < self.glow_duration

         # Draw the normal bumper (image or circle)
        if self.original_scaled and self.color in self.tinted_images:
            img = self.tinted_images[self.color]
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect)
        elif self.original_scaled:
            rect = self.original_scaled.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.original_scaled, rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # Then glow if active:
        if glow_active:
            # Draw a semi‑transparent glowing circle behind the bumper
            glow_radius = self.radius * 3
            alpha = max(0, 255 * (1 - (now - self.glow_start_time) / self.glow_duration))
            # Create a surface for the glow
            glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color[:9], int(alpha)), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (int(self.x - glow_radius), int(self.y - glow_radius)), special_flags=pygame.BLEND_ALPHA_SDL2)

       