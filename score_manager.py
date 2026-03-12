class ScoreManager:
    def __init__(self, notification_center, settings):
        self.notification_center = notification_center
        self.settings = settings
        self.score = 0
        # Observe bumper hits
        self.notification_center.add_observer('bumper_hit', self.on_bumper_hit)

    def on_bumper_hit(self, bumper):
        self.score += self.settings.pph
        # Cycle bumper color
        if bumper.c == self.settings.red:
            bumper.c = self.settings.blu
        elif bumper.c == self.settings.blu:
            bumper.c = self.settings.ylw
        elif bumper.c == self.settings.ylw:
            bumper.c = self.settings.red
        # Optionally post a score changed notification for UI
        self.notification_center.post_notification('score_changed', self.score)

    def reset(self):
        self.score = 0