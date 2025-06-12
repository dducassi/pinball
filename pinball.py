
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

    


    def run_game(self):
        running = False  # Initially game is not running
        paused = False   # Initially game is not paused
        score = 0
        
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
                            score = 0
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

                # Move the ball and check for wall collisions
                self.fl.update()
                self.fr.update()


                # Save old position
                old_x, old_y = self.b.x, self.b.y

                # Then move ball
                self.b.move()
                
                
                
                
                
                
            
                # Find closest point on flipper to ball

                ball_x = self.b.x
                ball_y = self.b.y
                ball_dx = self.b.dx
                ball_dy = self.b.dy
                ball_radius = self.settings.br
                position_corrected = False
                fcollision_occurred = False

                for f in self.flippers:
                    

                    # Get flipper properties
                    pivot_x, pivot_y = f.pivot
                    angle = f.angle
                    length = f.length

                    if f == self.fl:
                        if angle < -0.5:
                            f.active = False
                    elif f == self.fr:
                        if angle > 0.5:
                            f.active = False
                        

                    # Calculate flipper endpoints
                    end_x = pivot_x + math.cos(angle) * length
                    end_y = pivot_y + math.sin(angle) * length

                    # Calculate flipper slope
                    if abs(end_x - pivot_x) > 0:  # Avoid division by zero
                        flipper_slope = (end_y - pivot_y) / (end_x - pivot_x)
                        flipper_intercept = pivot_y - flipper_slope * pivot_x
                        
                        # Calculate ball's position relative to flipper line
                        ball_relative_y = ball_y - (flipper_slope * ball_x + flipper_intercept)
                    
                    # Check if ball is crossing the flipper line
                    if (f.is_left and ball_relative_y < ball_radius) or (not f.is_left and ball_relative_y > -ball_radius):
                        # Calculate distance from ball to flipper line
                        distance_to_line = abs(ball_relative_y) / math.sqrt(flipper_slope**2 + 1)
                    

                    if  distance_to_line < ball_radius + math.hypot(ball_dx, ball_dy):
                        # Calculate closest point on flipper to ball
                        # (using vector projection)
                        flipper_vec_x = end_x - pivot_x
                        flipper_vec_y = end_y - pivot_y
                        to_ball_x = ball_x - pivot_x
                        to_ball_y = ball_y - pivot_y
                        
                        projection = (to_ball_x * flipper_vec_x + to_ball_y * flipper_vec_y) / (length * length)
                        t = max(0, min(1, projection))
                        closest_x = pivot_x + t * flipper_vec_x
                        closest_y = pivot_y + t * flipper_vec_y
                    
                        # Calculate actual distance to flipper segment
                        dx = ball_x - closest_x
                        dy = ball_y - closest_y
                        distance = math.sqrt(dx*dx + dy*dy)
                    
    
                    
                        if distance <= ball_radius * 1.415: # Small tolerance # 
                            fcollision_occurred = True
                        
                            # Position correction to prevent sinking
                            overlap = ball_radius - distance
                            if distance > 0:  # Avoid division by zero
                                ball_x = closest_x + (dx / distance) * (ball_radius + 0.5)
                                ball_y = closest_y + (dy / distance) * (ball_radius + 0.5)
                                
                                print(f"Corrected by method 1 to {ball_x}, {ball_y}")
                                print(f"Before update: self.b.x = {self.b.x} and self.b.y = {self.b.y}")

                                self.b.x = ball_x
                                self.b.y = ball_y
                                position_corrected = True
                            
                            # Calculate normal vector
                            nx, ny = -flipper_vec_y/length, flipper_vec_x/length  # Perpendicular
                            if not f.is_left:
                                nx, ny = -nx, -ny  # Flip for right flipper
                            
                            
                            
                            # Ensure normal faces toward ball
                            dot_to_ball = (ball_x - closest_x) * nx + (ball_y - closest_y) * ny
                            if dot_to_ball < 0:
                                nx, ny = -nx, -ny
                            
                            # Calculate velocity dot product with normal
                            dot_product = ball_dx * nx + ball_dy * ny
                            
                            # Only bounce if moving toward flipper
                            if dot_product < 0 or position_corrected:
                                # Calculate reflection
                                ball_dx = ball_dx - 2 * dot_product * nx
                                ball_dy = ball_dy - 2 * dot_product * ny
                                
                                # Apply energy loss/boost based on flipper state
                                if f.active:
                                    ball_dx *= self.settings.flip_force
                                    ball_dy *= self.settings.flip_force
                                else:
                                    ball_dx *= self.settings.deadf_bounce
                                    ball_dy *= self.settings.deadf_bounce
                                
                                break

                    # Now check if line segment to next_x and next_y and current self.b.x, self.b.y intersects with flipper line, bounce
                    if not fcollision_occurred and distance_to_line < ball_radius + math.hypot(ball_dx, ball_dy):
                        
                        # NEW: Segment intersection check (if no collision detected yet)
                        if self.b.dy > 20 or abs(self.b.dx) > 20:
                            
                            
                            ball_radius = self.settings.br

    
                            
                            # Define ball path segment (current to next position)
                            ball_seg_start = (self.b.x, self.b.y)
                            ball_seg_end = (old_x, old_y)
                            
                            # Define flipper segment
                            flipper_seg_start = (pivot_x, pivot_y)
                            flipper_seg_end = (end_x, end_y)
                            
                            # Calculate intersection
                            denom = ((ball_seg_end[0] - ball_seg_start[0]) * (flipper_seg_end[1] - flipper_seg_start[1]) - 
                                    (ball_seg_end[1] - ball_seg_start[1]) * (flipper_seg_end[0] - flipper_seg_start[0]))
                            
                            if abs(denom) > 1e-10:  # Not parallel
                                
                                ball_dx, ball_dy = self.b.dx, self.b.dy
                                t = ((ball_seg_start[0] - flipper_seg_start[0]) * (flipper_seg_end[1] - flipper_seg_start[1]) - 
                                    (ball_seg_start[1] - flipper_seg_start[1]) * (flipper_seg_end[0] - flipper_seg_start[0])) / denom
                                u = -((ball_seg_start[0] - ball_seg_end[0]) * (ball_seg_start[1] - flipper_seg_start[1]) - 
                                    (ball_seg_start[1] - ball_seg_end[1]) * (ball_seg_start[0] - flipper_seg_start[0])) / denom
                                
                                if 0 <= t <= 1 and 0 <= u <= 1:  # Segments intersect
                                    # Calculate exact intersection point
                                    intersect_x = ball_seg_start[0] + t * (ball_seg_end[0] - ball_seg_start[0])
                                    intersect_y = ball_seg_start[1] + t * (ball_seg_end[1] - ball_seg_start[1])
                                    
                                    # Calculate flipper normal vector
                                    flipper_vec_x = end_x - pivot_x
                                    flipper_vec_y = end_y - pivot_y
                                    flen = math.hypot(flipper_vec_x, flipper_vec_y)
                                    if flen > 0:
                                        fcollision_occurred = True
                                        nx = -flipper_vec_y / flen  # Perpendicular (normal)
                                        ny = flipper_vec_x / flen
                                        if not f.is_left:
                                            nx, ny = -nx, -ny  # Flip normal for right flipper
                                        
                                        # Position correction (push ball to edge)
                                        ball_x = intersect_x + nx * ball_radius
                                        ball_y = intersect_y + ny * ball_radius
                                        print(f"Corrected by method 2 to {ball_x}, {ball_y}")
                                        print(f"Before update: self.b.x = {self.b.x} and self.b.y = {self.b.y}")
                                        self.b.x = ball_x
                                        self.b.y = ball_y
                                        position_corrected = True
                                       
                                        
                                        # Calculate reflection
                                        dot = ball_dx * nx + ball_dy * ny
                                        if dot < 0 or position_corrected:  # Only bounce if moving toward flipper
                                            ball_dx = ball_dx - 2 * dot * nx
                                            ball_dy = ball_dy - 2 * dot * ny
                                            
                                            # Apply force multipliers
                                            if f.active:
                                                ball_dx *= self.settings.flip_force
                                                ball_dy *= self.settings.flip_force
                                            else:
                                                ball_dx *= self.settings.deadf_bounce
                                                ball_dy *= self.settings.deadf_bounce
                                        
                                        
                                        break  # Handle only first collision



                # Update ball state if collision occurred
                if fcollision_occurred:
                    self.b.x, self.b.y = ball_x, ball_y
                    self.b.dx, self.b.dy = ball_dx, ball_dy
                
                                

                                          


                # Check for collision with blocks
                for block in self.blocks:
                    if block is self.blocks[0]:
                        slope_start = block.x2, block.y2 
                        slope_end = block.x3, block.y3
                        # Calculate slope: y = mx + c
                        m = (block.y3 - block.y2) / (block.x3 - block.x2)
                        c =  block.y2 - m * block.x2

                        # Check if ball is below the left slope
                        line_y_at_ball = m * self.b.x + c
                        line_x_at_ball = (self.b.y - c) / m
                        if self.b.x <= 100 + self.settings.br:
                            if self.b.y >= self.settings.screen_height - (155 + self.settings.br):
                                if self.b.y +  self.settings.br * 1.415 >= line_y_at_ball:
                                    self.b.y = line_y_at_ball - self.settings.br * 1.415
                                    if self.b.dx <= 0:
                                        self.b.dy, self.b.dx = -abs(self.b.dx) * self.settings.block_bounce, self.b.dy * self.settings.block_bounce
                                    else:
                                        self.b.dy, self.b.dx = -(self.b.dx) * self.settings.block_bounce, self.b.dy * self.settings.block_bounce


                        else:
                            # If below flippers, bounce right
                            if self.b.dy > self.settings.screen_height - 10:
                                if self.b.dx - self.settings.br <= 100:
                                    self.b.dx = -0.8 * self.b.dx
                                if self.b.dx + self.settings.br <= 100:
                                    self.b.dx = -0.8 * self.b.dx
                        
                    if block is self.blocks[1]:
                        slope_start = block.x2, block.y2 
                        slope_end = block.x3, block.y3
                        # Calculate slope: y = mx + c
                        m =  (block.y3 - block.y2) / (block.x3 - block.x2)
                        c =  block.y2 - m * block.x2
                        line_y2_at_ball = m * self.b.x + c
                        if self.b.x > self.settings.screen_width - 100 - self.settings.br:
                            if self.b.y >= self.settings.screen_height - (155 + self.settings.br):
                                if self.b.y + self.settings.br * 1.415 >= line_y2_at_ball:
                                    self.b.y = line_y2_at_ball - self.settings.br * 1.415
                                    if self.b.dx <= 0:
                                        self.b.dy, self.b.dx = self.b.dx * self.settings.block_bounce, (-self.b.dy) * self.settings.block_bounce
                                    elif self.b.dx > 0:
                                        if self.b.dy <= 0:
                                            self.b.dy, self.b.dx = -self.b.dx * self.settings.block_bounce, self.b.dy * self.settings.block_bounce
                                        if self.b.dy > 0:
                                            self.b.dy, self.b.dx = (-self.b.dx) * self.settings.block_bounce, (-self.b.dy) * self.settings.block_bounce
                                                             
                                    

                # Check for collisions with obstacles
                for ob in self.obs:
                    # Circular collision detection
                    # If ball's x is within obstacle's radius
                    distx = self.b.x - ob.x
                    disty = self.b.y - ob.y
                    distance = math.sqrt(distx**2 + disty**2) # a^2 + b^2 = c^2
                    min_distance = self.settings.orad + self.settings.br
                    
                    if distance < min_distance:
                        # Fix Location:
                        if distance > 0:
                            correction = (min_distance - distance) / distance
                            self.b.x += distx * correction
                            self.b.y += disty * correction
                            

                        # Calculate normal vector (from obstacle to ball)
                        if distance == 0:  # Handle exactly overlapping centers
                            nx, ny = 1, 0

                        else:
                            nx = distx / distance  # Normalized vector from obstacle to ball
                            ny = disty / distance
            
                        # Original velocity components
                        dx_old, dy_old = self.b.dx, self.b.dy
                            
                        # Compute dot product (v · n)
                        dot_product = dx_old * nx + dy_old * ny
                       
                            
                            
                        if dot_product < 0:
                            # Simplified reflection (normalized vector)
                            self.b.dx = self.b.dx - 2 * dot_product * nx
                            self.b.dy = self.b.dy - 2 * dot_product * ny

                        # Update velocity with reflection
                        self.b.dx *= self.settings.obs_bounce
                        self.b.dy *= self.settings.obs_bounce
                            
                        score += self.settings.pph # Score goes up
                        if ob.c == self.settings.red:
                            ob.c = self.settings.blu
                        elif ob.c == self.settings.blu:
                            ob.c = self.settings.ylw
                        elif ob.c == self.settings.ylw:
                            ob.c = self.settings.red
                        
                
                if self.b.check_collision():
                        time.sleep(1.5)
                        self.b.reset()
                        score = 0  # Reset score when the game is over
                
                

            # Draw game elements
            
            
            self.draw_obs()
            self.draw_blocks()
        
            self.b.draw_ball()

            self.fl.draw(self.screen)
            self.fr.draw(self.screen)
           
            


            # Display the current score
            f = pygame.font.Font(None, 36)
            score_text = f.render(f'Score: {score}', True, self.settings.wht)
            self.screen.blit(score_text, (20, 20))


            # Update the display
            pygame.display.flip()


            # Control the frame rate
            pygame.time.Clock().tick(60)

if __name__ == '__main__':
    # Make a game instance and run the game.
    pb = Pinball()
    pb.run_game()
