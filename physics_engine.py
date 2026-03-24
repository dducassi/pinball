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

        # Update flipper angles
        for f in self.flippers:
            f.update()

        # Local copies for readability
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

        RESTING_THRESHOLD = 0.3
        # --- Flipper collisions ---
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
                push_dist = f.width / 2
                ball_x += nx * push_dist
                ball_y += ny * push_dist

               # Compute contact point velocity (varies with distance from pivot)
                contact_dist = local_contact_x
                contact_speed = f.angular_vel * contact_dist
                contact_vx = -math.sin(angle) * contact_speed
                contact_vy = math.cos(angle) * contact_speed

               # Unified restitution‑based reflection
                restitution = settings.restitution
                v_rel_x = ball_dx - contact_vx
                v_rel_y = ball_dy - contact_vy
                v_rel_n = v_rel_x * nx + v_rel_y * ny
                if v_rel_n < 0:  # moving into the surface
                    v_rel_t_x = v_rel_x - v_rel_n * nx
                    v_rel_t_y = v_rel_y - v_rel_n * ny
                    v_rel_n_after = -restitution * v_rel_n
                    ball_dx = contact_vx + v_rel_n_after * nx + v_rel_t_x
                    ball_dy = contact_vy + v_rel_n_after * ny + v_rel_t_y

                # Resting detection
                rel_vn = (ball_dx - contact_vx) * nx + (ball_dy - contact_vy) * ny
                if abs(rel_vn) < RESTING_THRESHOLD:
                    vn_target = contact_vx * nx + contact_vy * ny
                    current_vn = ball_dx * nx + ball_dy * ny
                    ball_dx += (vn_target - current_vn) * nx
                    ball_dy += (vn_target - current_vn) * ny

                # Break after handling a hit
                #print(f"[Swept CCD] Flipper collision at ({ball_x:.2f},{ball_y:.2f}), velocity ({ball_dx:.2f},{ball_dy:.2f})")

                ball.resting = False

                
                break

         

        # --- Blocks collisions ---
        for block in self.blocks:
            new_x, new_y, new_dx, new_dy, hit = block.collide(
                ball_x, ball_y, ball_dx, ball_dy,
                ball_radius
            )
            if hit:
                ball_x, ball_y, ball_dx, ball_dy = new_x, new_y, new_dx, new_dy
                ball.resting = False

                # Post block hit notification
                if abs(ball_dx) > 2 or abs(ball_dy) > 2:
                    if not ball.resting:
                        if not ball.trapped:
                            self.notification_center.post_notification('block_hit', block)


        # --- Bumpers collisions ---
        for bumper in self.bumpers:
            bump_x, bump_y = bumper.x, bumper.y
            bump_rad = bumper.radius

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

        # --- Wall collisions (playfield boundaries) ---
        # Left wall
        if ball_x - ball_radius - self.settings.lane_wall_thickness < 0:
            ball_x = ball_radius + self.settings.lane_wall_thickness
            if ball_dx < 0:
                ball_dx = -ball_dx * settings.restitution
        # Top wall (including top margin)
        if ball_y - ball_radius - self.settings.lane_wall_thickness < settings.top_margin:
            ball_y = settings.top_margin + ball_radius + self.settings.lane_wall_thickness
            if ball_dy < 0:
                ball_dy = -ball_dy * settings.restitution

        # Bottom out-of-bounds
        if ball_y + ball_radius > settings.screen_height * 1.5:
            self.ball.lost = True   # ball lost

        # Apply final ball state
        ball.x = ball_x
        ball.y = ball_y
        ball.dx = ball_dx
        ball.dy = ball_dy
      
        # Apply final ball state
        ball.x = ball_x
        ball.y = ball_y
        ball.dx = ball_dx
        ball.dy = ball_dy


        # --- Trapped detection (ball between flipper and block) ---
        TRAP_SPEED_THRESH = 0.07
        TRAP_DIST_EPSILON = 1.0  # extra allowance beyond ball_radius

        if not ball.trapped and math.hypot(ball_dx, ball_dy) < TRAP_SPEED_THRESH:
            # Check if ball is near any flipper
            near_flipper = False
            for f in self.flippers:
                # Simplified distance to flipper (use closest point on rectangle)
                pivot_x, pivot_y = f.pivot
                angle = f.angle
                length = f.length
                width = f.width
                dx = ball_x - pivot_x
                dy = ball_y - pivot_y
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)
                local_x = dx * cos_a + dy * sin_a
                local_y = -dx * sin_a + dy * cos_a
                rect_left = min(0, length)
                rect_right = max(0, length)
                rect_top = -width / 2
                rect_bottom = width / 2
                closest_x = max(rect_left, min(local_x, rect_right))
                closest_y = max(rect_top, min(local_y, rect_bottom))
                dist = math.hypot(local_x - closest_x, local_y - closest_y)
                if dist < ball_radius + TRAP_DIST_EPSILON:
                    near_flipper = True
                    break

            if near_flipper:
                # Check if ball is near any block
                near_block = False
                for block in self.blocks:
                    # Use block's edges to find closest distance
                    for (x1, y1, x2, y2) in block.edges:
                        cx, cy = block._closest_point_on_segment(ball_x, ball_y, x1, y1, x2, y2)
                        dist = math.hypot(ball_x - cx, ball_y - cy)
                        if dist < ball_radius + TRAP_DIST_EPSILON:
                            near_block = True
                            break
                    if near_block:
                        break

                if near_block:
                    # Trapped!
                    ball.trapped = True
                    ball.dx = 0
                    ball.dy = 0

                # --- Resting detection (ball at rest on any surface) ---
            REST_SPEED_THRESH = 0.1
            if not ball.resting and math.hypot(ball_dx, ball_dy) < REST_SPEED_THRESH:
                # Check if ball is near any flipper
                near_surface = False
                for f in self.flippers:
                    # Simplified distance to flipper
                    pivot_x, pivot_y = f.pivot
                    angle = f.angle
                    length = f.length
                    width = f.width
                    dx = ball_x - pivot_x
                    dy = ball_y - pivot_y
                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)
                    local_x = dx * cos_a + dy * sin_a
                    local_y = -dx * sin_a + dy * cos_a
                    rect_left = min(0, length)
                    rect_right = max(0, length)
                    rect_top = -width / 2
                    rect_bottom = width / 2
                    closest_x = max(rect_left, min(local_x, rect_right))
                    closest_y = max(rect_top, min(local_y, rect_bottom))
                    dist = math.hypot(local_x - closest_x, local_y - closest_y)
                    if dist < ball_radius + 5:   # 5 pixel tolerance
                        near_surface = True
                        break
                if not near_surface:
                    # Check blocks
                    for block in self.blocks:
                        min_dist = float('inf')
                        for (x1, y1, x2, y2) in block.edges:
                            cx, cy = block._closest_point_on_segment(ball_x, ball_y, x1, y1, x2, y2)
                            dist = math.hypot(ball_x - cx, ball_y - cy)
                            if dist < min_dist:
                                min_dist = dist
                        if min_dist < ball_radius + 5:
                            near_surface = True
                            break
                    if not near_surface:
                        # Check left wall (x=0)
                        if ball_x - ball_radius < 5:
                            near_surface = True
                        # Check top wall (y=top_margin)
                        if ball_y - ball_radius < self.settings.top_margin + 5:
                            near_surface = True

                if near_surface:
                    ball.resting = True
                    ball_dx = 0
                    ball_dy = 0

            

        # Original ball.move() call (gravity, friction, walls)
        ball.move()
