from bumpers import Bumper
from blocks import Block

class TableBuilder:
    def __init__(self, settings):
        self.settings = settings

    def generate_bumpers(self):
        """Return a list of bumpers for the table."""
        bumpers = []
        x = self.settings.screen_width / 2
        y = (self.settings.screen_height) / 5
        c = self.settings.blu
        bumpers.append(Bumper(x, y, c))   # using Bumper

        x = 0
        y = 0
        c = self.settings.blu
        bumpers.append(Bumper(x, y, c))

        x = self.settings.screen_width
        y = 0
        c = self.settings.blu
        bumpers.append(Bumper(x, y, c))

        x = .22 * self.settings.bump_rad
        y = 6/7 * (self.settings.screen_height)
        c = self.settings.blu
        bumpers.append(Bumper(x, y, c))

        x = self.settings.screen_width - .22 * self.settings.bump_rad
        y = 6/7 * (self.settings.screen_height)
        c = self.settings.blu
        bumpers.append(Bumper(x, y, c))

        return bumpers


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