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

font_path = os.path.join(base_dir, 'PressStart2P-Regular.ttf')

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

        # Message system
        self.main_message = ""
        self.secondary_message = ""
        self._update_messages()

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
        self.lives = 3

        # Flippers
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

        # Lane and plunger
        self.lane_center = self.table_builder.get_lane_center()
        self.lane_bottom = self.table_builder.get_lane_bottom()
        self.b.lane_x_center = self.lane_center
        self.b.lane_bottom = self.lane_bottom
        self.b.reset()

        self.plunger = Plunger(
            self.lane_center,
            self.table_builder.get_plunger_base_y(),
            max_pull=100,
            pull_speed=5,
            max_launch_speed=15
        )

        # Background
        if not test_mode:
            self.bg = pygame.image.load(os.path.join(base_dir, 'wizard.png')).convert()
            self.bg = pygame.transform.scale(self.bg,
                                             (self.settings.playfield_width,
                                              self.settings.playfield_height))
        else:
            self.bg = None

    # Drawing helpers
    def draw_bumpers(self):
        for bumper in self.bumpers:
            pygame.draw.circle(self.screen, bumper.c, (bumper.x, bumper.y), bumper.radius)

    def draw_blocks(self):
        for block in self.blocks:
            pygame.draw.polygon(self.screen, block.c, block.vertices)
        # Visual walls
        wall_color = (100, 100, 100)
        pygame.draw.rect(self.screen, wall_color,
                         (0, self.settings.top_margin,
                          self.settings.lane_wall_thickness,
                          self.settings.screen_height - self.settings.top_margin))
        pygame.draw.rect(self.screen, wall_color,
                         (0, self.settings.top_margin,
                          self.settings.screen_width,
                          self.settings.lane_wall_thickness))

    # Game loop
    def run_game(self):
        clock = pygame.time.Clock()
        while True:
            self._handle_events()
            self._update()
            self._draw()
            clock.tick(60)

    # Event handling
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
            elif self.state == GameState.GAME_OVER:
                self._handle_game_over_event(event)

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            self._start_game()

    def _handle_game_over_event(self, event):
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
                self._set_state(GameState.PAUSED)
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
                    self.b.dy = -speed
                    self.b.launched = True

    def _handle_paused_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self._set_state(GameState.PLAYING)

    # State management
    def _set_state(self, new_state):
        self.state = new_state
        self._update_messages()

    def _update_messages(self):
        if self.state == GameState.MENU:
            self.main_message = "Press S to start"
            self.secondary_message = ""
        elif self.state == GameState.PAUSED:
            self.main_message = "PAUSED"
            self.secondary_message = ""
        elif self.state == GameState.GAME_OVER:
            self.main_message = "GAME OVER"
            self.secondary_message = ""
        else:  # PLAYING
            self.main_message = ""
            self.secondary_message = ""

    # Game start
    def _start_game(self):
        self._set_state(GameState.PLAYING)
        self.b.reset()
        self.b.trapped = False
        self.score_manager.reset()
        self.lives = 3

    # Physics update
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

            # Ball lost
            if self.b.y > self.settings.screen_height * 1.05:
                self.main_message = 'BALL LOST'
            if self.b.lost:
                self.lives -= 1
                if self.lives > 0:
                    self.b.trapped = False
                    self.main_message = 'NEW BALL'
                    self.b.reset()
                    time.sleep(1.5)
                    
                else:
                    self._set_state(GameState.GAME_OVER)

            
                

    # Drawing
    def _draw(self):
        self.screen.fill((0, 0, 0))
        # Playfield background
        if self.bg:
            self.screen.blit(self.bg, (self.settings.lane_wall_thickness, self.playfield_y))

        for bumper in self.bumpers:
                if bumper.radius > 20:
                    if self.b.launched and bumper.c == self.settings.blu:
                        self.main_message = 'ORB OF POWER'
                    elif self.b.launched and bumper.c == self.settings.red:
                        self.main_message = 'FIREBALL'
                    elif self.b.launched and bumper.c == self.settings.ylw:
                        self.main_message = 'BALL LIGHTNING'

        # Game elements
        self.fl.draw(self.screen)
        self.fr.draw(self.screen)
        self.b.draw_ball()
        self.draw_bumpers()
        self.plunger.draw(self.screen)

        if not self.test_mode:
            self.draw_blocks()

        # Title
        try:
            title_font = pygame.font.Font(font_path, 12)
        except:
            title_font = pygame.font.Font(None, 36)
        title_text = title_font.render('WIZARD PINBALL', True, self.settings.wht)
        title_rect = title_text.get_rect(center=(self.settings.screen_width // 2, self.settings.top_margin // 5))
        self.screen.blit(title_text, title_rect)

        # Score and lives
        try:
            f = pygame.font.Font(font_path, 12)
        except:
            f = pygame.font.Font(None, 24)
        score_text = f.render(f'Score: {self.score_manager.score}', True, self.settings.wht)
        self.screen.blit(score_text, (12, 65))
        lives_text = f.render(f'Balls: {self.lives}', True, self.settings.wht)
        self.screen.blit(lives_text, (self.settings.screen_width - 110, 65))

        # Context messages
        self._draw_messages()

        pygame.display.flip()

    def _draw_messages(self):
        if not self.main_message and not self.secondary_message:
            return
        try:
            main_font = pygame.font.Font(font_path, 14)
            second_font = pygame.font.Font(font_path, 9)
        except:
            main_font = pygame.font.Font(None, 24)
            second_font = pygame.font.Font(font_path, 12)
        

        if self.main_message:
            text = main_font.render(self.main_message, True, self.settings.wht)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, self.settings.top_margin // 2))
            self.screen.blit(text, text_rect)
        if self.secondary_message:
            text2 = second_font.render(self.secondary_message, True, self.settings.wht)
            text2_rect = text2.get_rect(center=(self.settings.screen_width // 2,
                                                 self.settings.top_margin // 2 + text.get_height() + 5))
            self.screen.blit(text2, text2_rect)

    # Test mode
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