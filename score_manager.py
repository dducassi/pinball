class ScoreManager:
    def __init__(self, notification_center, settings):
        self.notification_center = notification_center
        self.settings = settings
        self.score = 0

   

    def add_points(self, points):
        self.score += points
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