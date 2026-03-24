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
        

        self.settings = Settings()
        


        self.bg = None
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.state = GameState.MENU
        self.playfield_x = 0
        self.playfield_y = self.settings.top_margin
        # Load background music
        self.music_loaded = False
        self.music_playing = True
        self.original_music_volume = self.settings.music_volume 
        self.sound_enabled = True   # global sound toggle
        
        if self.music_playing == True:
            try:
                # Use a suitable format (OGG recommended)
                music_path = os.path.join(base_dir, 'music.mid')
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.settings.music_volume)
                pygame.mixer.music.play(-1)   # loop indefinitely
                self.music_loaded = True
                print("Background music loaded and playing.")
            except Exception as e:
                print(f"Background music not loaded: {e}")

      

        # Message system
        self.main_message = ""
        self.secondary_message = ""
        self._update_messages()
        

        # Menu system
        self.menu_options = ['START GAME', 'HIGH SCORES', 'TABLE SELECTOR', 'AUDIO', 'VIDEO', 'CREDITS', 'EXIT']
        self.selected_option = 0
        self.show_credits = False
        self.show_high_scores = False
        self.credits_text = [ ... ]   # as before
        self.sound_enabled = True   # global sound toggle
        self.high_scores = self.load_high_scores()
        self.high_score = self.high_scores[0][0] if self.high_scores else 0
        self.new_high_score_achieved = False
        self.credits_text = [
            "Wizard's Tower Pinball",
            "",
            "",
            "Design & Programming: Daniel Ducassi",
            "",
            "Music: 'In the Hall of the Mountain King'",
            "by Edvard Grieg",
            "",
            "Graphics: Daniel Ducassi",
            "",
            "Audio: Daniel Ducassi and Nazli Koca"
            "",
            "",
            "Thanks for playing!"
        ]
        self.audio_submenu = False
        self.audio_options = ['SOUND EFFECTS', 'MUSIC', 'BACK']
        self.audio_selected = 0
        self.resume_game = False
        self.entry_name = ""
        self.entry_score = 0
        

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

        try:
            edge_vert = pygame.image.load(os.path.join(base_dir, 'edge_vert.png')).convert_alpha()
            self.edge_vert_texture = edge_vert
            print("Vertical edge texture loaded")
        except:
            print("edge_vert.png not found")
            self.edge_vert_texture = None

        try:
            edge_horz = pygame.image.load(os.path.join(base_dir, 'edge_horz.png')).convert_alpha()
            self.edge_horz_texture = edge_horz
            print("Horizontal edge texture loaded")
        except:
            print("edge_horz.png not found")
            self.edge_horz_texture = None

        wall_thick = self.settings.lane_wall_thickness

        if self.edge_vert_texture:
            self.edge_vert_texture = pygame.transform.scale(
                self.edge_vert_texture,
                (wall_thick, self.edge_vert_texture.get_height())
            )

        if self.edge_horz_texture:
            self.edge_horz_texture = pygame.transform.scale(
                self.edge_horz_texture,
                (self.edge_horz_texture.get_width(), wall_thick)
        )

        
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

        # Observe score changes

        self.notification_center.add_observer('score_changed', self.on_score_changed)

        
        # Observe bumper hits
        self.notification_center.add_observer('bumper_hit', self.on_bumper_hit)
        self.notification_center.add_observer('large_bumper_hit', self.on_large_bumper_hit)

        # Ball
        self.lives = 3
        

        # Flippers
        self.fl = Flipper(
            2/7 * self.settings.playfield_width,
            self.playfield_y + self.settings.playfield_height - 19/140 * self.settings.playfield_height + 1,
            self.settings.f_length, 0.6, True
        )
        self.fr = Flipper(
            5/7 * self.settings.playfield_width,
            self.playfield_y + self.settings.playfield_height - 19/140 * self.settings.playfield_height + 1,
            self.settings.f_length, -0.6, False
        )
        self.flippers = [self.fl, self.fr]

        # Table elements
        self.table_builder = TableBuilder(
            self.settings,
            self.block_texture,
            self.tri_texture,
            self.tri_flipped,
            self.tri_mirrored,
            edge_vert_texture=self.edge_vert_texture,
            edge_horz_texture=self.edge_horz_texture
        )
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

        # Load background
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
        
        # Pre‑tint background for orb colors (custom hues)
        self.bg_tinted = {}
        if self.bg:
            def tint_image(img, color):
                tinted = img.copy()
                color_surf = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
                color_surf.fill(color)
                tinted.blit(color_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                return tinted

            # Custom colors for background
            bg_blue = (30, 205, 255)    # soft cyan‑blue
            bg_red  = (255, 100, 20)     # bright, orangey ed
            bg_white = (255, 255, 255)  # white (can adjust slightly)

            self.bg_tinted[self.settings.blu] = tint_image(self.bg, bg_blue)
            self.bg_tinted[self.settings.red] = tint_image(self.bg, bg_red)
            self.bg_tinted[self.settings.wht] = tint_image(self.bg, bg_white)

            self.current_bg = self.bg_tinted[self.settings.wht]   # start with white
        else:
            self.current_bg = None
         # Overlay surfaces (semi‑transparent tint)
        self.overlay_tinted = {}
        if self.bg:
            overlay_blue = self._make_overlay((10, 15, 255), 25) # Pure Blue Light
            overlay_red  = self._make_overlay((255, 15, 15), 25) # Pure Red Light
            overlay_white = self._make_overlay((255, 255, 255), 0)
            self.overlay_tinted[self.settings.blu] = overlay_blue
            self.overlay_tinted[self.settings.red] = overlay_red
            self.overlay_tinted[self.settings.wht] = overlay_white
            self.current_overlay = self.overlay_tinted[self.settings.wht]
        else:
            self.current_overlay = None

        self.ball_save_active = False
        self.ball_save_start_time = 0
        self.ball_save_duration = 10000  # 10 seconds in milliseconds  

    def _update_menu_options(self):
        if self.resume_game:
            self.menu_options = ['RESUME GAME', 'HIGH SCORES', 'TABLE SELECTOR', 'AUDIO', 'VIDEO', 'CREDITS', 'EXIT']
        else:
            self.menu_options = ['START GAME', 'HIGH SCORES', 'TABLE SELECTOR', 'AUDIO', 'VIDEO', 'CREDITS', 'EXIT']
        # Reset selected option to avoid index errors
        if self.selected_option >= len(self.menu_options):
            self.selected_option = 0

    def load_high_scores(self):
        scores = []
        try:
            with open('highscores.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        scores.append((int(parts[0]), parts[1]))
        except:
            pass
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:5]

    def save_high_score(self, score, name):
        self.high_scores.append((score, name))
        self.high_scores.sort(key=lambda x: x[0], reverse=True)
        self.high_scores = self.high_scores[:5]
        self.high_score = self.high_scores[0][0] if self.high_scores else 0
        try:
            with open('highscores.txt', 'w') as f:
                for s, n in self.high_scores:
                    f.write(f"{s},{n}\n")
        except:
            pass

    def _draw_high_scores(self):
        try:
            font = pygame.font.Font(font_path, 12)
        except:
            font = pygame.font.Font(None, 24)
        start_y = self.settings.top_margin // 2 + 50
        for i, (score, name) in enumerate(self.high_scores):
            text = font.render(f"{i+1}. {score:,}  {name}", True, self.settings.wht)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, start_y + i * 25))
            self.screen.blit(text, text_rect)
        prompt_font = pygame.font.Font(font_path, 8) if font_path else pygame.font.Font(None, 16)
        prompt = prompt_font.render("Press ESC to return", True, self.settings.wht)
        prompt_rect = prompt.get_rect(center=(self.settings.screen_width // 2, start_y + len(self.high_scores) * 25 + 30))
        self.screen.blit(prompt, prompt_rect)
    
    def on_score_changed(self, score):
     # Draw high score, but don't save it yet
     if score > self.high_score:
         self.high_score = score
         self.new_high_score_achieved = True

    # Drawing helpers
    def draw_bumpers(self):
        for bumper in self.bumpers:
            bumper.draw(self.screen)
                
    def draw_blocks(self):
        for block in self.blocks:
            block.draw(self.screen)

    def _draw_menu_options(self):
        try:
            font = pygame.font.Font(font_path, 13)
        except:
            font = pygame.font.Font(None, 24)
        start_y = self.settings.screen_height // 2 # Middle minus rough screen length /2
        for i, option in enumerate(self.menu_options):
            color = self.settings.wht if i != self.selected_option else self.settings.red
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(self.settings.playfield_width // 2, start_y + i * 28))
            self.screen.blit(text, text_rect)

    def _draw_credits(self):
        try:
            font = pygame.font.Font(font_path, 7)
        except:
            font = pygame.font.Font(None, 12)
        start_y = self.settings.top_margin // 2 + 40
        for i, line in enumerate(self.credits_text):
            text = font.render(line, True, self.settings.wht)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, start_y + i * 20))
            self.screen.blit(text, text_rect)
        # small prompt
        prompt_font = pygame.font.Font(font_path, 8) if font_path else pygame.font.Font(None, 16)
        prompt = prompt_font.render("Press ESC to return", True, self.settings.wht)
        prompt_rect = prompt.get_rect(center=(self.settings.screen_width // 2, start_y + len(self.credits_text) * 20 + 30))
        self.screen.blit(prompt, prompt_rect)
    
    def _draw_audio_submenu(self):
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        try:
            font = pygame.font.Font(font_path, 13)
        except:
            font = pygame.font.Font(None, 24)

        start_y = self.settings.screen_height // 2
        for i, option in enumerate(self.audio_options):
            color = self.settings.wht if i != self.audio_selected else self.settings.red
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, start_y + i * 35))
            self.screen.blit(text, text_rect)


    # Color Tint overlays
    def _make_overlay(self, color, alpha=30):
        """Create a semi‑transparent surface of playfield size with given color."""
        surf = pygame.Surface((self.settings.playfield_width, self.settings.playfield_height), pygame.SRCALPHA)
        surf.fill(color + (alpha,))
        return surf
    
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
            
            elif self.state == GameState.NAME_ENTRY:
                self._handle_name_entry_event(event)

    def _handle_menu_event(self, event):
        # Audio submenu takes precedence
        if self.audio_submenu:
            self._handle_audio_submenu_event(event)
            return

        # Handle sub‑screens (credits, high scores)
        if self.show_credits or self.show_high_scores:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.show_credits = False
                self.show_high_scores = False
            return

        # Main menu navigation (only if no sub‑screen active)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                self._select_menu_option()
            elif event.key == pygame.K_ESCAPE:
                if self.resume_game:
                    # Resume game
                    self.resume_game = False
                    self._set_state(GameState.PLAYING)
                else:
                    pygame.quit()
                    sys.exit()
    def _select_menu_option(self):
        option = self.menu_options[self.selected_option]
        if option == 'START GAME':
            self._start_game()
        elif option == 'TABLE SELECTOR':
            self.temp_message = "COMING SOON!"
            self.temp_message_time = pygame.time.get_ticks()
        elif option == 'AUDIO':
            self.audio_submenu = True
            self.audio_selected = 0
            self.temp_message = "SOUND ON" if self.sound_enabled else "SOUND OFF"
            self.temp_message_time = pygame.time.get_ticks()
            if self.sound_enabled:
                self.sound_manager.enable_sound()
            else:
                self.sound_manager.disable_sound()
        elif option == 'VIDEO':
            self.temp_message = "COMING SOON!"
            self.temp_message_time = pygame.time.get_ticks()
        elif option == 'CREDITS':
            self.show_credits = True
        elif option == 'EXIT':
            pygame.quit()
            sys.exit()
        elif option == 'HIGH SCORES':
            self.show_high_scores = True
        elif option == 'RESUME GAME':
            self.resume_game = False
            self._set_state(GameState.PLAYING)

    def _handle_name_entry_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.entry_name:
                self.save_high_score(self.entry_score, self.entry_name.upper())
                self._set_state(GameState.MENU)
                self.entry_name = ""
                self.entry_score = 0
            elif event.key == pygame.K_BACKSPACE:
                self.entry_name = self.entry_name[:-1]
            elif len(self.entry_name) < 3:
                # Accept letters and digits, convert to uppercase
                if event.unicode.isalpha() or event.unicode.isdigit():
                    self.entry_name += event.unicode.upper()

    def _handle_audio_submenu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.audio_selected = (self.audio_selected - 1) % len(self.audio_options)
            elif event.key == pygame.K_DOWN:
                self.audio_selected = (self.audio_selected + 1) % len(self.audio_options)
            elif event.key == pygame.K_RETURN:
                option = self.audio_options[self.audio_selected]
                if option == 'SOUND EFFECTS':
                    self.sound_enabled = not self.sound_enabled
                    if self.sound_enabled:
                        self.sound_manager.enable_sound()
                    else:
                        self.sound_manager.disable_sound()
                    self.temp_message = "SOUND ON" if self.sound_enabled else "SOUND OFF"
                    self.temp_message_time = pygame.time.get_ticks()
                elif option == 'MUSIC':
                    self.music_playing = not self.music_playing
                    if self.music_playing:
                        pygame.mixer.music.set_volume(self.original_music_volume)
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.set_volume(0)
                    self.temp_message = "MUSIC ON" if self.music_playing else "MUSIC OFF"
                    self.temp_message_time = pygame.time.get_ticks()
                elif option == 'BACK':
                    self.audio_submenu = False
            elif event.key == pygame.K_ESCAPE:
                self.audio_submenu = False

    def _handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._start_game()
            elif event.key == pygame.K_ESCAPE:
                self._set_state(GameState.MENU)

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
            elif event.key == pygame.K_ESCAPE:
                self.resume_game = True
                self._set_state(GameState.MENU)

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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self._set_state(GameState.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.resume_game = True
                self._set_state(GameState.MENU)

    # State management
    def _set_state(self, new_state):
        self.state = new_state
        if new_state == GameState.MENU:
            self._update_menu_options()
        self._update_messages()

    def _reset_game_state(self):
        """Reset flippers, bumpers, lights for a fresh game."""
        # Reset flippers
        for flipper in self.flippers:
            flipper.reset()

        # Reset bumpers to initial color (blue)
        for bumper in self.bumpers:
            bumper.color = self.settings.wht

        # Reset lights: turn off and set color to match bumpers' initial
        for light in self.lights:
            light.reset(self.settings.wht)

        # Reset background tint and overlay
        if self.bg_tinted:
            self.current_bg = self.bg_tinted.get(self.settings.wht, self.bg)
        if self.overlay_tinted:
            self.current_overlay = self.overlay_tinted.get(self.settings.wht, self.overlay_tinted[self.settings.wht])

    def _update_messages(self):
        if self.state == GameState.MENU:
            self.main_message = "CAST A SPELL!"
            self.secondary_message = "INSERT COIN"
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
        self.resume_game = False
        self._reset_game_state()
        self._set_state(GameState.PLAYING)
        self.b.reset()
        self.b.trapped = False
        self.score_manager.reset()
        self.lives = 3
        self.ball_save_active = False
        self.new_high_score_achieved = False
        self.entry_name = ""
        self.entry_score = 0
        if self.music_loaded:
            pygame.mixer.music.stop()
            pygame.mixer.music.play(-1)

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
                     # Check if score qualifies for high score list
                     if (len(self.high_scores) < 5 or self.score_manager.score > min(s for s,_ in self.high_scores)):
                         self.entry_score = self.score_manager.score
                         self.entry_name = ""
                         self._set_state(GameState.NAME_ENTRY)
                     else:
                         self._set_state(GameState.GAME_OVER)
                     winsound.Beep(640, 200)
                     winsound.Beep(440, 200)
                     winsound.Beep(640, 200)
                     winsound.Beep(440, 200)

            # Update lights
            for light in self.lights:
                light.update(pygame.time.get_ticks())
                


    def on_bumper_hit(self, bumper):
        if self.state != GameState.PLAYING:
            return

        # Update corresponding light's color and turn it on
        try:
            idx = self.bumpers.index(bumper)
            if idx < len(self.lights):
                light = self.lights[idx]
                light.set_color(bumper.color)
                light.turn_on(pygame.time.get_ticks())
        except ValueError:
            pass

        # Generate message
        if bumper.radius > 20:
            if bumper.color == self.settings.blu:
                msg = "ORB OF POWER!"
            elif bumper.color == self.settings.red:
                msg = "FIREBALL!"
            elif bumper.color == self.settings.wht:
                msg = "BALL LIGHTNING!"
            else:
                msg = ""
        else:
            msg = random.choice(["BOOM!", "HISS!", "POP!", "ZAP!", "BUZZ!"])
        if msg:
            self.temp_message = msg
            self.temp_message_time = pygame.time.get_ticks()

    def on_large_bumper_hit(self, color):
        for bumper in self.bumpers:
            bumper.color = color
        for light in self.lights:
            light.set_color(color)
        # Update background tint
        if self.bg_tinted:
            self.current_bg = self.bg_tinted.get(color, self.bg)
        # Update overlay
        if self.overlay_tinted:
            self.current_overlay = self.overlay_tinted.get(color, self.overlay_tinted[self.settings.wht])

    # Drawing
    def _draw(self):
        self.screen.fill((0, 0, 0))
         # Draw playfield background
        if self.current_bg:
            self.screen.blit(self.current_bg, (0, self.playfield_y))
        
        # Draw lane background (right side)
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
        # Draw overlay (semi‑transparent tint)
        if self.current_overlay:
            self.screen.blit(self.current_overlay, (0, self.playfield_y))
       

        # Title
        try:
            title_font = pygame.font.Font(font_path, 12)
        except:
            title_font = pygame.font.Font(None, 36)
        title_text = title_font.render("THE WIZARD'S TOWER", True, self.settings.wht)
        title_rect = title_text.get_rect(center=(self.settings.screen_width // 2, self.settings.top_margin // 5))
        self.screen.blit(title_text, title_rect)

        # Score and lives

        if self.score_manager.score > 1000000:
            try:
                f = pygame.font.Font(font_path, 8)
            except:
                f = pygame.font.Font(None, 16)
        else:
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
            high_font = pygame.font.Font(font_path, 6)   # smaller font
        except:
            high_font = pygame.font.Font(None, 24)      # fallback
        high_text = high_font.render(f'HIGH: {self.high_score:,}', True, self.settings.wht)
        self.screen.blit(high_text, (self.settings.screen_width - 110, 90))
       
        # Context messages
        self._draw_messages()
        
        # Draw credits overlay if needed
        if self.state == GameState.MENU and self.show_credits:
            # Draw a semi‑transparent overlay
            overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            self._draw_credits()
        if self.state == GameState.MENU and self.show_high_scores:
            overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            self._draw_high_scores()
        if self.state == GameState.NAME_ENTRY:
            self._draw_name_entry()
        
        # Draw audio submenu
        if self.state == GameState.MENU and self.audio_submenu:
            self._draw_audio_submenu()

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
                # Draw menu options if in MENU state and not showing credits
        
        if self.state == GameState.MENU and not self.show_credits:
            self._draw_menu_options()
    
    def _draw_name_entry(self):
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        try:
            font = pygame.font.Font(font_path, 14)
            small_font = pygame.font.Font(font_path, 12)
        except:
            font = pygame.font.Font(None, 24)
            small_font = pygame.font.Font(None, 20)

        # "NEW HIGH SCORE!" title
        prompt = font.render("NEW HIGH SCORE!", True, self.settings.wht)
        prompt_rect = prompt.get_rect(center=(self.settings.screen_width // 2, self.settings.top_margin // 2))
        self.screen.blit(prompt, prompt_rect)

        # Static instruction
        instruction = small_font.render("ENTER YOUR NAME:", True, self.settings.wht)
        inst_rect = instruction.get_rect(center=(self.settings.screen_width // 2,
                                                 self.settings.top_margin // 2 + 50))
        self.screen.blit(instruction, inst_rect)

        # Display the entered name (uppercase) on a new line
        name_display = self.entry_name.upper() + ("_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " ")
        name_text = small_font.render(name_display, True, self.settings.wht)
        name_rect = name_text.get_rect(center=(self.settings.screen_width // 2,
                                                self.settings.top_margin // 2 + 85))
        self.screen.blit(name_text, name_rect)

        # Display the score
        score_text = small_font.render(f"SCORE: {self.entry_score:,}", True, self.settings.wht)
        score_rect = score_text.get_rect(center=(self.settings.screen_width // 2,
                                                  self.settings.top_margin // 2 + 130))
        self.screen.blit(score_text, score_rect)
    
    
    
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