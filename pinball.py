
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
        

    def ball_physics(self):
        # Move flippers
        self.fl.update()
        self.fr.update()

        old_x, old_y = self.b.x, self.b.y

        # Move the ball according to current velocity
        self.b.move()

        # Use local vars for ball position and velocity
        ball_x = self.b.x
        ball_y = self.b.y
        ball_dx = self.b.dx
        ball_dy = self.b.dy
        ball_radius = self.settings.br

        position_corrected = False

        # --- Flipper collisions ---
        for f in self.flippers:
            pivot_x, pivot_y = f.pivot
            angle = f.angle
            length = f.length

            if f == self.fl and angle < -0.5:
                f.active = False
            elif f == self.fr and angle > 0.5:
                f.active = False

            end_x, end_y = f.get_end_pos()

            # Avoid division by zero for slope calculation
            if abs(end_x - pivot_x) > 1e-10:
                flipper_slope = (end_y - pivot_y) / (end_x - pivot_x)
                flipper_intercept = pivot_y - flipper_slope * pivot_x

                flipper_vec_x = end_x - pivot_x
                flipper_vec_y = end_y - pivot_y
                to_ball_x = ball_x - pivot_x
                to_ball_y = ball_y - pivot_y

                projection = (to_ball_x * flipper_vec_x + to_ball_y * flipper_vec_y) / (length * length)

                # Early skip if ball is far from flipper segment
                if projection < -0.1 or projection > 1.1:
                    continue

                t = max(0, min(1, projection))
                closest_x = pivot_x + t * flipper_vec_x
                closest_y = pivot_y + t * flipper_vec_y

                dx = ball_x - closest_x
                dy = ball_y - closest_y
                distance = math.sqrt(dx * dx + dy * dy)

                ball_relative_y = ball_y - (flipper_slope * ball_x + flipper_intercept)

                flipper_zone_padding = 100  # tweakable
                if not (pivot_y - flipper_zone_padding <= ball_y <= pivot_y + flipper_zone_padding):
                    continue

                # METHOD 1 collision detection
                if (f.is_left and ball_relative_y < ball_radius) or (not f.is_left and ball_relative_y > -ball_radius):
                    distance_to_line = abs(ball_relative_y) / math.sqrt(flipper_slope**2 + 1)
                    velocity_magnitude = math.hypot(ball_dx, ball_dy)

                    if distance_to_line < ball_radius + velocity_magnitude:
                        if distance < ball_radius and 0.05 < t < 0.95:
                            epsilon = 0.5
                            ball_x = closest_x + (dx / distance) * (ball_radius + epsilon)
                            ball_y = closest_y + (dy / distance) * (ball_radius + epsilon)

                            print(f"Corrected by method 1 to {ball_x}, {ball_y}")
                            print(f"Before update: self.b.x = {self.b.x} and self.b.y = {self.b.y}")

                            position_corrected = True

                            # Normal vector calculation
                            nx, ny = -flipper_vec_y / length, flipper_vec_x / length
                            if not f.is_left:
                                nx, ny = -nx, -ny

                            # Ensure normal points toward ball
                            dot_to_ball = (ball_x - closest_x) * nx + (ball_y - closest_y) * ny
                            if dot_to_ball < 0:
                                nx, ny = -nx, -ny

                            dot_product = ball_dx * nx + ball_dy * ny

                            if dot_product < -1e-3:
                                ball_dx = ball_dx - 2 * dot_product * nx
                                ball_dy = ball_dy - 2 * dot_product * ny

                                if f.active:
                                    ball_dx *= self.settings.flip_force
                                    ball_dy *= self.settings.flip_force
                                else:
                                    ball_dx *= self.settings.deadf_bounce
                                    ball_dy *= self.settings.deadf_bounce

                                min_velocity = 0.5
                                if abs(ball_dx) < min_velocity and abs(ball_dy) < min_velocity:
                                    ball_dx = min_velocity * (1 if ball_dx > 0 else -1)
                                    ball_dy = min_velocity * (1 if ball_dy > 0 else -1)

                                print(f"BOUNCED by method 1")
                                print(f"Ball dy: {ball_dy} at y: {ball_y}")
                                print(f"Checking bounce: ball_dx={ball_dx:.2f}, ball_dy={ball_dy:.2f}, dot={dot_product:.2f}, normal=({nx:.2f}, {ny:.2f})")
                                print(f"Dot product with normal: {dot_product}")

                # METHOD 2 collision detection - only if no previous collision correction
                distance_to_line = abs(ball_relative_y) / math.sqrt(flipper_slope**2 + 1)
                if not position_corrected and distance_to_line < ball_radius + math.hypot(ball_dx, ball_dy):
                    velocity_mag = math.hypot(ball_dx, ball_dy)
                    if velocity_mag > 20:
                        ball_seg_start = (old_x, old_y)
                        ball_seg_end = (self.b.x, self.b.y)
                        flipper_seg_start = (pivot_x, pivot_y)
                        flipper_seg_end = (end_x, end_y)

                        denom = ((ball_seg_end[0] - ball_seg_start[0]) * (flipper_seg_end[1] - flipper_seg_start[1]) -
                                (ball_seg_end[1] - ball_seg_start[1]) * (flipper_seg_end[0] - flipper_seg_start[0]))

                        if abs(denom) > 1e-10:
                            t = ((ball_seg_start[0] - flipper_seg_start[0]) * (flipper_seg_end[1] - flipper_seg_start[1]) -
                                (ball_seg_start[1] - flipper_seg_start[1]) * (flipper_seg_end[0] - flipper_seg_start[0])) / denom
                            u = -((ball_seg_start[0] - ball_seg_end[0]) * (ball_seg_start[1] - flipper_seg_start[1]) -
                                (ball_seg_start[1] - ball_seg_end[1]) * (ball_seg_start[0] - flipper_seg_start[0])) / denom

                            if 0 <= t <= 1 and 0 <= u <= 1:
                                intersect_x = ball_seg_start[0] + t * (ball_seg_end[0] - ball_seg_start[0])
                                intersect_y = ball_seg_start[1] + t * (ball_seg_end[1] - ball_seg_start[1])

                                # Check that intersection point projects on flipper segment (u similar to projection)
                                if -0.1 <= u <= 1.1:
                                    flen = f.length
                                    nx = -flipper_vec_y / flen
                                    ny = flipper_vec_x / flen
                                    if not f.is_left:
                                        nx, ny = -nx, -ny

                                    ball_x = intersect_x + nx * ball_radius
                                    ball_y = intersect_y + ny * ball_radius

                                    print(f"Corrected by method 2 to {ball_x}, {ball_y}")
                                    print(f"Before update: self.b.x = {self.b.x} and self.b.y = {self.b.y}")

                                    position_corrected = True

                                    dot = ball_dx * nx + ball_dy * ny
                                    if dot < -1e-3:
                                        print(f"Distance to flipper: {distance:.3f}, velocity=({ball_dx:.3f}, {ball_dy:.3f}), dot={dot:.5f}")
                                        ball_dx = ball_dx - 2 * dot * nx
                                        ball_dy = ball_dy - 2 * dot * ny

                                        if f.active:
                                            ball_dx *= self.settings.flip_force
                                            ball_dy *= self.settings.flip_force
                                        else:
                                            ball_dx *= self.settings.deadf_bounce
                                            ball_dy *= self.settings.deadf_bounce

                                        min_velocity = 0.5
                                        if abs(ball_dx) < min_velocity and abs(ball_dy) < min_velocity:
                                            ball_dx = min_velocity * (1 if ball_dx > 0 else -1)
                                            ball_dy = min_velocity * (1 if ball_dy > 0 else -1)

                                        print(f"BOUNCED by method 2")
                                        print(f"Ball dy: {ball_dy} at y: {ball_y}")
                                        print(f"Checking bounce: ball_dx={ball_dx:.2f}, ball_dy={ball_dy:.2f}, dot={dot:.2f}, normal=({nx:.2f}, {ny:.2f})")
                                        print(f"Dot product with normal: {dot}")

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
                    if ball_y >= self.settings.screen_height - (155 + ball_radius):
                        if ball_y + ball_diag >= line_y_at_ball:
                            ball_y = line_y_at_ball - ball_diag
                            if ball_dx <= 0:
                                ball_dy, ball_dx = -abs(ball_dx) * bounce, ball_dy * bounce
                            else:
                                ball_dy, ball_dx = -ball_dx * bounce, ball_dy * bounce
                            position_corrected = True

                # Left vertical wall (x=0)
                if ball_x <= ball_radius:
                    if ball_y >= y2:  # y2 is upper y of vertical wall
                        ball_x = ball_radius
                        if ball_dx < 0:
                            ball_dx = -ball_dx * bounce
                        position_corrected = True

            elif block is self.blocks[1]:
                # Right lower block slope line (x2,y2) to (x3,y3)
                m = (y3 - y2) / (x3 - x2)
                c = y2 - m * x2

                line_y_at_ball = m * ball_x + c

                # Check collision with slope
                if ball_x >= x3 - ball_radius:
                    if ball_y >= self.settings.screen_height - (155 + ball_radius):
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

                # Right vertical wall (x=screen_width)
                if ball_x >= self.settings.screen_width - ball_radius:
                    if ball_y >= y2:
                        ball_x = self.settings.screen_width - ball_radius
                        if ball_dx > 0:
                            ball_dx = -ball_dx * bounce
                        position_corrected = True

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


        if abs(ball_y - old_y) > 200 or abs(ball_dx - self.b.dx) > 100: # Sanity check
            print("⚠️ SUSPICIOUS movement detected!")
            print(f"Before: y={old_y}, dy={self.b.dy}")
            print(f"After: y={ball_y}, dy={ball_dy}")

        # Update the ball's position and velocity once after all collisions
        self.b.x = ball_x
        self.b.y = ball_y
        self.b.dx = ball_dx
        self.b.dy = ball_dy

        print(f"FINAL updated ball position: ({self.b.x}, {self.b.y}), velocity: ({self.b.dx}, {self.b.dy})")
        

        # Reset ball if out of bounds or collision condition met
        if self.b.check_collision():
            time.sleep(1.5)
            self.b.reset()
            self.score = 0  # Reset score on game over
                
        

    


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
            
            
            self.draw_obs()
            self.draw_blocks()
        
            self.b.draw_ball()

            self.fl.draw(self.screen)
            self.fr.draw(self.screen)
           
            


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
