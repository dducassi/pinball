### WIZARD PINBALL ###

import pygame
import sys
import random
import time
import math
import argparse
from settings import Settings
from ball import Ball
from obstacles import Obstacle
from blocks import Block
from flipper import Flipper
from gamestate import GameState
from physics_engine import PhysicsEngine
from table_builder import TableBuilder


import os

try:
    print("Script starting...", flush=True)
    # rest of code
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()


script_dir = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    # Running as EXE - use temporary bundle directory
    base_dir = sys._MEIPASS
else:
    # Running as script - use normal script directory
    base_dir = script_dir



class Pinball:
    
    

    def __init__(self, test_mode=False):
        # Initialize Pygame and settings
        self.test_mode = test_mode
        if test_mode:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
        pygame.init()

        self.settings = Settings()

        # Set up the game window
        self.bg = None

        # Start in Menu mode
        self.state = GameState.MENU
        self.score = 0
        
        if test_mode:
            self.screen = pygame.display.set_mode((self.settings.screen_width, 
                self.settings.screen_height))
        else:
            self.screen = pygame.display.set_mode((self.settings.screen_width, 
                self.settings.screen_height), pygame.RESIZABLE)
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
        self.table_builder = TableBuilder(self.settings)
        self.obs = self.table_builder.generate_obstacles()
        self.blocks = self.table_builder.generate_blocks()
        self.physics_engine = PhysicsEngine(self.b, self.flippers, self.obs, self.blocks, self.settings)


    def draw_obs(self):
        for ob in self.obs:
            pygame.draw.circle(self.screen, ob.c, (ob.x, ob.y), self.settings.orad)
    
    def draw_blocks(self):
        for block in self.blocks:
            pygame.draw.polygon(self.screen, block.c, [(block.x1, block.y1), (block.x2, block.y2), (block.x3, block.y3), (block.x4, block.y4)])

    def increment_score(self):
        self.score += self.settings.pph # Score goes up


    def run_game(self):
        clock = pygame.time.Clock()
        while True:
            self._handle_events()
            self._update()
            self._draw()
            clock.tick(30)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Dispatch to current state
            if self.state == GameState.MENU:
                self._handle_menu_event(event)
            elif self.state == GameState.PLAYING:
                self._handle_playing_event(event)
            elif self.state == GameState.PAUSED:
                self._handle_paused_event(event)

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            self._start_game()

    def _handle_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.fl.active = True
                self.fl.activate()
            elif event.key == pygame.K_RIGHT:
                self.fr.active = True
                self.fr.activate()
            elif event.key == pygame.K_p:
                self.state = GameState.PAUSED
            elif event.key == pygame.K_r:   # reset ball (optional)
                self.b.reset()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.fl.active = False
                self.fl.deactivate()
            elif event.key == pygame.K_RIGHT:
                self.fr.active = False
                self.fr.deactivate()

    def _handle_paused_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self.state = GameState.PLAYING

    def _start_game(self):
        self.state = GameState.PLAYING
        self.b.reset()
        self.score = 0

    def _update(self):
        if self.state == GameState.PLAYING:
            for _ in range(self.settings.phys_runs):
                events = self.physics_engine.update()
                # Process events (score and color change)
                for event in events:
                    if event[0] == 'obstacle_hit':
                        obs = event[1]
                        self.increment_score()
                        # Cycle obstacle color (original logic)
                        if obs.c == self.settings.red:
                            obs.c = self.settings.blu
                        elif obs.c == self.settings.blu:
                            obs.c = self.settings.ylw
                        elif obs.c == self.settings.ylw:
                            obs.c = self.settings.red

            # Ball out-of-bounds check
            if self.b.check_collision():
                time.sleep(1.5)
                self.b.reset()
                self.score = 0

    def _draw(self):
        # Common drawing (background, score, game objects)
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        # Draw game elements
        self.fl.draw(self.screen)
        self.fr.draw(self.screen)
        self.b.draw_ball()
        self.draw_obs()
        if not self.test_mode:
            self.draw_blocks()

        # Draw overlay text based on state
        if self.state == GameState.MENU:
            self._draw_menu_text()
        elif self.state == GameState.PAUSED:
            self._draw_paused_text()

        # Score display (always)
        f = pygame.font.Font(None, 36)
        score_text = f.render(f'Score: {self.score}', True, self.settings.wht)
        self.screen.blit(score_text, (20, 20))

        pygame.display.flip()

    def _draw_menu_text(self):
        f = pygame.font.Font(None, 36)
        text = f.render("Press S to start", True, self.settings.wht)
        self.screen.blit(text, ((self.settings.screen_width - text.get_width()) // 2,
                                (self.settings.screen_height - text.get_height()) // 2))

    def _draw_paused_text(self):
        f = pygame.font.Font(None, 36)
        text = f.render("Paused", True, self.settings.wht)
        self.screen.blit(text, ((self.settings.screen_width - text.get_width()) // 2,
                                (self.settings.screen_height - text.get_height()) // 2))

    def run_test(self, num_frames=500):
        print(f"=== HEADLESS TEST MODE ({num_frames} frames) ===")
        self.score = 0
        running = True
        frame = 0
        
        print(f"Initial ball: ({self.b.x}, {self.b.y}) velocity: ({self.b.dx}, {self.b.dy})")
        
        while running and frame < num_frames:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
            except:
                pass
            
            events = self.physics_engine.update()
            for event in events:
                if event[0] == 'obstacle_hit':
                    self.increment_score()
            
            if frame % 50 == 0:
                print(f"Frame {frame}: ball at ({self.b.x:.1f}, {self.b.y:.1f}), velocity ({self.b.dx:.2f}, {self.b.dy:.2f}), score={self.score}")
            
            if self.b.check_collision():
                print(f"Frame {frame}: BALL RESET - final position ({self.b.x}, {self.b.y})")
                self.b.reset()
                self.score = 0
            
            frame += 1
        
        print(f"=== TEST COMPLETE - Final score: {self.score} ===")
        pygame.quit()
        input("Press Enter to exit...")

if __name__ == '__main__':
    import sys
    try:
        print("Starting pinball...", flush=True)
        parser = argparse.ArgumentParser(description='Wizard Pinball')
        parser.add_argument('--test', action='store_true', help='Run in headless test mode')
        parser.add_argument('--frames', type=int, default=500, help='Number of frames to run in test mode')
        args = parser.parse_args()
        
        print(f"Creating Pinball instance, test_mode={args.test}", flush=True)
        pb = Pinball(test_mode=args.test)
        print("Pinball instance created", flush=True)
        
        if args.test:
            pb.run_test(num_frames=args.frames)
        else:
            pb.run_game()
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
