import pygame
import os
import winsound

class SoundManager:
    def __init__(self, notification_center, base_dir):
        self.notification_center = notification_center
        self.base_dir = base_dir
        self.effects_enabled = True          # only for sound effects
        self._load_sounds()
        self._register_observers()

    def _load_sounds(self):
        # Use absolute paths (base_dir is the script directory)
        try:
            self.bumper_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'bumper.wav'))
        except:
            self.bumper_sound = None
        try:
            self.flipper_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'flipper.wav'))
        except:
            self.flipper_sound = None
        try:
            self.launch_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'launch.ogg'))
        except:
            self.launch_sound = None
        try:
            self.ball_lost_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'ball_lost.ogg'))
        except:
            self.ball_lost_sound = None
        try:
            self.save_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'ball_save.ogg'))
        except:
            self.save_sound = None
        try:
            self.block_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'block_sound.wav'))
        except:
            self.block_sound = None
        try:
            self.game_over_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'game_over_sound.ogg'))
        except:
            self.game_over_sound = None

    def _register_observers(self):
        self.notification_center.add_observer('bumper_hit', self.on_bumper_hit)
        self.notification_center.add_observer('flipper_click', self.on_flipper_click)
        self.notification_center.add_observer('ball_launch', self.on_ball_launch)
        self.notification_center.add_observer('ball_lost', self.on_ball_lost)
        self.notification_center.add_observer('ball_saved', self.on_ball_saved)
        self.notification_center.add_observer('block_hit', self.on_block_hit)
        self.notification_center.add_observer('game_over', self.on_game_over)

    # Toggle Effects

    def enable_effects(self):
        self.effects_enabled = True

    def disable_effects(self):
        self.effects_enabled = False

    # Sound Effects

    def on_bumper_hit(self, bumper):
        if not self.effects_enabled:
            return
        if self.bumper_sound:
            self.bumper_sound.play()
        

    def on_flipper_click(self, flipper):
        if not self.effects_enabled:
            return
        if self.flipper_sound:
            self.flipper_sound.play()

    def on_ball_launch(self, data):
        if not self.effects_enabled:
            return
        if self.launch_sound:
            self.launch_sound.play()

    def on_ball_lost(self, data):
        if not self.effects_enabled:
            return
        if self.ball_lost_sound:
            self.ball_lost_sound.play()

    def on_ball_saved(self, data):
        if not self.effects_enabled:
            return
        if self.save_sound:
            self.save_sound.play()
           

    def on_block_hit(self, block):
        if not self.effects_enabled:
            return
        if self.block_sound:
            self.block_sound.play()
    
    def on_game_over(self, data=None):
        if not self.effects_enabled:
            return
        if self.game_over_sound:
            self.game_over_sound.play()
    