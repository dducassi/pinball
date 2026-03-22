import pygame
import os

class SoundManager:
    def __init__(self, notification_center, base_dir):
        self.notification_center = notification_center
        self.base_dir = base_dir
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
            self.launch_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'launch.wav'))
        except:
            self.launch_sound = None
        try:
            self.ball_lost_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'ball_lost.wav'))
        except:
            self.ball_lost_sound = None
        try:
            self.save_sound = pygame.mixer.Sound(os.path.join(self.base_dir, 'save.wav'))
        except:
            self.save_sound = None

    def _register_observers(self):
        self.notification_center.add_observer('bumper_hit', self.on_bumper_hit)
        self.notification_center.add_observer('flipper_click', self.on_flipper_click)
        self.notification_center.add_observer('ball_launch', self.on_ball_launch)
        self.notification_center.add_observer('ball_lost', self.on_ball_lost)
        self.notification_center.add_observer('ball_saved', self.on_ball_saved)

    def on_bumper_hit(self, bumper):
        if self.bumper_sound:
            self.bumper_sound.play()

    def on_flipper_click(self, flipper):
        if self.flipper_sound:
            self.flipper_sound.play()

    def on_ball_launch(self, data):
        if self.launch_sound:
            self.launch_sound.play()

    def on_ball_lost(self, data):
        if self.ball_lost_sound:
            self.ball_lost_sound.play()

    def on_ball_saved(self, data):
        if self.save_sound:
            self.save_sound.play()