from bumpers import Bumper
from blocks import Block
from one_way_block import OneWayBlock 

class TableBuilder:
    def __init__(self, settings, block_texture=None, tri_texture=None, tri_flipped=None, tri_mirrored=None, pattern=False):
        self.settings = settings
        self.block_texture = block_texture
        self.tri_texture = tri_texture
        self.tri_flipped = tri_flipped
        self.tri_mirrored = tri_mirrored
        self.playfield_width = settings.playfield_width
        self.playfield_height = settings.playfield_height
        self.top_margin = settings.top_margin
        self.right_margin = settings.right_margin
        self.screen_width = settings.screen_width
        self.screen_height = settings.screen_height
        self.guide_height = 30 
    
    def generate_bumpers(self, orb_image=None, small_orb_image=None, tiny_bumper_image=None):
        bumpers = []
        # Wizard's Orb (center)
        x = self.playfield_width / 2 
        y = self.playfield_height / 6 + self.top_margin
        bump_rad = 55
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))

        # Left lower pointer (tiny)
        x = self.playfield_width / 5 + self.settings.lane_wall_thickness
        y = self.playfield_height / 5 + self.top_margin + self.settings.br * 5
        bump_rad = 10
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, tiny_bumper_image))

        # Left upper pointer (tiny)
        x = self.playfield_width / 9 + self.settings.lane_wall_thickness
        y = self.playfield_height / 5 + self.top_margin - self.settings.br * 6
        bump_rad = 6
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, tiny_bumper_image))

        # Right upper pointer (tiny)
        x = 4 * self.playfield_width / 5 + self.settings.lane_wall_thickness + self.settings.br
        y = self.playfield_height / 5 + self.top_margin - self.settings.br * 3
        bump_rad = 8
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, tiny_bumper_image))

        # Right lower pointer (tiny)
        x = 4 * self.playfield_width / 5 + self.settings.lane_wall_thickness - 1 * self.settings.br
        y = self.playfield_height / 5 + self.top_margin +  self.settings.br * 7
        bump_rad = 12
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, tiny_bumper_image))



        # Lower left bumper (small orb)
        x = self.playfield_width - 1/7 * self.playfield_width - (3 * self.settings.br / 4) - (0.18 * self.settings.lane_wall_thickness)
        y = self.top_margin + self.playfield_height - 19/56 * self.playfield_height
        bump_rad = 14
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, small_orb_image))

        # Lower right bumper (small orb)
        x = (0.18 * self.settings.lane_wall_thickness) + 1/7 * self.playfield_width + (3 * self.settings.br / 4) 
        y = self.top_margin + self.playfield_height - 19/56 * self.playfield_height
        bump_rad = 14
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, small_orb_image))

        return bumpers
    
    def generate_top_guide(self):
        """Return a triangular guide at the top of the plunger lane to deflect ball left."""
        wall_thick = self.settings.lane_wall_thickness
        lane_left = self.playfield_width - wall_thick          # interior left edge
        lane_right = self.screen_width - wall_thick            # interior right edge
        guide_height = 40                                      # how far down the guide extends
        vertices = [
            (lane_left, self.top_margin + 5),                      # top left
            (lane_right, self.top_margin + 5),                     # top right
            (lane_right, self.top_margin +5 + guide_height)       # bottom right
        ]
        return Block(vertices, (150,150,150), restitution=self.settings.restitution, image = self.tri_mirrored)

    def generate_one_way_wall(self):
        """Create a thin vertical wall just left of the lane exit to prevent re‑entry."""
        wall_thick = self.settings.lane_wall_thickness
        wall_x = self.playfield_width - 5
        # Plunger Lane Exit
        thickness = 3
        vertices = [
            (wall_x, self.top_margin),
            (wall_x, self.top_margin + self.guide_height * 2),
            (wall_x - thickness, self.top_margin + self.guide_height * 2),
            (wall_x - thickness, self.top_margin)
        ]
        
        return(OneWayBlock(vertices, (100,100,100), restitution=self.settings.restitution, direction='left', image=self.block_texture))
        
    def generate_bottom_wall(self):
        thickness = 5  # height of the bottom strip
        vertices = [
            (0, self.screen_height - thickness),
            (0, self.screen_height),
            (self.screen_width, self.screen_height),
            (self.screen_width, self.screen_height - thickness)
        ]
        return (OneWayBlock(vertices, (180,180,180), restitution=self.settings.restitution, direction='down', image = self.block_texture))
    
    def generate_blocks(self):
        blocks = []
        # Left block (main) – no texture
        left_vertices = [
            (0, self.screen_height - 4/14 * self.playfield_height),
            (0, self.screen_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            
        ]
        blocks.append(Block(left_vertices, self.settings.slv, self.settings.restitution, self.tri_flipped))

        # Left lower block
        left_lower_vertices = [
            (0, self.screen_height),
            (0, self.screen_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.screen_height),
        ]
        blocks.append(Block(left_lower_vertices, self.settings.slv, self.settings.restitution, image = self.block_texture))

        # Left lower border
        left_lower_vertices = [
            (2/7 * self.playfield_width - 5, self.screen_height),
            (2/7 * self.playfield_width - 5, self.screen_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.screen_height),
        ]
        blocks.append(Block(left_lower_vertices, self.settings.slv, self.settings.restitution, image = self.block_texture))


       
        # Right block (main) – no texture
        right_vertices = [
            (self.playfield_width, self.screen_height - 4/14 * self.playfield_height),
            (self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (self.playfield_width - 2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height)
        ]
        blocks.append(Block(right_vertices, self.settings.slv, self.settings.restitution, self.tri_texture))



        # Right lower block
        #(self.playfield_width - 2/7 * self.playfield_width, self.screen_height)
        right_lower_vertices = [
            (self.playfield_width, self.screen_height),
            (self.playfield_width, self.screen_height - 2/14 * self.playfield_height),
            (self.playfield_width - 2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (self.playfield_width - 2/7 * self.playfield_width, self.screen_height),
        ]
        blocks.append(Block(right_lower_vertices, self.settings.slv, self.settings.restitution, image = self.block_texture))

        # Right lower border
        right_lower_vertices = [
            ((self.playfield_width - 2/7 * self.playfield_width) + 5, self.screen_height),
            ((self.playfield_width - 2/7 * self.playfield_width) + 5, self.screen_height - 2/14 * self.playfield_height),
            ((self.playfield_width - 2/7 * self.playfield_width), self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            ((self.playfield_width - 2/7 * self.playfield_width), self.screen_height),
        ]
        blocks.append(Block(right_lower_vertices, self.settings.slv, self.settings.restitution, image = self.block_texture))
        

        # Funnel blocks above left and right main blocks – no texture
        funnel_height = 50
        # Left funnel
        left_top_y = self.top_margin + self.playfield_height - 9/28 * self.playfield_height
        left_bottom_y = self.top_margin + self.playfield_height - 6/28 * self.playfield_height
        left_funnel_vertices = [
            (3 * self.settings.br, left_top_y - funnel_height),
            (3 * self.settings.br, left_top_y),
            (2/7 * self.playfield_width - self.settings.br * 1.1, left_bottom_y),
            (2/7 * self.playfield_width - self.settings.br * 1.7, left_bottom_y - funnel_height)
        ]
        blocks.append(Block(left_funnel_vertices, self.settings.slv, restitution=self.settings.restitution, pattern=True))

        # Right funnel
        right_top_y = self.top_margin + self.playfield_height - 9/28 * self.playfield_height
        right_bottom_y = self.top_margin + self.playfield_height - 6/28 * self.playfield_height
        right_funnel_vertices = [
            (self.playfield_width - 3 * self.settings.br, right_top_y - funnel_height),
            (self.playfield_width - 3 * self.settings.br, right_top_y),
            (self.playfield_width - 2/7 * self.playfield_width + self.settings.br * 1.1, right_bottom_y),
            (self.playfield_width - 2/7 * self.playfield_width + self.settings.br * 1.7, right_bottom_y - funnel_height)
        ]
        blocks.append(Block(right_funnel_vertices, self.settings.slv, self.settings.restitution, pattern=True))


        # Bottom stopper block
        stopper_height = 10
        stopper_top = self.screen_height - stopper_height
        stopper_vertices = [
            (self.playfield_width, self.screen_height),
            (self.playfield_width, stopper_top),
            (self.screen_width, stopper_top),
            (self.screen_width, self.screen_height)
        ]
        blocks.append(Block(stopper_vertices, (100,100,100), restitution=0.2, pattern=True))

        # Top guide (untextured)
        guide = self.generate_top_guide()
        blocks.append(guide)

        # One‑way wall (textured)
        oneway = self.generate_one_way_wall()
        blocks.append(oneway)

        # Bottom wall (textured)
       
        bottom_wall = self.generate_bottom_wall()
        blocks.append(bottom_wall)

        # Top playing field border (textured)
        top_border_vertices = [
            (0, self.top_margin),
            (0, self.top_margin + self.settings.lane_wall_thickness),
            (self.screen_width, self.top_margin + self.settings.lane_wall_thickness),
            (self.screen_width, self.top_margin)
        ]
        blocks.append(Block(top_border_vertices, (100,100,100), restitution=self.settings.restitution, image=self.block_texture))

      # Top bar (thin decorative strip at very top)
        top_bar_vertices = [
            (0, 0),
            (0, 5),                             # height 5 pixels
            (self.screen_width, 5),
            (self.screen_width, 0)
        ]
        blocks.append(Block(top_bar_vertices, (100,100,100), restitution=self.settings.restitution, image=self.block_texture))

        # Left border (full height, from top to bottom)
        left_border_vertices = [
            (0, 0),
            (0, self.screen_height),
            (self.settings.lane_wall_thickness, self.screen_height),
            (self.settings.lane_wall_thickness, 0)
        ]
        blocks.append(Block(left_border_vertices, (100,100,100), restitution=self.settings.restitution, image=self.block_texture))

        # Right border (full height)
        right_border_vertices = [
            (self.screen_width - self.settings.lane_wall_thickness, 0),
            (self.screen_width - self.settings.lane_wall_thickness, self.screen_height),
            (self.screen_width, self.screen_height),
            (self.screen_width, 0)
        ]
        blocks.append(Block(right_border_vertices, (100,100,100), restitution=self.settings.restitution, image=self.block_texture))
        



        # Lane walls (textured)
        wall_thick = self.settings.lane_wall_thickness
        lane_left = self.playfield_width
        lane_right = self.screen_width
        lane_top = self.top_margin
        lane_bottom = self.screen_height

        # Left lane wall (shortened to allow exit)
        left_wall_vertices = [
            (lane_left - wall_thick, lane_bottom),
            (lane_left - wall_thick, lane_top + self.guide_height * 2),
            (lane_left + wall_thick, lane_top + self.guide_height * 2),
            (lane_left + wall_thick, lane_bottom)
        ]
        blocks.append(Block(left_wall_vertices, (100,100,100), restitution=self.settings.restitution, image=self.block_texture))

        # Left Lane wall cap
        left_wall_vertices = [
            (lane_left, lane_top + self.guide_height * 2),
            (lane_left + 7, lane_top + self.guide_height * 2),
            (lane_left + 7, lane_top + self.guide_height * 2 + 5),
            (lane_left, lane_top + self.guide_height * 2 + 5),
        ]
        blocks.append(Block(left_wall_vertices, (100,100,100), restitution=self.settings.restitution, image=self.block_texture))

        

        return blocks

    def get_lane_center(self):
        lane_left = self.playfield_width
        return lane_left + self.right_margin / 2

    def get_lane_bottom(self):
        return self.screen_height - 10

    def get_plunger_base_y(self):
        return self.screen_height - 10