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
        self.tinted_images = {}
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

            print(f"DEBUG: Bumper radius {radius}: image loaded, created original_circular")

            # Pre‑tint for each possible bumper color (red, blue, white)
            for col in [(255,30,0), (0,100,255), (255,255,255)]:
                self.tinted_images[col] = tint_image(self.original_circular, col)
            print(f"DEBUG: Tinted images keys: {list(self.tinted_images.keys())}")
        else:
            self.original_circular = None
            print(f"DEBUG: Bumper radius {radius}: no image")

    def hit(self):
        self.glow_start_time = pygame.time.get_ticks()

    def draw(self, screen):
        # Draw base colored circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius * 0.95)

        # Draw image on top if available
        if self.original_circular:
            # Use the tinted image for the current color
            if self.color in self.tinted_images:
                img = self.tinted_images[self.color]
            else:
                img = self.original_circular
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect)
