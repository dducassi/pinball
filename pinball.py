### WIZARD PINBALL ###

import pygame
import sys
import random
import time
import math
from settings import Settings
from ball import Ball
from obstacles import Obstacle
from blocks import Block
from flipper import Flipper


import os
script_dir = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    # Running as EXE - use temporary bundle directory
    base_dir = sys._MEIPASS
else:
    # Running as script - use normal script directory
    base_dir = script_dir



class Pinball:
    
    

    def __init__(self):
        # Initialize Pygame and settings
        pygame.init()

        self.settings = Settings()

        # Set up the game window
        self.screen = pygame.display.set_mode((self.settings.screen_width, 
            self.settings.screen_height))
        self.bg = pygame.image.load(os.path.join(
                                        base_dir, 'wizard.png'))
        pygame.display.set_caption('Wizard Pinball')
        
        # Initialize the ball and flippers
        self.b = Ball(self)
        self.fl = Flipper(2/7 * self.settings.screen_width, self.settings.screen_height - 9/140 * self.settings.screen_height, self.settings.f_length, 0.6, True)
        self.fr = Flipper(5/7 * self.settings.screen_width, self.settings.screen_height - 9/140 * self.settings.screen_height, self.settings.f_length, -0.6, False)
    
        
        # Generate bumpers (obs) and block elements
        self.obs = []
        self.blocks = [] 
        self.flippers = [self.fl, self.fr]
        self.gen_obs()
        self.gen_blocks()

    def gen_obs(self):
        x = self.settings.screen_width / 2
        y = (self.settings.screen_height) / 5
        c = self.settings.blu
        self.obs.append(Obstacle(x, y, c))
        x = 0
        y = 0
        c = self.settings.blu
        self.obs.append(Obstacle(x, y, c))
        x = self.settings.screen_width
        y = 0
        c = self.settings.blu
        self.obs.append(Obstacle(x, y, c))
        self.draw_obs()
        x = .22 * self.settings.orad
        y = 6/7 * (self.settings.screen_height)
        c = self.settings.blu
        self.obs.append(Obstacle(x, y, c))
        x = self.settings.screen_width - .22 * self.settings.orad
        y = 6/7 * (self.settings.screen_height)
        c = self.settings.blu
        self.obs.append(Obstacle(x, y, c))




    def draw_obs(self):
        for ob in self.obs:
            pygame.draw.circle(self.screen, ob.c, (ob.x, ob.y), self.settings.orad)
    
    def gen_blocks(self):

        # Left lower block
        x1 = 0
        y1 = self.settings.screen_height
        x2 = 0
        y2 = self.settings.screen_height - (3/14) * self.settings.screen_height
        x3 = (2/7) * self.settings.screen_width
        y3 = self.settings.screen_height - (1/14) * self.settings.screen_height
        x4 = (2/7) * self.settings.screen_width
        y4 = self.settings.screen_height
        c = self.settings.gry
        self.blocks.append(Block(x1, y1, x2, y2, x3, y3, x4, y4, c))
        #[(0, self.settings.screen_height), (100, self.settings.screen_height), (0, self.settings.screen_height - 120), (100, self.settings.screen_height - 20)]

        # Right lower block
        x1 = self.settings.screen_width
        y1 = self.settings.screen_height
        x2 = self.settings.screen_width
        y2 = self.settings.screen_height - (3/14) * self.settings.screen_height
        x3 = self.settings.screen_width - (2/7) * self.settings.screen_width 
        y3 = self.settings.screen_height - (1/14) * self.settings.screen_height
        x4 = self.settings.screen_width - (2/7) * self.settings.screen_width 
        y4 = self.settings.screen_height

        c = self.settings.gry
        self.blocks.append(Block(x1, y1, x2, y2, x3, y3, x4, y4, c))

    def draw_blocks(self):
        for block in self.blocks:
            pygame.draw.polygon(self.screen, block.c, [(block.x1, block.y1), (block.x2, block.y2), (block.x3, block.y3), (block.x4, block.y4)])

    def increment_score(self):
        self.score += self.settings.pph # Score goes up


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

        # Get delta
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
        

    def ball_physics(self):
        
        # Move flippers for fresh collision state
        self.fl.update()
        self.fr.update()

        next_x = self.b.x + self.b.dx
        next_y = self.b.y + self.b.dy

        

        # Use local vars for ball position and velocity
        ball_x = self.b.x
        ball_y = self.b.y
        ball_dx = self.b.dx
        ball_dy = self.b.dy
        ball_radius = self.settings.br
        position_corrected = False

        # Process each flipper
        for f in self.flippers:
            pivot_x, pivot_y = f.pivot
            angle = f.angle
            length = f.length
            width = f.width  # Rectangle thickness
            
            
            # Transform next ball position into flipper's local space
            dx = next_x - pivot_x
            dy = next_y - pivot_y
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            # Transform both current and next ball positions into flipper's local space
            dx = ball_x - pivot_x
            dy = ball_y - pivot_y
            local_x1 = dx * cos_a + dy * sin_a
            local_y1 = -dx * sin_a + dy * cos_a

            dx_next = next_x - pivot_x
            dy_next = next_y - pivot_y
            local_x2 = dx_next * cos_a + dy_next * sin_a
            local_y2 = -dx_next * sin_a + dy_next * cos_a

            # Define rectangle bounds (ensure left < right)
            rect_left = min(0, length)
            rect_right = max(0, length)
            rect_top = -width / 2
            rect_bottom = width / 2

            # Find closest point on rectangle to ball
            closest_x = max(rect_left, min(local_x2, rect_right))
            closest_y = max(rect_top, min(local_y2, rect_bottom))

            # Distance from ball to closest point
            dist_x = local_x2 - closest_x
            dist_y = local_y2 - closest_y
            distance = math.hypot(dist_x, dist_y)

            # Check swept collision with flipper rectangle
            hit, contact = self.swept_circle_vs_aabb(
                (local_x1, local_y1),
                (local_x2, local_y2),
                ball_radius,
                rect_left, rect_right,
                rect_top, rect_bottom)
            if hit:
                # Move ball to contact point (in local space)
                local_contact_x, local_contact_y = contact

                # Transform contact point back to world space
                world_dx = local_contact_x * cos_a - local_contact_y * sin_a
                world_dy = local_contact_x * sin_a + local_contact_y * cos_a
                ball_x = pivot_x + world_dx
                ball_y = pivot_y + world_dy

                # Compute local normal
                cx = max(rect_left, min(local_contact_x, rect_right))
                cy = max(rect_top, min(local_contact_y, rect_bottom))
                nx_local = local_contact_x - cx
                ny_local = local_contact_y - cy
                length = math.hypot(nx_local, ny_local) or 1.0
                nx_local /= length
                ny_local /= length

                # Transform normal to world space
                nx = nx_local * cos_a - ny_local * sin_a
                ny = nx_local * sin_a + ny_local * cos_a

                # Reflect velocity
                dot = ball_dx * nx + ball_dy * ny
                if dot < 0:
                    ball_dx -= 2 * dot * nx
                    ball_dy -= 2 * dot * ny

                    if f.active:
                        boost = self.settings.flip_force
                        ball_dx += nx * boost
                        ball_dy += ny * boost
                    else:
                        bounce = self.settings.deadf_bounce
                        ball_dx *= bounce
                        ball_dy *= bounce

                    position_corrected = True
                    print(f"[Swept CCD] Flipper collision at ({ball_x:.2f},{ball_y:.2f}), velocity ({ball_dx:.2f},{ball_dy:.2f})")
                break

            # Fallback: static overlap resolution (e.g., flipper moved into ball)
            if distance < ball_radius:
                # Compute contact normal (local space)
                if distance > 1e-6:
                    normal_local = (dist_x / distance, dist_y / distance)
                else:
                    # Push away from flipper rectangle center
                    rect_cx = (rect_left + rect_right) / 2
                    rect_cy = (rect_top + rect_bottom) / 2
                    fallback_dx = local_x2 - rect_cx
                    fallback_dy = local_y2 - rect_cy
                    fallback_length = math.hypot(fallback_dx, fallback_dy) or 1.0
                    normal_local = (fallback_dx / fallback_length, fallback_dy / fallback_length)

                # Transform normal to world space
                nx = normal_local[0] * cos_a - normal_local[1] * sin_a
                ny = normal_local[0] * sin_a + normal_local[1] * cos_a

                # Push ball out of flipper
                overlap = ball_radius - distance
                ball_x += nx * overlap
                ball_y += ny * overlap

                # Reflect velocity
                dot_product = ball_dx * nx + ball_dy * ny
                if dot_product < 0:
                    ball_dx -= 2 * dot_product * nx
                    ball_dy -= 2 * dot_product * ny

                    # Add flipper force if active
                    if f.active:
                        boost = self.settings.flip_force
                        ball_dx += nx * boost
                        ball_dy += ny * boost
                    else:
                        bounce = self.settings.deadf_bounce
                        ball_dx *= bounce
                        ball_dy *= bounce

                    # Enforce minimum velocity
                    min_vel = 0.5
                    if abs(ball_dx) < min_vel and abs(ball_dy) < min_vel:
                        sign_x = 1 if ball_dx >= 0 else -1
                        sign_y = 1 if ball_dy >= 0 else -1
                        ball_dx = sign_x * min_vel
                        ball_dy = sign_y * min_vel

                position_corrected = True
                print(f"[Fallback] Flipper overlap at ({ball_x:.2f},{ball_y:.2f}), velocity ({ball_dx:.2f},{ball_dy:.2f})")
                time.sleep(2)




        # --- Block collisions ---
        for block in self.blocks:
        
            # Extract points for convenience
            x1, y1 = block.x1, block.y1
            x2, y2 = block.x2, block.y2
            x3, y3 = block.x3, block.y3
            x4, y4 = block.x4, block.y4
            bounce = self.settings.block_bounce
            ball_diag = ball_radius * 1.415  # diagonal radius approx sqrt(2)*radius

            if block is self.blocks[0]:
                # Left lower block slope line (x2,y2) to (x3,y3)
                m = (y3 - y2) / (x3 - x2)
                c = y2 - m * x2

                line_y_at_ball = m * ball_x + c

                # Check collision with slope
                if ball_x <= x3 + ball_radius:
                    if y2 - ball_radius <= ball_y <= y3 + ball_radius:
                        if ball_y + ball_diag >= line_y_at_ball:
                            ball_y = line_y_at_ball - ball_diag
                            if ball_dx <= 0:
                                ball_dy, ball_dx = -abs(ball_dx) * bounce, ball_dy * bounce
                            else:
                                ball_dy, ball_dx = -ball_dx * bounce, ball_dy * bounce
                            position_corrected = True
                            print(f"Block bounce, left slope. Velocity:{ball_dy, ball_dx} ")

                # Left vertical wall (marked by x4)
                if ball_x <= x4 + ball_radius:
                    if ball_y >= y3:  # y3 is upper y of vertical wall
                        if ball_dx < 0:
                            ball_x = x4 + ball_radius
                            ball_dx = -ball_dx * bounce
                            position_corrected = True
                        print(f"Block bounce, left wall. Velocity:{ball_dy, ball_dx}")

            elif block is self.blocks[1]:
                # Right lower block slope line (x2,y2) to (x3,y3)
                m = (y3 - y2) / (x3 - x2)
                c = y2 - m * x2

                line_y_at_ball = m * ball_x + c

                # Check collision with slope
                if ball_x >= x3 - ball_radius:
                    if y2 - ball_radius <= ball_y <= y3 + ball_radius:
                        if ball_y + ball_diag >= line_y_at_ball:
                            ball_y = line_y_at_ball - ball_diag
                            if ball_dx >= 0:
                                ball_dy, ball_dx = ball_dx * bounce, -ball_dy * bounce
                            else:
                                if ball_dy <= 0:
                                    ball_dy, ball_dx = -ball_dx * bounce, ball_dy * bounce
                                else:
                                    ball_dy, ball_dx = -ball_dx * bounce, -ball_dy * bounce
                            position_corrected = True
                            print(f"Block bounce, right slope. Velocity:{ball_dy, ball_dx}")

                # Right vertical wall (marked by x4)
                if ball_x >= x4 - ball_radius:
                    if ball_y >= y3:
                        ball_x = self.settings.screen_width - ball_radius
                        if ball_dx > 0:
                            ball_x = x4 - ball_radius
                            ball_dx = -ball_dx * bounce
                            position_corrected = True
                        position_corrected = True
                        print(f"Block bounce, right wall. Velocity:{ball_dy, ball_dx}")

        # --- Obstacle collisions ---
        for obs in self.obs:
            ox, oy = obs.x, obs.y
            orad = self.settings.orad

            dx = ball_x - ox
            dy = ball_y - oy
            dist = math.sqrt(dx*dx + dy*dy)

            if dist < ball_radius + orad:
                # Correct ball position outside the obstacle
                epsilon = 0.5
                ball_x = ox + (dx / dist) * (ball_radius + orad + epsilon)
                ball_y = oy + (dy / dist) * (ball_radius + orad + epsilon)

                # Bounce the ball off the obstacle surface
                nx = dx / dist
                ny = dy / dist
                dot = ball_dx * nx + ball_dy * ny

                if dot < -1e-3:
                    ball_dx = ball_dx - 2 * dot * nx
                    ball_dy = ball_dy - 2 * dot * ny

                    ball_dx *= self.settings.obs_bounce
                    ball_dy *= self.settings.obs_bounce

                self.increment_score() 
                if obs.c == self.settings.red:
                    obs.c = self.settings.blu
                elif obs.c == self.settings.blu:
                    obs.c = self.settings.ylw
                elif obs.c == self.settings.ylw:
                    obs.c = self.settings.red
                print(f"Hit obstacle at {ox},{oy}, bounce velocity ({ball_dx},{ball_dy})")

        revised_next_y = ball_y + ball_dy
        if abs(revised_next_y - ball_y) > 50: # Sanity check
            print("⚠️ SUSPICIOUS movement detected!")
            print(f"Before: y={self.b.y}, dy={self.b.dy}")
            print(f"After: y={ball_y}, dy={ball_dy}")

        # Update the ball's position and velocity once after all collisions
        self.b.x = ball_x
        self.b.y = ball_y
        self.b.dx = ball_dx
        self.b.dy = ball_dy

        print(f"FINAL ball pos: ({self.b.x}, {self.b.y}), velocity: ({self.b.dx}, {self.b.dy})")
        

        # Reset ball if out of bounds or collision condition met
        if self.b.check_collision():
            time.sleep(1.5)
            self.b.reset()
            self.score = 0  # Reset score on game over
        
        

        # Move the ball according to current velocity
        self.b.move() # Split off gravity and speed clamping, ideally


        

    


    def run_game(self):
        running = False  # Initially game is not running
        paused = False   # Initially game is not paused
        self.score = 0
        
        show_start_text = True  # Display "Press S to start" initially

        # Main game loop
        while True:
            self.screen.blit(self.bg, (0, 0))  # Paint background

            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:  # Start or resume the game
                        if not running:
                            running = True
                            self.b.reset()
                            self.score = 0
                            show_start_text = False
                    if event.key == pygame.K_r:
                        self.b.reset()
                    if event.key == pygame.K_LEFT:
                        self.fl.active = True
                        self.fl.activate()
                    if event.key == pygame.K_RIGHT:
                        self.fr.active = True
                        self.fr.activate()
                        
                    elif event.key == pygame.K_p:  # Pause the game
                        paused = not paused
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.fl.active = False
                        self.fl.deactivate()
                    if event.key == pygame.K_RIGHT:
                        self.fr.active = False
                        self.fr.deactivate()

            

            # Display start text if game not running
            if not running and show_start_text:
                f = pygame.font.Font(None, 36)
                start_text = f.render("Press S to start", True, self.settings.wht)
                self.screen.blit(start_text, ((self.settings.screen_width - start_text.get_width()) // 2, (self.settings.screen_height - start_text.get_height()) // 2))
            elif running and paused:
                f = pygame.font.Font(None, 36)
                pause_text = f.render("Paused", True, self.settings.wht)
                self.screen.blit(pause_text, ((self.settings.screen_width - pause_text.get_width()) // 2, (self.settings.screen_height - pause_text.get_height()) // 2))
                
               

            # If game is running, not paused
            if running and not paused:

                for i in range(self.settings.phys_runs):
                    self.ball_physics()
                
                
                
            # Draw game elements

            
            self.fl.draw(self.screen)
            self.fr.draw(self.screen)
        
            self.b.draw_ball()

            self.draw_obs()
            self.draw_blocks()
           
            


            # Display the current score
            f = pygame.font.Font(None, 36)
            score_text = f.render(f'Score: {self.score}', True, self.settings.wht)
            self.screen.blit(score_text, (20, 20))


            # Update the display
            pygame.display.flip()


            # Control the frame rate
            pygame.time.Clock().tick(30)

if __name__ == '__main__':
    # Make a game instance and run the game.
    pb = Pinball()
    pb.run_game()
