import pygame
import math

class Block:
    def __init__(self, vertices, color, restitution, image=None, pattern=False):
        self.vertices = vertices
        self.c = color
        self.restitution = restitution
        self.image = None
        self.rect = None
        self.pattern = pattern
        self.pattern_spacing = 3 # pixels between dots
        self.pattern_dot_radius = 1       # dot radius (1 = tiny dot)

        if image:
            # Compute bounding box
            xs = [v[0] for v in vertices]
            ys = [v[1] for v in vertices]
            xmin, xmax = min(xs), max(xs)
            ymin, ymax = min(ys), max(ys)
            w = int(xmax - xmin)
            h = int(ymax - ymin)
            # Scale texture to bounding box
            scaled = pygame.transform.scale(image, (w, h))
            # Create mask for polygon shape
            mask = pygame.Surface((w, h), pygame.SRCALPHA)
            mask.fill((0,0,0,0))
            translated_vertices = [(x - xmin, y - ymin) for (x, y) in vertices]
            pygame.draw.polygon(mask, (255,255,255,255), translated_vertices)
            # Apply mask to texture
            self.texture = scaled.copy()
            self.texture.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
            self.texture_rect = pygame.Rect(xmin, ymin, w, h)
        else:
            self.texture = None
            self.texture_rect = None

        # Build edges for collision
        self.edges = []
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1) % n]
            self.edges.append((x1, y1, x2, y2))

    def _closest_point_on_segment(self, px, py, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx*dx + dy*dy
        if length_sq == 0:
            return x1, y1
        t = ((px - x1)*dx + (py - y1)*dy) / length_sq
        t = max(0, min(1, t))
        return x1 + t*dx, y1 + t*dy

    def collide(self, ball_x, ball_y, ball_dx, ball_dy, ball_radius):
        best_penetration = 0
        best_nx = best_ny = 0
        best_cx = best_cy = None
        hit = False

        # Check edges
        for (x1, y1, x2, y2) in self.edges:
            cx, cy = self._closest_point_on_segment(ball_x, ball_y, x1, y1, x2, y2)
            dx = ball_x - cx
            dy = ball_y - cy
            dist = math.hypot(dx, dy)
            if dist < ball_radius:
                penetration = ball_radius - dist
                if penetration > best_penetration:
                    best_penetration = penetration
                    best_cx, best_cy = cx, cy
                    if dist > 0:
                        best_nx = dx / dist
                        best_ny = dy / dist
                    else:
                        edge_dx = x2 - x1
                        edge_dy = y2 - y1
                        best_nx = edge_dy
                        best_ny = -edge_dx
                        norm_len = math.hypot(best_nx, best_ny)
                        if norm_len > 0:
                            best_nx /= norm_len
                            best_ny /= norm_len
                        else:
                            best_nx, best_ny = 0, 1
                    hit = True

        # Check vertices
        for (vx, vy) in self.vertices:
            dx = ball_x - vx
            dy = ball_y - vy
            dist = math.hypot(dx, dy)
            if dist < ball_radius:
                penetration = ball_radius - dist
                if penetration > best_penetration:
                    best_penetration = penetration
                    best_cx, best_cy = vx, vy
                    if dist > 0:
                        best_nx = dx / dist
                        best_ny = dy / dist
                    else:
                        best_nx, best_ny = 0, 1
                    hit = True

        if not hit:
            return ball_x, ball_y, ball_dx, ball_dy, False

        # Position correction
        ball_x = best_cx + best_nx * ball_radius
        ball_y = best_cy + best_ny * ball_radius

        # Velocity response
        vn = ball_dx * best_nx + ball_dy * best_ny
        vt_x = ball_dx - vn * best_nx
        vt_y = ball_dy - vn * best_ny

        RESTING_THRESHOLD = 0.75
        if vn < 0:
            if -vn < RESTING_THRESHOLD:
                vn = 0
            else:
                vn = -vn * self.restitution

        ball_dx = vt_x + vn * best_nx
        ball_dy = vt_y + vn * best_ny

        return ball_x, ball_y, ball_dx, ball_dy, True

    def _point_in_polygon(self, px, py):
        inside = False
        n = len(self.vertices)
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i+1) % n]
            if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1) + x1):
                inside = not inside
        return inside

    def draw(self, screen):
        # Draw the solid polygon or texture
        if self.texture:
            screen.blit(self.texture, self.texture_rect)
        else:
            pygame.draw.polygon(screen, self.c, self.vertices)

                # Draw bevel effect for sloping edges (funnel blocks)
        if self.pattern and len(self.vertices) == 4:
            edges = [(self.vertices[i], self.vertices[(i+1)%4]) for i in range(4)]
            for (p1, p2) in edges:
                # Check if edge is sloping (x coordinates differ)
                if abs(p1[0] - p2[0]) > 5:
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    # Perpendicular vector (rotate 90 deg)
                    perp_x = -dy
                    perp_y = dx
                    length = math.hypot(perp_x, perp_y)
                    if length > 0:
                        perp_x /= length
                        perp_y /= length
                    # Flip colors: top edge (downward) gets dark, bottom edge (upward) gets light
                    if p2[1] > p1[1]:   # downward sloping (top edge) -> shadow
                        color = (30, 30, 30)        # dark gray
                    else:                # upward sloping (bottom edge) -> highlight
                        color = (210, 210, 210)    # light gray
                    # Draw a thick line (5 lines) to simulate bevel
                    for d in range(-2, 3):
                        ox = -perp_x * d * 0.5
                        oy = -perp_y * d * 0.5
                        start = (p1[0] + ox, p1[1] + oy)
                        end = (p2[0] + ox, p2[1] + oy)
                        pygame.draw.line(screen, color, start, end, 1)