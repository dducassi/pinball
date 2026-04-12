import pygame
import os

class SoundManager:
    def __init__(self, notification_center, base_dir):
        self.notification_center = notification_center
        self.base_dir = base_dir
        self.effects_enabled = True
        self.sounds = {}          # stores loaded Sound objects for current table
        self.music_loaded = False
        self._load_default_music()

    def load_table_sounds(self, sound_dict):
        """Load all sounds for a table. sound_dict: {'bumper': 'bumper.wav', ...}"""
        self.sounds = {}
        for key, filename in sound_dict.items():
            path = os.path.join(self.base_dir, filename)
            try:
                self.sounds[key] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Could not load sound {filename}: {e}")
                self.sounds[key] = None

    def play(self, key):
        if not self.effects_enabled:
            return
        sound = self.sounds.get(key)
        if sound:
            sound.play()

    def enable_effects(self):
        self.effects_enabled = True

    def disable_effects(self):
        self.effects_enabled = False

    def _load_default_music(self):
        try:
            music_path = os.path.join(self.base_dir, 'music.ogg')
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.8)
            self.music_loaded = True
        except:
            self.music_loaded = False

    def change_music(self, music_path):
        if not music_path or not self.music_loaded:
            return
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)
        except:
            pass