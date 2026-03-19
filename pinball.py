### WIZARD PINBALL ###

import pygame
import sys
import random
import time
import math
import argparse
from settings import Settings
from ball import Ball
from bumpers import Bumper
from blocks import Block
from flipper import Flipper
from plunger import Plunger
from gamestate import GameState
from physics_engine import PhysicsEngine
from table_builder import TableBuilder
from notification_center import NotificationCenter
from score_manager import ScoreManager

import os

try:
    print("Script starting...", flush=True)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

script_dir = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = script_dir


class Pinball:

    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        if test_mode:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
        pygame.init()

        self.settings = Settings()

        self.bg = None
        self.state = GameState.MENU
        self.playfield_x = 0
        self.playfield_y = self.settings.top_margin

        if test_mode:
            self.screen = pygame.display.set_mode((self.settings.screen_width,
                                                   self.settings.screen_height))
        else:
            self.screen = pygame.display.set_mode((self.settings.screen_width,
                                                   self.settings.screen_height), pygame.RESIZABLE)
            self.bg = pygame.image.load(os.path.join(base_dir, 'wizard.png'))
        pygame.display.set_caption('Wizard Pinball')

        self.notification_center = NotificationCenter()
        self.score_manager = ScoreManager(self.notification_center, self.settings)

        # Ball
        self.b = Ball(self)

        # Flippers (positioned within playfield)
        self.fl = Flipper(
            2/7 * self.settings.playfield_width,
            self.playfield_y + self.settings.playfield_height - 19/140 * self.settings.playfield_height,
            self.settings.f_length, 0.6, True
        )
        self.fr = Flipper(
            5/7 * self.settings.playfield_width,
            self.playfield_y + self.settings.playfield_height - 19/140 * self.settings.playfield_height,
            self.settings.f_length, -0.6, False
        )

        self.flippers = [self.fl, self.fr]

        # Table elements
        self.table_builder = TableBuilder(self.settings)
        self.bumpers = self.table_builder.generate_bumpers()
        self.blocks = self.table_builder.generate_blocks()

        # Physics engine
        self.physics_engine = PhysicsEngine(
            self.b, self.flippers, self.bumpers, self.blocks,
            self.settings, self.notification_center
        )

        # Plunger lane
        self.lane_center = self.table_builder.get_lane_center()
        self.lane_bottom = self.settings.screen_height
        self.b.lane_x_center = self.lane_center
        self.b.lane_bottom = self.lane_bottom
        self.b.reset()   # reposition ball in the lane

        # Plunger
        self.plunger = Plunger(
            self.lane_center,
            self.lane_bottom - 20,
            max_pull=100,
            pull_speed=5,
            max_launch_speed=15
        )
        # Set plunger lane using table builder
        self.lane_center = self.table_builder.get_lane_center()
        self.lane_bottom = self.table_builder.get_lane_bottom()
        self.b.lane_x_center = self.lane_center
        self.b.lane_bottom = self.lane_bottom

        # Create plunger at correct height
        self.plunger = Plunger(
            self.lane_center,
            self.table_builder.get_plunger_base_y(),
            max_pull=100,
            pull_speed=5,
            max_launch_speed=15
        )

        # Set up background
        if not test_mode:
            self.bg = pygame.image.load(os.path.join(base_dir, 'wizard.png')).convert()
            # Scale to playfield size
            self.bg = pygame.transform.scale(self.bg,
                                             (self.settings.playfield_width,
                                              self.settings.playfield_height))
        else:
            self.bg = None

    def draw_bumpers(self):
        for bumper in self.bumpers:
            pygame.draw.circle(self.screen, bumper.c, (bumper.x, bumper.y), bumper.radius)

    def draw_blocks(self):
        for block in self.blocks:
            pygame.draw.polygon(self.screen, block.c, block.vertices)

        # Visual walls
        wall_color = (100, 100, 100)
        # Left wall
        pygame.draw.rect(self.screen, wall_color,
                         (0, self.settings.top_margin,
                          self.settings.lane_wall_thickness,
                          self.settings.screen_height - self.settings.top_margin))
        
        pygame.draw.rect(self.screen, wall_color,
                         (0, self.settings.top_margin,
                          self.settings.screen_width,
                          self.settings.lane_wall_thickness))
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
            elif event.key == pygame.K_r:
                self.b.reset()
            elif event.key == pygame.K_SPACE:
                if not self.b.launched:
                    self.plunger.start_pull()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.fl.active = False
                self.fl.deactivate()
                if self.b.trapped:
                    self.b.trapped = False
                    self.b.dy = 0.21
            elif event.key == pygame.K_RIGHT:
                self.fr.active = False
                self.fr.deactivate()
                if self.b.trapped:
                    self.b.trapped = False
                    self.b.dy = 0.21
            elif event.key == pygame.K_SPACE:
                if not self.b.launched:
                    speed = self.plunger.release()
                    self.b.dy = -speed   # upward launch
                    self.b.launched = True

    def _handle_paused_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self.state = GameState.PLAYING

    def _start_game(self):
        self.state = GameState.PLAYING
        self.b.reset()
        self.b.trapped = False
        self.score_manager.reset()

    def _update(self):
        if self.state == GameState.PLAYING:
            # Plunger update while pulling
            if not self.b.launched and self.plunger.pulling:
                self.plunger.update(1)

            for _ in range(self.settings.phys_runs):
                self.physics_engine.update()

            # Check if ball is resting on stopper (allows relaunch)
            if (self.b.launched and 
                abs(self.b.x - self.lane_center) < 5 and
                abs(self.b.y - (self.lane_bottom - self.settings.br)) < 5 and
                math.hypot(self.b.dx, self.b.dy) < 0.5):
                self.b.launched = False

            if self.b.lost:
                time.sleep(1.5)
                self.b.reset()
                self.b.trapped = False
                self.score_manager.reset()

    def _draw(self):
        self.screen.fill((0, 0, 0))
        
        # Draw playfield background if available
        if self.bg:
            self.screen.blit(self.bg, (self.settings.lane_wall_thickness, self.playfield_y))

        # Game elements
        self.fl.draw(self.screen)
        self.fr.draw(self.screen)
        self.b.draw_ball()
        self.draw_bumpers()
        self.plunger.draw(self.screen)
        


        if not self.test_mode:
            self.draw_blocks()

        # Overlay text
        if self.state == GameState.MENU:
            self._draw_menu_text()
        elif self.state == GameState.PAUSED:
            self._draw_paused_text()

        # Try to load the custom font
        try:
            font_path = os.path.join(base_dir, 'PressStart2P-Regular.ttf')
            title_font = pygame.font.Font(font_path, 12 )  # Adjust size as needed
        except:
            # Fallback to default font if custom font not found
            title_font = pygame.font.Font(None, 36)

        # Score (use a different font or the same – here we keep default)
        f = pygame.font.Font(font_path, 16)
        score_text = f.render(f'Score: {self.score_manager.score}', True, self.settings.wht)
        self.screen.blit(score_text, (12, 60))

        # Title – use the loaded font
        title_text = title_font.render('WIZARD PINBALL', True, self.settings.wht)
        title_rect = title_text.get_rect(center=(self.settings.screen_width // 2, self.settings.top_margin // 4))
        self.screen.blit(title_text, title_rect)

        

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
        self.score_manager.reset()
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

            self.physics_engine.update()

            if frame % 50 == 0:
                print(f"Frame {frame}: ball at ({self.b.x:.1f}, {self.b.y:.1f}), "
                      f"velocity ({self.b.dx:.2f}, {self.b.dy:.2f}), score={self.score_manager.score}")

            if self.b.lost:
                print(f"Frame {frame}: BALL LOST - final position ({self.b.x}, {self.b.y})")
                self.b.reset()
                self.score_manager.reset()

            frame += 1

        print(f"=== TEST COMPLETE - Final score: {self.score_manager.score} ===")
        pygame.quit()
        input("Press Enter to exit...")


if __name__ == '__main__':
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
        if input == "":
            sys.exit()
        else:
            sys.exit()