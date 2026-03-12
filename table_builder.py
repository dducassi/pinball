from bumpers import Bumper
from blocks import Block

class TableBuilder:
    def __init__(self, settings):
        self.settings = settings

    def generate_bumpers(self):
        """Return a list of bumpers for the table."""
        bumpers = []

        # Central orb bumper
        x = self.settings.screen_width / 2
        y = (self.settings.screen_height) / 5
        c = self.settings.blu
        bumpers.append(Bumper(x, y, c))   

        # Top left bumper
        x = 0
        y = 0
        c = self.settings.blu
        bumpers.append(Bumper(x, y, c))


        # Top right bumper
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
        w = self.settings.screen_width
        h = self.settings.screen_height

        # Left lower block vertices (order: bottom-left, top-left, top-right, bottom-right)
        left_vertices = [
            (0, h),
            (0, h - 3/14 * h),
            (2/7 * w, h - 1/14 * h),
            (2/7 * w, h)
        ]
        blocks.append(Block(left_vertices, self.settings.gry, bounce=self.settings.block_bounce))

        # Right lower block vertices
        right_vertices = [
            (w, h),
            (w, h - 3/14 * h),
            (w - 2/7 * w, h - 1/14 * h),
            (w - 2/7 * w, h)
        ]
        blocks.append(Block(right_vertices, self.settings.gry, bounce=self.settings.block_bounce))

        return blocks