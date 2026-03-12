# Class for blocks

import pygame
import math

class Block:
    def __init__(self, vertices, color, bounce=0.8):
        """
        vertices: list of (x, y) tuples defining a convex polygon in order.
        color: RGB tuple or color constant.
        bounce: restitution coefficient.
        """
        self.vertices = vertices
        self.c = color
        self.bounce = bounce

        # Build edges from vertices (works for any polygon)
        self.edges = []
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1) % n]
            self.edges.append((x1, y1, x2, y2))

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
        Check collision between this block and the ball.
        Returns (new_ball_x, new_ball_y, new_ball_dx, new_ball_dy, hit)
        """
        best_penetration = 0
        best_nx = best_ny = 0
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
                    if dist > 0:
                        best_nx = dx / dist
                        best_ny = dy / dist
                    else:
                        # Ball exactly on edge – compute a normal perpendicular to the edge
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
                    if dist > 0:
                        best_nx = dx / dist
                        best_ny = dy / dist
                    else:
                        best_nx, best_ny = 0, 1
                    hit = True

        if not hit:
            return ball_x, ball_y, ball_dx, ball_dy, False

        # Push ball out
        ball_x += best_nx * best_penetration
        ball_y += best_ny * best_penetration

        # Reflect velocity
        dot = ball_dx * best_nx + ball_dy * best_ny
        if dot < 0:
            ball_dx -= 2 * dot * best_nx
            ball_dy -= 2 * dot * best_ny
            ball_dx *= self.bounce
            ball_dy *= self.bounce

        # Minimum velocity (original behavior)
        speed = math.hypot(ball_dx, ball_dy)
        if speed < 2.0:
            scale = 2.0 / speed
            ball_dx *= scale
            ball_dy *= scale

        return ball_x, ball_y, ball_dx, ball_dy, True