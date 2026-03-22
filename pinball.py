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
from sound_manager import SoundManager
import winsound



from light import Light

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
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)
        (self.beep_hz, self.beep_dur) = (600, 200)

        self.settings = Settings()
        self.bg = None
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.state = GameState.MENU
        self.playfield_x = 0
        self.playfield_y = self.settings.top_margin

        # Message system
        self.main_message = ""
        self.secondary_message = ""
        self._update_messages()

        # Temporary message system
        self.temp_message = ""
        self.temp_message_time = 0
        self.temp_message_duration = 2000  # milliseconds

        # Load Crystal Orb image
        try:
            img = pygame.image.load(os.path.join(base_dir, 'crystal_orb.png')).convert_alpha()
            self.orb_image = img
            print("Crystal orb image loaded, size:", img.get_size())
            desired_size = 180 # radius 45 * 2
            self.orb_image = pygame.transform.scale(img, (desired_size, desired_size))
        except:
            print("Crystal orb image not found, using fallback circle.")
            self.orb_image = None

        # Load Small Orb image (for lower bumpers)p
        try:
            small_img = pygame.image.load(os.path.join(base_dir, 'small_orb.png')).convert_alpha()
            self.small_orb_image = small_img
            print("Small orb image loaded, size:", small_img.get_size())
            # No scaling here – Bumper will scale to its radius
        except:
            print("Small orb image not found, using fallback circle.")
            self.small_orb_image = None

        # Load Tiny Bumper image (for tiny bumpers near main orb)
        try:
            tiny_bumper_img = pygame.image.load(os.path.join(base_dir, 'tiny_bumper.png')).convert_alpha()
            self.tiny_bumper_image = tiny_bumper_img
            print("Tiny Bumper image loaded, size:", tiny_bumper_img.get_size())
        except:
            print("Tiny Bumper image not found, using fallback circle.")
            self.tiny_bumper_image = None

         # Load pinball image (ball)
        try:
            ball_img = pygame.image.load(os.path.join(base_dir, 'pinball.png')).convert_alpha()
            self.ball_image = ball_img
            print("Pinball image loaded, size:", ball_img.get_size())
        except:
            print("Pinball image not found, using fallback circle.")
            self.ball_image = None
        self.b = Ball(self, self.ball_image)

        # Load block texture
        try:
            block_texture = pygame.image.load(os.path.join(base_dir, 'block_texture.png')).convert()
            self.block_texture = block_texture
            print("Block texture loaded")
        except:
            print("Block texture not found, using solid colors.")
            self.block_texture = None

        # Load triangle block texture
        try:
            tri_texture = pygame.image.load(os.path.join(base_dir, 'tri_image.png')).convert_alpha()
            tri_flipped = pygame.transform.flip(tri_texture, True, False)   # horizontal flip
            tri_mirrored = pygame.transform.flip(tri_texture, False, True)   # vertical flip
            self.tri_texture = tri_texture
            self.tri_flipped = tri_flipped
            self.tri_mirrored = tri_mirrored
            print("Triangle texture loaded")
        except:
            print("Triangle texture not found, using solid colors.")
            self.tri_texture = None
            self.tri_flipped = None
            self.tri_mirrored = None

        
        # Load flipper image
        try:
            flipper_img = pygame.image.load(os.path.join(base_dir, 'flipper.png')).convert_alpha()
            self.flipper_image = flipper_img
            print("Flipper image loaded")
        except:
            print("Flipper image not found, using fallback drawing.")
            self.flipper_image = None

         # Load light image
        try:
            light_img = pygame.image.load(os.path.join(base_dir, 'light.png')).convert_alpha()
            self.light_image = light_img
        except:
            self.light_image = None

        


        pygame.display.set_caption('Wizard Pinball')

        self.notification_center = NotificationCenter()
        self.score_manager = ScoreManager(self.notification_center, self.settings)
        self.sound_manager = SoundManager(self.notification_center, base_dir)

        # High score
        self.high_score = self.load_high_score()
        self.notification_center.add_observer('score_changed', self.on_score_changed)

        
        # Observe bumper hits
        self.notification_center.add_observer('bumper_hit', self.on_bumper_hit)

        # Ball
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
        self.table_builder = TableBuilder(self.settings, self.block_texture, self.tri_texture, self.tri_flipped, self.tri_mirrored)
        self.blocks = self.table_builder.generate_blocks()
        self.bumpers, self.lights = self.table_builder.generate_bumpers(self.orb_image, self.small_orb_image, self.tiny_bumper_image, self.light_image)

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
            self.lane_bg =  pygame.image.load(os.path.join(base_dir, 'lane_bg.png')).convert()
            self.lane_bg = pygame.transform.scale(self.lane_bg,
                                             (self.settings.playfield_width,
                                              self.settings.playfield_height))
        else:
            self.bg = None
            self.lane_bg = None

        self.ball_save_active = False
        self.ball_save_start_time = 0
        self.ball_save_duration = 10000  # 10 seconds in milliseconds  

    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self):
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            print("Could not save high score.")

    def on_score_changed(self, score):
        if score > self.high_score:
            self.high_score = score
            self.save_high_score()

    # Drawing helpers
    def draw_bumpers(self):
        for bumper in self.bumpers:
            bumper.draw(self.screen)
                
    def draw_blocks(self):
        for block in self.blocks:
            block.draw(self.screen)
        
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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            # Sound test
            winsound.Beep(440, 200)
            winsound.Beep(640, 200)
            self._start_game()

    def _handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._start_game()

    def _handle_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.fl.active = True
                self.fl.activate()
                self.notification_center.post_notification('flipper_click', self.fl)
            elif event.key == pygame.K_RIGHT:
                self.fr.active = True
                self.fr.activate()
                self.notification_center.post_notification('flipper_click', self.fr)
                
            elif event.key == pygame.K_p:
                self._set_state(GameState.PAUSED)
            elif event.key == pygame.K_r:
                self.b.reset()
            elif event.key == pygame.K_SPACE:
                if not self.b.launched:
                    self.plunger.start_pull()   # <-- start pull on press

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
                    self.ball_save_active = True
                    self.ball_save_start_time = pygame.time.get_ticks()
                    self.secondary_message = 'SAVE'   # display during grace period
                    self.notification_center.post_notification('ball_launch')
                    
                    
    def _handle_paused_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self._set_state(GameState.PLAYING)

    # State management
    def _set_state(self, new_state):
        self.state = new_state
        self._update_messages()

    def _update_messages(self):
        if self.state == GameState.MENU:
            self.main_message = "CAST A SPELL!"
            self.secondary_message = "'ENTER' TO INSERT COIN"
        elif self.state == GameState.PAUSED:
            self.main_message = "PAUSED"
            self.secondary_message = ""
        elif self.state == GameState.GAME_OVER:
            self.main_message = "GAME OVER"
            self.secondary_message = "'ENTER' TO INSERT COIN"
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
        self.ball_save_active = False

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

            # Ball save timer – clear "SAVE" after 10 seconds
            if self.ball_save_active and (pygame.time.get_ticks() - self.ball_save_start_time) >= self.ball_save_duration:
                self.ball_save_active = False
                self.secondary_message = ''

            # Ball lost (physics engine sets self.b.lost)
            if self.b.lost:
             now = pygame.time.get_ticks()
             # Check if ball save is active and within time window
             if self.ball_save_active and (now - self.ball_save_start_time) < self.ball_save_duration:
                 # Ball saved!
                 self.temp_message = 'BALL SAVED'
                 self.secondary_message = ''
                 self.temp_message_time = now
                 self.ball_save_active = False   # used up
                 self.b.reset()
                 self.b.trapped = False
                 self.notification_center.post_notification('ball_saved')
             else:
                 self.temp_message = 'BALL LOST'
                 self.secondary_message = ''
                 self.temp_message_time = now
                 self.lives -= 1
                 self.notification_center.post_notification('ball_lost')
                 if self.lives > 0:
                     self.b.reset()
                     self.b.trapped = False
                     
                 else:
                     self._set_state(GameState.GAME_OVER)
                     winsound.Beep(640, 200)
                     winsound.Beep(440, 200)
                     winsound.Beep(640, 200)
                     winsound.Beep(440, 200)

            # Update lights
            for light in self.lights:
                light.update(pygame.time.get_ticks())
                


    # Check for Orb hits:
    def on_bumper_hit(self, bumper):
        if self.state != GameState.PLAYING:
            return
       
        # Find the matching light and update its color to match the bumper
        try:
            idx = self.bumpers.index(bumper)
            if idx < len(self.lights):
                light = self.lights[idx]
                light.set_color(bumper.color)   # sync color with bumper
                light.turn_on(pygame.time.get_ticks())
        except ValueError:
            pass
        try:
            idx = self.bumpers.index(bumper)
            if idx < len(self.lights):
                self.lights[idx].turn_on(pygame.time.get_ticks())
        except ValueError:
            pass
        # Find the index of the bumper
        for i, b in enumerate(self.bumpers):
            if b is bumper:
                if i < len(self.lights):
                    self.lights[i].turn_on(pygame.time.get_ticks())
                break

        if bumper.radius > 20:
            print("Large bumper color:", bumper.color)   # debug
            if bumper.color == self.settings.blu:
                msg = "ORB OF POWER!"
            elif bumper.color == self.settings.red:
                msg = "FIREBALL!"
            elif bumper.color == self.settings.wht:
                msg = "BALL LIGHTNING!"
                
        else:
            msg = random.choice(["BOOM!", "HISS!", "POP!", "ZAP!"])
        if msg:
            self.temp_message = msg
            self.temp_message_time = pygame.time.get_ticks()
                

    # Drawing
    def _draw(self):
        self.screen.fill((0, 0, 0))
        # Playfield background
        if self.bg:
            self.screen.blit(self.bg, (0, self.playfield_y))
        if self.lane_bg:
            self.screen.blit(self.lane_bg, (self.settings.playfield_width, self.playfield_y))
       



        

        # Game elements
        
        self.b.draw_ball()
        for light in self.lights:
            light.draw(self.screen)
        self.draw_bumpers()
        self.plunger.draw(self.screen)
        self.draw_blocks()
        self.fl.draw(self.screen)
        self.fr.draw(self.screen)
       

        # Title
        try:
            title_font = pygame.font.Font(font_path, 12)
        except:
            title_font = pygame.font.Font(None, 36)
        title_text = title_font.render("THE WIZARD'S TOWER", True, self.settings.wht)
        title_rect = title_text.get_rect(center=(self.settings.screen_width // 2, self.settings.top_margin // 5))
        self.screen.blit(title_text, title_rect)

        # Score and lives
        try:
            f = pygame.font.Font(font_path, 11)
        except:
            f = pygame.font.Font(None, 24)
        score_text = f.render(f'SCORE: {self.score_manager.score:,}', True, self.settings.wht)
        self.screen.blit(score_text, (12, 65))
        lives_text = f.render(f'BALLS: {self.lives}', True, self.settings.wht)
        self.screen.blit(lives_text, (self.settings.screen_width - 110, 65))

        # High score (right side, below score)
        try:
            high_font = pygame.font.Font(font_path, 8)   # smaller font
        except:
            high_font = pygame.font.Font(None, 24)      # fallback
        high_text = high_font.render(f'HIGH: {self.high_score:,}', True, self.settings.wht)
        self.screen.blit(high_text, (self.settings.screen_width - 110, 90))
        # Context messages
        self._draw_messages()

        pygame.display.flip()

    def _draw_messages(self):
        now = pygame.time.get_ticks()
        
        # Determine main message (temporary or state)
        if self.temp_message and now - self.temp_message_time < self.temp_message_duration:
            main = self.temp_message
            secondary = self.secondary_message
        else:
            self.temp_message = ""
            main = self.main_message
            secondary = self.secondary_message
        
        if not main and not secondary:
            return

        try:
            font = pygame.font.Font(font_path, 13)
            secondary_font = pygame.font.Font(font_path, 8) if secondary else None
        except:
            font = pygame.font.Font(None, 24)
            secondary_font = pygame.font.Font(None, 16) if secondary else None

        # Main message (centered in top margin)
        if main:
            main_surf = font.render(main, True, self.settings.wht)
            main_rect = main_surf.get_rect(center=(self.settings.screen_width // 2, self.settings.top_margin // 2))
            self.screen.blit(main_surf, main_rect)

        # Secondary message (positioned lower left, below score)
        if secondary:
            sec_font = secondary_font if secondary_font else font
            sec_surf = sec_font.render(secondary, True, self.settings.wht)
            # Place below score (score is at (12, 65); use (12, 90) for secondary)
            sec_rect = sec_surf.get_rect(topleft=(12, 90))
            self.screen.blit(sec_surf, sec_rect)
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