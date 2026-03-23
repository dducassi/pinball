class ScoreManager:
    def __init__(self, notification_center, settings):
        self.notification_center = notification_center
        self.settings = settings
        self.score = 0
        self.notification_center.add_observer('bumper_hit', self.on_bumper_hit)

    def on_bumper_hit(self, bumper):
        if bumper.radius > 20:
            self.score += self.settings.pph * 10
        elif 5.5 < bumper.radius < 15:
            self.score += self.settings.pph * 2
        elif bumper.radius < 6:
            self.score += self.settings.pph * 3
        else:
            self.score += self.settings.pph //2

        # Cycle bumper color (only for bumpers with radius > 5)
        if bumper.radius > 5:
            if bumper.color == self.settings.red:
                new_color = self.settings.blu
            elif bumper.color == self.settings.blu:
                new_color = self.settings.wht
            else:  # white
                new_color = self.settings.red
            bumper.color = new_color

            # If it's a large bumper, notify others to sync colors
            if bumper.radius > 20:
                self.notification_center.post_notification('large_bumper_hit', new_color)

        self.notification_center.post_notification('score_changed', self.score)

    def reset(self):
        self.score = 0

    def load_high_score(self):
        """Load high score from file, return 0 if file missing or error."""
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self):
        """Save current high score to file."""
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            print("Could not save high score.")

    def on_score_changed(self, score):
        """Callback when score changes: update high score if needed."""
        if score > self.high_score:
            self.high_score = score
            self.save_high_score()