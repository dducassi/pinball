# Class for blocks
# blocks.py
import pygame
import math

class Block:
    def __init__(self, vertices, color, restitution, image=None):
        self.vertices = vertices
        self.c = color
        self.restitution = restitution
        self.image = None
        self.rect = None

        if image:
            # Compute bounding box
            xs = [v[0] for v in vertices]
            ys = [v[1] for v in vertices]
            w = max(xs) - min(xs)
            h = max(ys) - min(ys)
            # Scale image to fit bounding box
            self.image = pygame.transform.scale(image, (int(w), int(h)))
            self.rect = pygame.Rect(min(xs), min(ys), w, h)

        # Build edges for collision
        self.edges = []
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1) % n]
            self.edges.append((x1, y1, x2, y2))

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.polygon(screen, self.c, self.vertices)

    def _closest_point_on_segment(self, px, py, x1, y1, x2, y2):
        """Return closest point on segment (x1,y1)-(x2,y2) to (px,py)."""
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx*dx + dy*dy
        if length_sq == 0:
            return x1, y1
        t = ((px - x1)*dx + (py - y1)*dy) / length_sq
        t = max(0, min(1, t))
        return x1 + t*dx, y1 + t*dy

    def collide(self, ball_x, ball_y, ball_dx, ball_dy, ball_radius):
        """
        Check collision with block and resolve. 
        Returns (new_ball_x, new_ball_y, new_ball_dx, new_ball_dy, hit).
        """
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

        # Position correction: place ball exactly at distance ball_radius from the closest point
        ball_x = best_cx + best_nx * ball_radius
        ball_y = best_cy + best_ny * ball_radius

        # Unified restitution‑based response (block is static, so block velocity = 0)
        restitution = self.restitution
        vn = ball_dx * best_nx + ball_dy * best_ny
        vt_x = ball_dx - vn * best_nx
        vt_y = ball_dy - vn * best_ny


        # Resting threshold to avoid micro‑bounces
        RESTING_THRESHOLD = 0.3
        if vn < 0:  # moving into the surface
            if -vn < RESTING_THRESHOLD:
                vn = 0  # become resting
            else:
                vn = -vn * self.restitution   # normal bounce
        # If moving away, leave vn unchanged

        # No friction for now (keep tangential velocity as is)
        # vt_x and vt_y remain unchanged

        # Recompose velocity
        ball_dx = vt_x + vn * best_nx
        ball_dy = vt_y + vn * best_ny

        return ball_x, ball_y, ball_dx, ball_dy, True