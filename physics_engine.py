import math

class PhysicsEngine:
    def __init__(self, ball, flippers, bumpers, blocks, settings, notification_center):
        self.ball = ball
        self.flippers = flippers
        self.bumpers = bumpers
        self.blocks = blocks
        self.settings = settings
        self.notification_center = notification_center

    def swept_circle_vs_aabb(self, p0, p1, radius, rect_left, rect_right, rect_top, rect_bottom):
        """
        Checks if a circle of given radius moving from p0 to p1 collides with AABB defined by rect_*.
        Returns (hit, contact_point)
        """
        # Expand rectangle by radius
        r_left = rect_left - radius
        r_right = rect_right + radius
        r_top = rect_top - radius
        r_bottom = rect_bottom + radius

        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]

        t_entry = 0.0
        t_exit = 1.0

        for axis in range(2):
            if axis == 0:
                p = p0[0]
                d = dx
                min_b = r_left
                max_b = r_right
            else:
                p = p0[1]
                d = dy
                min_b = r_top
                max_b = r_bottom

            if abs(d) < 1e-8:
                if p < min_b or p > max_b:
                    return False, None
            else:
                t1 = (min_b - p) / d
                t2 = (max_b - p) / d
                t_min = min(t1, t2)
                t_max = max(t1, t2)
                t_entry = max(t_entry, t_min)
                t_exit = min(t_exit, t_max)
                if t_entry > t_exit:
                    return False, None

        contact_x = p0[0] + dx * t_entry
        contact_y = p0[1] + dy * t_entry
        return True, (contact_x, contact_y)

    def update(self):
        """Run one physics step and send notifications."""

        # Update flipper angles (original first lines of ball_physics)
        for f in self.flippers:
            f.update()

        # Local copies for readability (same as original)
        ball = self.ball
        settings = self.settings
        ball_radius = settings.br

        # Original: next_x = self.b.x + self.b.dx, etc.
        next_x = ball.x + ball.dx
        next_y = ball.y + ball.dy

        ball_x = ball.x
        ball_y = ball.y
        ball_dx = ball.dx
        ball_dy = ball.dy

        # --- Flipper collisions (exact copy from original ball_physics) ---
        for f in self.flippers:
            pivot_x, pivot_y = f.pivot
            angle = f.angle
            length = f.length
            width = f.width

            # Transform both current and next ball positions into flipper's local space
            dx = ball_x - pivot_x
            dy = ball_y - pivot_y
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            local_x1 = dx * cos_a + dy * sin_a
            local_y1 = -dx * sin_a + dy * cos_a

            dx_next = next_x - pivot_x
            dy_next = next_y - pivot_y
            local_x2 = dx_next * cos_a + dy_next * sin_a
            local_y2 = -dx_next * sin_a + dy_next * cos_a

            rect_left = min(0, length)
            rect_right = max(0, length)
            rect_top = -width / 2
            rect_bottom = width / 2

            # Swept collision check
            hit, contact = self.swept_circle_vs_aabb(
                (local_x1, local_y1),
                (local_x2, local_y2),
                ball_radius,
                rect_left, rect_right, rect_top, rect_bottom
            )

            if hit:
                # Move ball to contact point
                local_contact_x, local_contact_y = contact
                world_dx = local_contact_x * cos_a - local_contact_y * sin_a
                world_dy = local_contact_x * sin_a + local_contact_y * cos_a
                ball_x = pivot_x + world_dx
                ball_y = pivot_y + world_dy

                # Compute local normal
                cx = max(rect_left, min(local_contact_x, rect_right))
                cy = max(rect_top, min(local_contact_y, rect_bottom))
                nx_local = local_contact_x - cx
                ny_local = local_contact_y - cy

                if abs(nx_local) < 1e-6 and abs(ny_local) < 1e-6:
                    eps = 1e-4
                    if abs(local_contact_y - rect_top) < eps:
                        nx_local, ny_local = 0, -1
                    elif abs(local_contact_y - rect_bottom) < eps:
                        nx_local, ny_local = 0, 1
                    elif abs(local_contact_x - rect_left) < eps:
                        nx_local, ny_local = -1, 0
                    elif abs(local_contact_x - rect_right) < eps:
                        nx_local, ny_local = 1, 0
                    else:
                        nx_local, ny_local = 0, -1

                norm_len = math.hypot(nx_local, ny_local) or 1.0
                nx_local /= norm_len
                ny_local /= norm_len

                # Transform normal to world space
                nx = nx_local * cos_a - ny_local * sin_a
                ny = nx_local * sin_a + ny_local * cos_a

                # Push ball out
                push_dist = 2.0
                ball_x += nx * push_dist
                ball_y += ny * push_dist

                # Flipper tip velocity
                tip_speed = f.angular_vel * length
                tip_vx = -math.sin(angle) * tip_speed
                tip_vy = math.cos(angle) * tip_speed

                # Reflect velocity
                dot = ball_dx * nx + ball_dy * ny
                if dot < 0:
                    ball_dx -= 2 * dot * nx
                    ball_dy -= 2 * dot * ny

                    if f.active:
                        
                        ball_dx += tip_vx * (settings.phys_runs / 2)
                        ball_dy += tip_vy * (settings.phys_runs / 2)
                    else:
                        bounce = settings.deadf_bounce
                        ball_dx *= bounce
                        ball_dy *= bounce

                    # Minimum velocity
                    # speed = math.hypot(ball_dx, ball_dy)
                    # if speed < 2.0:
                        #scale = 2.0 / speed
                        #ball_dx *= scale
                        #ball_dy *= scale

                # Break after handling a hit
                print(f"[Swept CCD] Flipper collision at ({ball_x:.2f},{ball_y:.2f}), velocity ({ball_dx:.2f},{ball_dy:.2f})")
                
                break

            else:
                # Fallback: static overlap resolution
                closest_x = max(rect_left, min(local_x2, rect_right))
                closest_y = max(rect_top, min(local_y2, rect_bottom))
                dist_x = local_x2 - closest_x
                dist_y = local_y2 - closest_y
                distance = math.hypot(dist_x, dist_y)

                if distance < ball_radius:
                    if distance > 1e-6:
                        normal_local = (dist_x / distance, dist_y / distance)
                    else:
                        rect_cx = (rect_left + rect_right) / 2
                        rect_cy = (rect_top + rect_bottom) / 2
                        fallback_dx = local_x2 - rect_cx
                        fallback_dy = local_y2 - rect_cy
                        fb_len = math.hypot(fallback_dx, fallback_dy) or 1.0
                        normal_local = (fallback_dx / fb_len, fallback_dy / fb_len)

                    nx = normal_local[0] * cos_a - normal_local[1] * sin_a
                    ny = normal_local[0] * sin_a + normal_local[1] * cos_a

                    overlap = ball_radius - distance + 1.0
                    ball_x += nx * overlap
                    ball_y += ny * overlap

                    tip_speed = f.angular_vel * length
                    tip_vx = -math.sin(angle) * tip_speed
                    tip_vy = math.cos(angle) * tip_speed

                    dot = ball_dx * nx + ball_dy * ny
                    if dot < 0:
                        ball_dx -= 2 * dot * nx
                        ball_dy -= 2 * dot * ny

                    if f.active:
                        ball_dx += tip_vx * (settings.phys_runs / 2)
                        ball_dy += tip_vy * (settings.phys_runs / 2)
                    else:
                        bounce = settings.deadf_bounce
                        ball_dx *= bounce
                        ball_dy *= bounce

                    speed = math.hypot(ball_dx, ball_dy)

                    # Minimum velocity
                    # speed = math.hypot(ball_dx, ball_dy)
                    # if speed < 2.0:
                        #scale = 2.0 / speed
                        #ball_dx *= scale
                        #ball_dy *= scale

                   

        # --- Blocks collisions ---
        for block in self.blocks:
            new_x, new_y, new_dx, new_dy, hit = block.collide(
                ball_x, ball_y, ball_dx, ball_dy,
                ball_radius
            )
            if hit:
                ball_x, ball_y, ball_dx, ball_dy = new_x, new_y, new_dx, new_dy
                break   # only handle one block collision per step (original behavior)


        # --- Bumpers collisions ---
        for bumper in self.bumpers:
            bump_x, bump_y = bumper.x, bumper.y
            bump_rad = settings.bump_rad

            dx = ball_x - bump_x
            dy = ball_y - bump_y
            dist = math.hypot(dx, dy)

            if dist < ball_radius + bump_rad:
                if dist > 0:
                    ball_x = bump_x + (dx / dist) * (ball_radius + bump_rad + 0.5)
                    ball_y = bump_y + (dy / dist) * (ball_radius + bump_rad + 0.5)
                else:
                    ball_x = bump_x + (ball_radius + bump_rad + 0.5)
                    ball_y = bump_y

                nx = dx / dist if dist > 0 else 1
                ny = dy / dist if dist > 0 else 0
                dot = ball_dx * nx + ball_dy * ny
                if dot < -1e-3:
                    ball_dx -= 2 * dot * nx
                    ball_dy -= 2 * dot * ny
                    ball_dx *= settings.bump_bounce
                    ball_dy *= settings.bump_bounce

                # Record notifications for scoring and color change
                self.notification_center.post_notification('bumper_hit', bumper)

        # Apply final ball state
        ball.x = ball_x
        ball.y = ball_y
        ball.dx = ball_dx
        ball.dy = ball_dy

        # Original ball.move() call (gravity, friction, walls)
        ball.move()
