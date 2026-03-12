from obstacles import Obstacle
from blocks import Block

class TableBuilder:
    def __init__(self, settings):
        self.settings = settings

    def generate_obstacles(self):
        """Return a list of obstacles for the table."""
        obs = []
        # Original gen_obs logic
        x = self.settings.screen_width / 2
        y = (self.settings.screen_height) / 5
        c = self.settings.blu
        obs.append(Obstacle(x, y, c))

        x = 0
        y = 0
        c = self.settings.blu
        obs.append(Obstacle(x, y, c))

        x = self.settings.screen_width
        y = 0
        c = self.settings.blu
        obs.append(Obstacle(x, y, c))

        x = .22 * self.settings.orad
        y = 6/7 * (self.settings.screen_height)
        c = self.settings.blu
        obs.append(Obstacle(x, y, c))

        x = self.settings.screen_width - .22 * self.settings.orad
        y = 6/7 * (self.settings.screen_height)
        c = self.settings.blu
        obs.append(Obstacle(x, y, c))

        return obs

    def generate_blocks(self):
        """Return a list of blocks for the table."""
        blocks = []
        # Left lower block
        x1 = 0
        y1 = self.settings.screen_height
        x2 = 0
        y2 = self.settings.screen_height - (3/14) * self.settings.screen_height
        x3 = (2/7) * self.settings.screen_width
        y3 = self.settings.screen_height - (1/14) * self.settings.screen_height
        x4 = (2/7) * self.settings.screen_width
        y4 = self.settings.screen_height
        c = self.settings.gry
        blocks.append(Block(x1, y1, x2, y2, x3, y3, x4, y4, c))

        # Right lower block
        x1 = self.settings.screen_width
        y1 = self.settings.screen_height
        x2 = self.settings.screen_width
        y2 = self.settings.screen_height - (3/14) * self.settings.screen_height
        x3 = self.settings.screen_width - (2/7) * self.settings.screen_width
        y3 = self.settings.screen_height - (1/14) * self.settings.screen_height
        x4 = self.settings.screen_width - (2/7) * self.settings.screen_width
        y4 = self.settings.screen_height
        c = self.settings.gry
        blocks.append(Block(x1, y1, x2, y2, x3, y3, x4, y4, c))

        return blocks