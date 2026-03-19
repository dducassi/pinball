from bumpers import Bumper
from blocks import Block

class TableBuilder:
    def __init__(self, settings):
        self.settings = settings
        self.playfield_width = settings.playfield_width
        self.playfield_height = settings.playfield_height
        self.top_margin = settings.top_margin
        self.right_margin = settings.right_margin
        self.screen_width = settings.screen_width
        self.screen_height = settings.screen_height

    def generate_bumpers(self):
        bumpers = []
        # Convert original fractions to playfield coordinates, then add top_margin to y
        # Original used screen_width, screen_height. We'll use playfield dimensions.
        x = self.playfield_width / 2 + self.settings.lane_wall_thickness
        y = self.playfield_height / 5 + self.top_margin
        bumpers.append(Bumper(x, y, self.settings.blu))

        #x = 0
        #y = 0 + self.top_margin
        #bumpers.append(Bumper(x, y, self.settings.blu))


    
        return bumpers

    def generate_blocks(self):
        blocks = []
        # Left block (still at left edge of playfield)
        left_vertices = [
            (0, self.screen_height),   # bottom-left (screen coordinates)
            (0, self.top_margin + self.playfield_height - 4/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.screen_height)
        ]
        blocks.append(Block(left_vertices, self.settings.gry, restitution=self.settings.restitution))

        # Right block (now ends at playfield_width, not screen_width)
        right_vertices = [
            (self.playfield_width, self.screen_height),
            (self.playfield_width, self.top_margin + self.playfield_height - 4/14 * self.playfield_height),
            (self.playfield_width - 2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (self.playfield_width - 2/7 * self.playfield_width, self.screen_height)
        ]
        blocks.append(Block(right_vertices, self.settings.gry, restitution=self.settings.restitution))

        # Plunger lane walls (in right margin)
        lane_left = self.playfield_width
        lane_right = self.screen_width
        lane_top = self.top_margin
        lane_bottom = self.screen_height
        wall_thick = self.settings.lane_wall_thickness  # we'll add this to settings later

        # Left wall of lane (at playfield_width)
        left_wall_vertices = [
            (lane_left, lane_bottom),
            (lane_left, lane_top),
            (lane_left + wall_thick, lane_top),
            (lane_left + wall_thick, lane_bottom)
        ]
        blocks.append(Block(left_wall_vertices, (100,100,100), restitution=self.settings.restitution))

        # Right wall of lane (at screen edge)
        right_wall_vertices = [
            (lane_right - wall_thick, lane_bottom),
            (lane_right - wall_thick, lane_top),
            (lane_right, lane_top),
            (lane_right, lane_bottom)
        ]
        blocks.append(Block(right_wall_vertices, (100,100,100), restitution=self.settings.restitution))

        return blocks

    def get_lane_center(self):
        lane_left = self.playfield_width
        return lane_left + self.right_margin / 2