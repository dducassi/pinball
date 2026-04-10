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
from table import Table
from table import TableManager
from notification_center import NotificationCenter
from score_manager import ScoreManager
from sound_manager import SoundManager

from time import sleep
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

        # Resizable window and virtual surface
        self.display = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height),
            pygame.RESIZABLE
        )
        self.screen = pygame.Surface((self.settings.screen_width, self.settings.screen_height))
        self.playfield_x = 0
        self.playfield_y = self.settings.top_margin

        # Shared images (textures, bumpers, ball, flipper)
        self.images = {}
        self._load_shared_images()

        pygame.display.set_caption('Wizard Pinball')

        

        self.notification_center = NotificationCenter()
        self.score_manager = ScoreManager(self.notification_center, self.settings)
        self.sound_manager = SoundManager(self.notification_center, base_dir)

        # Load background music (but don't play yet)
        self.music_loaded = False
        self.music_playing = True
        self.original_music_volume = self.settings.music_volume

        try:
            music_path = os.path.join(base_dir, 'music.ogg')
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.original_music_volume)
            # REMOVED: pygame.mixer.music.play(-1)
            self.music_loaded = True
            print("Background music loaded (not playing).")
        except Exception as e:
            print(f"Background music not loaded: {e}")

        # Set blank background to start
        self.bg = None

        # Start in menu
        self.state = GameState.MENU

        # Observers
        self.notification_center.add_observer('score_changed', self.on_score_changed)
        self.notification_center.add_observer('bumper_hit', self.on_bumper_hit)
        self.notification_center.add_observer('large_bumper_hit', self.on_large_bumper_hit)

        self.lives = 3

        self.table_manager = TableManager(self.settings, base_dir)

        # Placeholders (will be filled by _load_table)
        self.blocks = []
        self.bumpers = []
        self.lights = []
        self.lane_center = 0
        self.lane_bottom = 0
        self.plunger = None
        self.flippers = []
        self.b = None
        self.physics_engine = None

        # Load the current table (creates ball, flippers, plunger, etc.)
        self._load_table(self.table_manager.get_current_table())

        # Ball save timer
        self.ball_save_active = False
        self.ball_save_start_time = 0
        self.ball_save_duration = 10000

        

        # Message system
        self.main_message = ""
        self.secondary_message = ""
        self._update_messages()

        # Menu system
        self.menu_options = ['START GAME', 'HIGH SCORES', 'TABLE SELECTOR', 'AUDIO', 'VIDEO', 'CREDITS', 'EXIT']
        self.selected_option = 0
        self.show_credits = False
        self.show_high_scores = False
        self.high_scores = self.load_high_scores()
        self.high_score = self.high_scores[0][0] if self.high_scores else 0
        self.new_high_score_achieved = False
        self.credits_text = [ ... ]   # unchanged
        self.audio_submenu = False
        self.audio_options = ['SOUND EFFECTS', 'MUSIC', 'BACK']
        self.audio_selected = 0
        self.resume_game = False
        self.entry_name = ""
        self.entry_score = 0

        # Temporary message system
        self.temp_message = ""
        self.temp_message_time = 0
        self.temp_message_duration = 2000
        
    def _update_menu_options(self):
        if self.resume_game:
            self.menu_options = ['RESUME GAME', 'HIGH SCORES', 'AUDIO', 'VIDEO', 'CREDITS', 'EXIT']
        else:
            self.menu_options = ['START GAME', 'HIGH SCORES', 'TABLE SELECTOR', 'AUDIO', 'VIDEO', 'CREDITS', 'EXIT']
        # Reset selected option to avoid index errors
        if self.selected_option >= len(self.menu_options):
            self.selected_option = 0

    def _load_shared_images(self):
        """Load all images used by tables (textures, bumpers, ball, flipper, etc.)."""
        # Helper to load and optionally scale an image
        def load_img(filename, scale=None, convert_alpha=True):
            path = os.path.join(base_dir, filename)
            try:
                if convert_alpha:
                    img = pygame.image.load(path).convert_alpha()
                else:
                    img = pygame.image.load(path).convert()
                if scale:
                    img = pygame.transform.scale(img, scale)
                return img
            except Exception as e:
                print(f"Could not load {filename}: {e}")
                return None

        # Block textures
        self.images['block_texture'] = load_img('block_texture.png', convert_alpha=False)
        self.images['tri_texture'] = load_img('tri_image.png')
        if self.images['tri_texture']:
            self.images['tri_flipped'] = pygame.transform.flip(self.images['tri_texture'], True, False)
            self.images['tri_mirrored'] = pygame.transform.flip(self.images['tri_texture'], False, True)
        else:
            self.images['tri_flipped'] = None
            self.images['tri_mirrored'] = None

        self.images['edge_vert_texture'] = load_img('edge_vert.png')
        self.images['edge_horz_texture'] = load_img('edge_horz.png')

        # Bumper images
        self.images['orb_image'] = load_img('crystal_orb.png', scale=(180,180))
        self.images['small_orb_image'] = load_img('small_orb.png')
        self.images['tiny_bumper_image'] = load_img('tiny_bumper.png')
        self.images['light_image'] = load_img('light.png')

        # Ball and flipper
        self.images['ball_image'] = load_img('pinball.png')
        self.images['flipper_image'] = load_img('flipper.png')

        # Backgrounds (loaded per‑table, uses default wizard background)
        # Tables loaded in _load_table.

    def _load_table(self, table):
        builder = table.builder_class(self.settings, self.images)
        blocks = builder.generate_blocks()
        bumpers, lights = builder.generate_bumpers(self.images)
        lane_center = builder.get_lane_center()
        lane_bottom = builder.get_lane_bottom()
        plunger_y = builder.get_plunger_base_y()

        self.blocks = blocks
        self.bumpers = bumpers
        self.lights = lights
        self.lane_center = lane_center
        self.lane_bottom = lane_bottom

        self.current_table_title = table.title
        self.current_tagline = table.tagline
        self._update_messages() 

        # --- Recreate flippers (their positions depend on playfield dimensions) ---
        # Use the same formulas as before, but now flipper_image comes from self.images
        flipper_img = self.images.get('flipper_image')
        self.fl = Flipper(
            2/7 * self.settings.playfield_width,
            self.playfield_y + self.settings.playfield_height - 19/140 * self.settings.playfield_height + 1,
            self.settings.f_length, 0.6, True,
            image=flipper_img
        )
        self.fr = Flipper(
            5/7 * self.settings.playfield_width,
            self.playfield_y + self.settings.playfield_height - 19/140 * self.settings.playfield_height + 1,
            self.settings.f_length, -0.6, False,
            image=flipper_img
        )
        self.flippers = [self.fl, self.fr]

        # --- Recreate plunger ---
        self.plunger = Plunger(
            lane_center,
            plunger_y,
            max_pull=100,
            pull_speed=5,
            max_launch_speed=15
        )

        # --- Recreate ball ---
        ball_image = self.images.get('ball_image') if table.use_ball_image else None
        self.b = Ball(self, ball_image)
        self.b.lane_x_center = lane_center
        self.b.lane_bottom = lane_bottom
        self.b.reset()

        # --- Recreate physics engine ---
        self.physics_engine = PhysicsEngine(
            self.b, self.flippers, self.bumpers, self.blocks,
            self.settings, self.notification_center
        )

        # --- Load table‑specific background ---
        if hasattr(table, 'bg_path') and table.bg_path:
            # Load custom background
            self.bg = pygame.image.load(table.bg_path).convert()
            self.bg = pygame.transform.scale(self.bg, (self.settings.playfield_width, self.settings.playfield_height))
            self.lane_bg = pygame.image.load(table.lane_bg_path).convert()
            self.lane_bg = pygame.transform.scale(self.lane_bg, (self.settings.playfield_width, self.settings.playfield_height))
        elif table.bg_path is None:
            # Explicitly no background (black)
            self.bg = None
            self.lane_bg = None
        else:
            # Default wizard backgrounds (fallback)
            if not self.test_mode:
                self.bg = pygame.image.load(os.path.join(base_dir, 'wizard.png')).convert()
                self.bg = pygame.transform.scale(self.bg, (self.settings.playfield_width, self.settings.playfield_height))
                self.lane_bg = pygame.image.load(os.path.join(base_dir, 'lane_bg.png')).convert()
                self.lane_bg = pygame.transform.scale(self.lane_bg, (self.settings.playfield_width, self.settings.playfield_height))
            else:
                self.bg = None
                self.lane_bg = None

        # Re‑create tinted backgrounds and overlays (depends on self.bg)
        self._pre_tint_background()

        # Change music for level (load but don't play)
        if hasattr(table, 'music_path') and table.music_path:
            self.sound_manager.change_music(table.music_path)
            self.music_loaded = True
        else:
            # No music for this table: stop any playing and mark as not loaded
            pygame.mixer.music.stop()
            self.music_loaded = False
        
        # Change table title
        self.current_table_title = table.title
        self.current_tagline = table.tagline
        self._update_messages()
    
    def _pre_tint_background(self):
        """Build tinted versions of the current background for orb color effects."""
        self.bg_tinted = {}
        if self.bg:
            def tint_image(img, color):
                tinted = img.copy()
                color_surf = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
                color_surf.fill(color)
                tinted.blit(color_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                return tinted

            bg_blue = (30, 205, 255)
            bg_red  = (255, 100, 20)
            bg_white = (255, 255, 255)

            self.bg_tinted[self.settings.blu] = tint_image(self.bg, bg_blue)
            self.bg_tinted[self.settings.red] = tint_image(self.bg, bg_red)
            self.bg_tinted[self.settings.wht] = tint_image(self.bg, bg_white)

            self.current_bg = self.bg_tinted[self.settings.wht]
        else:
            self.current_bg = None

        self.overlay_tinted = {}
        if self.bg:
            self.overlay_tinted[self.settings.blu] = self._make_overlay((10, 15, 255), 25)
            self.overlay_tinted[self.settings.red] = self._make_overlay((255, 15, 15), 25)
            self.overlay_tinted[self.settings.wht] = self._make_overlay((255, 255, 255), 0)
            self.current_overlay = self.overlay_tinted[self.settings.wht]
        else:
            self.current_overlay = None

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
            if event.type == pygame.VIDEORESIZE:
                self.display = pygame.display.set_mode(event.size, pygame.RESIZABLE)
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
            elif self.state == GameState.TABLE_SELECTOR:
                self._handle_table_selector_event(event)
            

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
            self._set_state(GameState.TABLE_SELECTOR)
        elif option == 'AUDIO':
            self.audio_submenu = True
            self.audio_selected = 0
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
                        if self.sound_manager.effects_enabled:
                            self.sound_manager.disable_effects()
                        else:
                            self.sound_manager.enable_effects()
                        self.temp_message = "SOUND ON" if self.sound_manager.effects_enabled else "SOUND OFF"
                        self.temp_message_time = pygame.time.get_ticks()
                        print("Sound effects:", self.sound_manager.effects_enabled)
                        print("Music playing:", self.music_playing)
                    elif option == 'MUSIC':
                        if not self.music_loaded:
                            self.temp_message = "MUSIC NOT AVAILABLE"
                            self.temp_message_time = pygame.time.get_ticks()
                        else:
                            self.music_playing = not self.music_playing
                            if self.music_playing:
                                pygame.mixer.music.set_volume(self.original_music_volume)
                                pygame.mixer.music.play(-1)
                            else:
                                pygame.mixer.music.stop()
                            self.temp_message = "MUSIC ON" if self.music_playing else "MUSIC OFF"
                            self.temp_message_time = pygame.time.get_ticks()
                    elif option == 'BACK':
                        self.audio_submenu = False
                elif event.key == pygame.K_ESCAPE:
                    self.audio_submenu = False

    def _handle_table_selector_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.table_manager.prev_table()
                self._load_table(self.table_manager.get_current_table())
                self.current_table_title = self.table_manager.get_current_table().title
                self.current_tagline = self.table_manager.get_current_table().tagline
            elif event.key == pygame.K_RIGHT:
                self.table_manager.next_table()
                self._load_table(self.table_manager.get_current_table())
                self.current_table_title = self.table_manager.get_current_table().title
                self.current_tagline = self.table_manager.get_current_table().tagline
            elif event.key == pygame.K_RETURN:
                # Select current table and return to menu
                self._set_state(GameState.MENU)
            elif event.key == pygame.K_ESCAPE:
                # Cancel: reload the originally selected table? Or just return without changing?
                # Simpler: just return to menu (current table remains as last cycled)
                self._set_state(GameState.MENU)

    def _handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._start_game()
            elif event.key == pygame.K_ESCAPE:
                if self.music_loaded and self.music_playing:
                    pygame.mixer.music.stop()
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

        # Get the current table's starting color
        current_table = self.table_manager.get_current_table()
        if current_table.color_cycle and len(current_table.color_cycle) > 0:
            initial_color = current_table.color_cycle[0]

        # Reset bumpers to the initial color
        if current_table.color_cycle:
            for bumper in self.bumpers:
                bumper.color = initial_color

        # Reset lights: turn off and set color to match bumpers' initial
        if current_table.color_cycle:
            for light in self.lights:
                light.reset(initial_color)

        # Reset background tint and overlay
        if self.bg_tinted:
            self.current_bg = self.bg_tinted.get(initial_color, self.bg)
        if self.overlay_tinted:
            self.current_overlay = self.overlay_tinted.get(initial_color, self.overlay_tinted[self.settings.wht])

    def _update_messages(self):
        if self.state == GameState.MENU:
            self.main_message = self.current_tagline
            self.secondary_message = "INSERT COIN"
        elif self.state == GameState.PAUSED:
            self.main_message = "PAUSED"
            self.secondary_message = ""
        elif self.state == GameState.GAME_OVER:
            self.main_message = "GAME OVER"
            self.secondary_message = "'ENTER' TO INSERT COIN"
            self.music_playing = False

        else:  # PLAYING
            self.main_message = ""
            self.secondary_message = ""

    

    # Game start
    def _start_game(self):
        current_table = self.table_manager.get_current_table()
        if self.music_loaded and self.music_playing and current_table.music_path:
            pygame.mixer.music.play(-1)
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
                     self.notification_center.post_notification('game_over')
                     # Check if score qualifies for high score list
                     if (len(self.high_scores) < 5 or self.score_manager.score > min(s for s,_ in self.high_scores)):
                         self.entry_score = self.score_manager.score
                         self.entry_name = ""
                         self._set_state(GameState.NAME_ENTRY)
                     else:
                         self._set_state(GameState.GAME_OVER)
                         
                

            # Update lights
            for light in self.lights:
                light.update(pygame.time.get_ticks())
                


    def on_bumper_hit(self, bumper):
        if self.state != GameState.PLAYING:
            return

        current_table = self.table_manager.get_current_table()

        # 1. Update the hit bumper's color (cycle if table has color_cycle)
        new_color = None
        if current_table.color_cycle and bumper.radius > 5:  # cycle only for bumpers that can change
            # Cycle to next color in the table's list
            if bumper.color in current_table.color_cycle:
                idx = current_table.color_cycle.index(bumper.color)
                new_color = current_table.color_cycle[(idx + 1) % len(current_table.color_cycle)]
            else:
                new_color = current_table.color_cycle[0]
            bumper.color = new_color

        # 2. Update the corresponding light's color and turn it on
        try:
            idx = self.bumpers.index(bumper)
            if idx < len(self.lights):
                light = self.lights[idx]
                light.set_color(bumper.color)
                light.turn_on(pygame.time.get_ticks())
        except ValueError:
            pass

        # 3. If it's a large bumper, notify all other bumpers to sync colors
        if bumper.radius > 20 and new_color is not None:
            self.notification_center.post_notification('large_bumper_hit', new_color)

        # 4. Generate a temporary message (small or large)
        msg = None
        if bumper.radius > 20:
            msg = current_table.large_bumper_messages.get(bumper.color)
        else:
            if current_table.small_bumper_messages:
                msg = random.choice(current_table.small_bumper_messages)
        if msg:
            self.temp_message = msg
            self.temp_message_time = pygame.time.get_ticks()

    def on_large_bumper_hit(self, color):
        current_table = self.table_manager.get_current_table()
        if not current_table.color_cycle:
            return  # no cycling for this table

        # Propagate the new color to all bumpers and lights
        for bumper in self.bumpers:
            bumper.color = color
        for light in self.lights:
            light.set_color(color)

        # Update background tint and overlay if enabled
        if current_table.tint_background and self.bg_tinted:
            self.current_bg = self.bg_tinted.get(color, self.bg)
        if current_table.tint_background and self.overlay_tinted:
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
        title_text = title_font.render(self.current_table_title, True, self.settings.wht)
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

        # Scale the virtual surface to the current window size
        win_w, win_h = self.display.get_size()
        virt_w, virt_h = self.screen.get_size()
        scale = min(win_w / virt_w, win_h / virt_h)
        new_w, new_h = int(virt_w * scale), int(virt_h * scale)
        scaled = pygame.transform.scale(self.screen, (new_w, new_h))
        x = (win_w - new_w) // 2
        y = (win_h - new_h) // 2
        self.display.fill((0, 0, 0))   # clear borders
        self.display.blit(scaled, (x, y))
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

    def _draw_table_selector(self):
        # Draw everything normally (the table, bumpers, blocks, etc.)
        # Clear screen and draw playfield background, blocks, bumpers, ball, flippers, etc.
        self.screen.fill((0, 0, 0))
        if self.current_bg:
            self.screen.blit(self.current_bg, (0, self.playfield_y))
        if self.lane_bg:
            self.screen.blit(self.lane_bg, (self.settings.playfield_width, self.playfield_y))
        self.b.draw_ball()
        for light in self.lights:
            light.draw(self.screen)
        self.draw_bumpers()
        self.plunger.draw(self.screen)
        self.draw_blocks()
        self.fl.draw(self.screen)
        self.fr.draw(self.screen)
        if self.current_overlay:
            self.screen.blit(self.current_overlay, (0, self.playfield_y))

        # Title (dynamic)
        try:
            title_font = pygame.font.Font(font_path, 12)
        except:
            title_font = pygame.font.Font(None, 36)
        title_text = title_font.render(self.current_table_title, True, self.settings.wht)
        title_rect = title_text.get_rect(center=(self.settings.screen_width // 2, self.settings.top_margin // 5))
        self.screen.blit(title_text, title_rect)

        # Score and lives (optional, but we can show placeholder or nothing)
        # For simplicity, skip showing scores in selector mode.

        # Instructions overlay (semi-transparent bar at bottom)
        instr_surf = pygame.Surface((self.settings.screen_width, 40), pygame.SRCALPHA)
        instr_surf.fill((0, 0, 0, 180))
        self.screen.blit(instr_surf, (0, self.settings.screen_height - 40))
        try:
            instr_font = pygame.font.Font(font_path, 10)
        except:
            instr_font = pygame.font.Font(None, 18)
        instr_text = instr_font.render("LEFT / RIGHT to change table   ENTER to select   ESC to cancel", True, self.settings.wht)
        instr_rect = instr_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height - 20))
        self.screen.blit(instr_text, instr_rect)
        
    
    
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