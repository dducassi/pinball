from bumpers import Bumper
from blocks import Block
from one_way_block import OneWayBlock 

class TableBuilder:
    def __init__(self, settings):
        self.settings = settings
        self.playfield_width = settings.playfield_width
        self.playfield_height = settings.playfield_height
        self.top_margin = settings.top_margin
        self.right_margin = settings.right_margin
        self.screen_width = settings.screen_width
        self.screen_height = settings.screen_height
        self.guide_height = 30 

    def generate_bumpers(self):
        bumpers = []
        x = self.playfield_width / 2 + self.settings.lane_wall_thickness
        y = self.playfield_height / 5 + self.top_margin
        bumpers.append(Bumper(x, y, self.settings.blu))
        return bumpers
    
    def generate_top_guide(self):
        """Return a triangular guide at the top of the plunger lane to deflect ball left."""
        wall_thick = self.settings.lane_wall_thickness
        lane_left = self.playfield_width + wall_thick          # interior left edge
        lane_right = self.screen_width - wall_thick            # interior right edge
        guide_height = 30                                      # how far down the guide extends
        vertices = [
            (lane_left, self.top_margin),                      # top left
            (lane_right, self.top_margin),                     # top right
            (lane_right, self.top_margin + guide_height)       # bottom right
        ]
        return Block(vertices, (100,100,100), restitution=self.settings.restitution)

    def generate_one_way_wall(self):
        """Create a thin vertical wall just left of the lane exit to prevent re‑entry."""
        wall_thick = self.settings.lane_wall_thickness
        wall_x = self.playfield_width + wall_thick - 2
        thickness = 2
        vertices = [
            (wall_x, self.top_margin),
            (wall_x, self.top_margin + self.guide_height * 1.5),
            (wall_x - thickness, self.top_margin + self.guide_height * 1.5),
            (wall_x - thickness, self.top_margin)
        ]
        return OneWayBlock(vertices, (100,100,100), restitution=self.settings.restitution, direction='left')
    
    def generate_blocks(self):
        blocks = []
        # Left block
        left_vertices = [
            (0, self.screen_height),
            (0, self.top_margin + self.playfield_height - 4/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.screen_height)
        ]
        blocks.append(Block(left_vertices, self.settings.gry, restitution=self.settings.restitution))

        # Right block
        right_vertices = [
            (self.playfield_width, self.screen_height),
            (self.playfield_width, self.top_margin + self.playfield_height - 4/14 * self.playfield_height),
            (self.playfield_width - 2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (self.playfield_width - 2/7 * self.playfield_width, self.screen_height)
        ]
        blocks.append(Block(right_vertices, self.settings.gry, restitution=self.settings.restitution))

        # Funnel blocks above left and right main blocks
        funnel_height = 40
        # Left funnel (same slope as left block)
        left_top_y = self.top_margin + self.playfield_height - 4/14 * self.playfield_height
        left_bottom_y = self.top_margin + self.playfield_height - 3/14 * self.playfield_height
        left_funnel_vertices = [
            (3 * self.settings.br, left_top_y - funnel_height),
            (3 * self.settings.br, left_top_y),
            (2/7 * self.playfield_width - self.settings.br * 1.5, left_bottom_y),
            (2/7 * self.playfield_width - self.settings.br * 1.5, left_bottom_y - funnel_height)
        ]
        blocks.append(Block(left_funnel_vertices, self.settings.gry, restitution=self.settings.restitution))

        # Right funnel (same slope as right block)
        right_top_y = self.top_margin + self.playfield_height - 4/14 * self.playfield_height
        right_bottom_y = self.top_margin + self.playfield_height - 3/14 * self.playfield_height
        right_funnel_vertices = [
            (self.playfield_width - 3 * self.settings.br + 7 , right_top_y - funnel_height),
            (self.playfield_width - 3 * self.settings.br + 7, right_top_y),
            (self.playfield_width - 2/7 * self.playfield_width + self.settings.br * 1.5, right_bottom_y),
            (self.playfield_width - 2/7 * self.playfield_width + self.settings.br * 1.5, right_bottom_y - funnel_height)
        ]
        blocks.append(Block(right_funnel_vertices, self.settings.gry, restitution=self.settings.restitution))

        # Bottom stopper block
        stopper_height = 10
        stopper_top = self.screen_height - stopper_height
        stopper_vertices = [
            (self.playfield_width, self.screen_height),
            (self.playfield_width, stopper_top),
            (self.screen_width, stopper_top),
            (self.screen_width, self.screen_height)
        ]
        blocks.append(Block(stopper_vertices, (100,100,100), restitution=0.2))

        guide = self.generate_top_guide()
        blocks.append(guide)

        oneway = self.generate_one_way_wall()
        blocks.append(oneway)

        # Lane walls
        wall_thick = self.settings.lane_wall_thickness
        lane_left = self.playfield_width
        lane_right = self.screen_width
        lane_top = self.top_margin
        lane_bottom = self.screen_height

        # Left lane wall (shortened to allow exit)
        left_wall_vertices = [
            (lane_left, lane_bottom),
            (lane_left, lane_top + self.guide_height * 1.5),
            (lane_left + wall_thick, lane_top + self.guide_height * 1.5),
            (lane_left + wall_thick, lane_bottom)
        ]
        blocks.append(Block(left_wall_vertices, (100,100,100), restitution=self.settings.restitution))

        # Right lane wall
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

    def get_lane_bottom(self):
        return self.screen_height - 10

    def get_plunger_base_y(self):
        return self.screen_height - 10