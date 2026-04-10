import pygame
import os
from settings import Settings
from bumpers import Bumper
from blocks import Block
from one_way_block import OneWayBlock 
from light import Light
import math
from abc import ABC, abstractmethod

class Table:
    def __init__(self, name, builder_class, title, tagline, music_path=None,
                 bg_path=None, lane_bg_path=None, use_ball_image=True,
                 small_bumper_messages=None, large_bumper_messages=None,
                 color_cycle=None, tint_background=True):
        self.name = name
        self.builder_class = builder_class
        self.title = title
        self.tagline = tagline
        self.music_path = music_path
        self.bg_path = bg_path
        self.lane_bg_path = lane_bg_path
        self.use_ball_image = use_ball_image
        self.small_bumper_messages = small_bumper_messages or ["BUMPER!"]
        self.large_bumper_messages = large_bumper_messages or {}
        self.color_cycle = color_cycle  # e.g., ['wht', 'blu', 'red']
        self.tint_background = tint_background


class TableManager:
    def __init__(self, settings, base_dir):
        self.settings = settings
        self.base_dir = base_dir
        self.tables = []
        self.current_index = 0
        self._register_tables()

    def _register_tables(self):

        # Wizard table
        self.tables.append(Table(
            name="WIZARD'S TOWER",
            builder_class=WizardTableBuilder,
            title="THE WIZARD'S TOWER",
            tagline="CAST A SPELL!",
            music_path=os.path.join(self.base_dir, 'music.ogg'),
            bg_path=os.path.join(self.base_dir, 'wizard.png'),
            lane_bg_path=os.path.join(self.base_dir, 'lane_bg.png'),
            large_bumper_messages={
                self.settings.blu: "ORB OF POWER!",
                self.settings.red: "FIREBALL!",
                self.settings.wht: "BALL LIGHTNING!"
            },
            small_bumper_messages = ["BOOM!", "HISS!", "POP!", "ZAP!", "BUZZ!"],
            color_cycle=[self.settings.wht, self.settings.blu, self.settings.red],
            tint_background=True
        ))

        # Minimalist table
        self.tables.append(Table(
                name="THE MINIMALIST",
                builder_class=MinimalistTableBuilder,
                title="THE MINIMALIST",
                tagline="START GAME",
                music_path=None,
                bg_path=None,
                lane_bg_path=None,
                use_ball_image=False,
                large_bumper_messages={
                    self.settings.blu: "BLUE!",
                    self.settings.ylw: "YELLOW!",
                    self.settings.red: "RED!"
                },
                color_cycle=None,   # no color cycling
                tint_background=False
        ))

    def get_current_table(self):
        return self.tables[self.current_index]

    def next_table(self):
        self.current_index = (self.current_index + 1) % len(self.tables)

    def prev_table(self):
        self.current_index = (self.current_index - 1) % len(self.tables)


class TableBuilderBase(ABC):
    def __init__(self, settings):
        self.settings = settings
        self.playfield_width = settings.playfield_width
        self.playfield_height = settings.playfield_height
        self.top_margin = settings.top_margin
        self.right_margin = settings.right_margin
        self.screen_width = settings.screen_width
        self.screen_height = settings.screen_height

    @abstractmethod
    def generate_blocks(self):
        """Return list of Block objects."""
        pass

    @abstractmethod
    def generate_bumpers(self, images):
        """Return tuple (bumpers, lights)."""
        pass

    def get_lane_center(self):
        return self.playfield_width + self.right_margin / 2

    def get_lane_bottom(self):
        return self.screen_height - 10

    def get_plunger_base_y(self):
        return self.screen_height - 10
    
class WizardTableBuilder(TableBuilderBase):
    def __init__(self, settings, images):
        super().__init__(settings)
        self.settings = settings
        self.block_texture = images.get('block_texture')
        self.tri_texture = images.get('tri_texture')
        self.tri_flipped = images.get('tri_flipped')
        self.tri_mirrored = images.get('tri_mirrored')
        self.edge_vert = images.get('edge_vert_texture')
        self.edge_horz = images.get('edge_horz_texture')
        self.guide_height = 30
        self.playfield_width = settings.playfield_width
        self.playfield_height = settings.playfield_height
        self.top_margin = settings.top_margin
        self.right_margin = settings.right_margin
        self.screen_width = settings.screen_width
        self.screen_height = settings.screen_height
        self.guide_height = 30 
        self.light = None


   
    def generate_bumpers(self, images):
        bumpers = []
        lights = []
        orb_image = images.get('orb_image')
        small_orb_image = images.get('small_orb_image')
        tiny_bumper_image = images.get('tiny_bumper_image')
        light_image = images.get('light_image')
        # Wizard's Orb (center)
        x = self.playfield_width / 2
        y = self.playfield_height / 6 + self.top_margin
        bump_rad = 6 * self.settings.br
        color = self.settings.wht
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, bump_rad + 2, color, light_image))

        # Left lower pointer (tiny)
        x = self.playfield_width / 5 + self.settings.lane_wall_thickness
        y = self.playfield_height / 5 + self.top_margin + self.settings.br * 5
        bump_rad = 1.1 * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, 13, color, light_image))

        # Left upper pointer (tiny)
        x = self.playfield_width / 9 + self.settings.lane_wall_thickness
        y = self.playfield_height / 5 + self.top_margin - self.settings.br * 6
        bump_rad = 0.7  * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, 9, color, light_image))

        # Right upper pointer (tiny)
        x = 4 * self.playfield_width / 5 + self.settings.lane_wall_thickness + self.settings.br
        y = self.playfield_height / 5 + self.top_margin - self.settings.br * 3
        bump_rad = 0.9  * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, 11, color, light_image))

        # Right lower pointer (tiny)
        x = 4 * self.playfield_width / 5 + self.settings.lane_wall_thickness - 1 * self.settings.br
        y = self.playfield_height / 5 + self.top_margin +  self.settings.br * 7
        bump_rad = 1.3 * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, 15, color, light_image))

        # Lower left bumper (small orb)
        x = self.playfield_width - 1/7 * self.playfield_width - (3 * self.settings.br / 4)
        y = self.top_margin + self.playfield_height - 19/56 * self.playfield_height
        bump_rad = 2 * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, 18, color, light_image))

        # Lower right bumper (small orb)
        x = (0.18 * self.settings.lane_wall_thickness) + 1/7 * self.playfield_width + (3 * self.settings.br / 4) 
        y = self.top_margin + self.playfield_height - 19/56 * self.playfield_height
        bump_rad = 2  * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, 18, color, light_image))

        # Wizard's chest
        x = self.playfield_width // 2
        y = self.playfield_height / 2 + self.top_margin - 6.5 * self.settings.br
        bump_rad = 0.8  * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, 10.5, color, light_image))

        # Wizard left
        x = self.playfield_width // 2 - 2  * self.settings.br
        y = self.playfield_height / 2 + self.top_margin - 11.5* self.settings.br
        bump_rad = 0.55  * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, 8, color, light_image))

        # Wizard right
        x = self.playfield_width // 2 + 2 * self.settings.br
        y = self.playfield_height / 2 + self.top_margin - 11.5 * self.settings.br
        bump_rad = 0.55  * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, 8, color, light_image))

        return bumpers, lights

    def generate_top_guide(self):
        """Return a concave guide at the top of the plunger lane, rotated 90° counter‑clockwise."""
        wall_thick = self.settings.lane_wall_thickness
        lane_left = self.playfield_width + 1
        lane_right = self.screen_width -4
        guide_height = 40
        y_top = self.top_margin
        y_bottom = y_top + guide_height

        vertices = []

        # Top edge (left to right)
        vertices.append((lane_left, y_top))
        vertices.append((lane_right, y_top))

        # Generate points along the concave curve (top‑right to bottom‑left)
        steps = 72
        for i in range(1, steps + 1):
            t = i / steps
            x = lane_right + (lane_left - lane_right) * t
            y = y_top + (y_bottom - y_top) * t
            offset = 15 * (1 - (2*t - 1)**2)
            x -= offset
            vertices.append((x, y))

        # Rotate the entire polygon 90° counter‑clockwise about its center
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2

        rotated_vertices = []
        for (x, y) in vertices:
            x1 = x - cx
            y1 = y - cy
            # Rotate 90° counter‑clockwise: (x1, y1) -> (-y1, x1)
            x2 = -y1
            y2 = x1
            x_new = x2 + cx
            y_new = y2 + cy
            rotated_vertices.append((x_new, y_new))

        return Block(rotated_vertices, (220, 220, 220), restitution=self.settings.restitution, pattern=True)
    
    
    
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
        
        return(OneWayBlock(vertices, (100,100,100), restitution=self.settings.restitution, direction='left', image=self.edge_vert))
        
    def generate_bottom_wall(self):
        thickness = 8  # height of the bottom strip
        vertices = [
            (0, self.screen_height - thickness),
            (0, self.screen_height),
            (self.screen_width, self.screen_height),
            (self.screen_width, self.screen_height - thickness)
        ]
        return (OneWayBlock(vertices, (180,180,180), restitution=self.settings.restitution, direction='down', image=self.edge_horz))
    
    def generate_blocks(self):
        blocks = []
        # Left block (main) – no texture
        left_vertices = [
            (0, self.screen_height - 4/14 * self.playfield_height + 0.1  * self.settings.br),
            (0, self.screen_height - 2/14 * self.playfield_height + 0.1  * self.settings.br),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 1),
            
        ]
        blocks.append(Block(left_vertices, self.settings.slv, self.settings.restitution, self.tri_flipped))

        # Left lower block
        left_lower_vertices = [
            (0, self.screen_height),
            (0, self.screen_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.screen_height),
        ]
        blocks.append(Block(left_lower_vertices, self.settings.slv, self.settings.restitution, image=self.block_texture))

        # Left lower border
        left_lower_vertices = [
            (2/7 * self.playfield_width - 5, self.screen_height),
            (2/7 * self.playfield_width - 5, self.screen_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.screen_height),
        ]
        blocks.append(Block(left_lower_vertices, self.settings.slv, self.settings.restitution, image=self.edge_vert))

        # Left lower top border
        left_lower_top_vertices = [
            (0, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (0, self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 5),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 5),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
        ]
        blocks.append(Block(left_lower_top_vertices, self.settings.slv, self.settings.restitution, image=self.edge_horz))


       
        # Right block -- triangle texture
        right_vertices = [
            (self.playfield_width, self.screen_height - 4/14 * self.playfield_height +  0.1 * self.settings.br),
            (self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 0.1  * self.settings.br),
            (self.playfield_width - 2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 1)
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
        blocks.append(Block(right_lower_vertices, self.settings.slv, self.settings.restitution, image=self.block_texture))

        # Right lower border
        right_lower_vertices = [
            ((self.playfield_width - 2/7 * self.playfield_width), self.screen_height),
            ((self.playfield_width - 2/7 * self.playfield_width), self.screen_height - 2/14 * self.playfield_height),
            ((self.playfield_width - 2/7 * self.playfield_width) + 5, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            ((self.playfield_width - 2/7 * self.playfield_width) + 5, self.screen_height),
        ]
        blocks.append(Block(right_lower_vertices, self.settings.slv, self.settings.restitution, image=self.edge_vert))
        
         # Right lower top border
        right_lower_top_vertices = [
            (self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 5),
            ((self.playfield_width - 2/7 * self.playfield_width), self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 5),
            ((self.playfield_width - 2/7 * self.playfield_width), self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
        ]
        blocks.append(Block(right_lower_top_vertices, self.settings.slv, self.settings.restitution, image=self.edge_horz))

        # Funnel blocks above left and right main blocks – no texture
        funnel_height = 50
        # Left funnel
        left_top_y = self.top_margin + self.playfield_height - 9/28 * self.playfield_height
        left_bottom_y = self.top_margin + self.playfield_height - 6/28 * self.playfield_height
        left_funnel_vertices = [
            (3 * self.settings.br, left_top_y - funnel_height),
            (3 * self.settings.br + 6, left_top_y),
            (2/7 * self.playfield_width - self.settings.br * 1.1, left_bottom_y),
            (2/7 * self.playfield_width - self.settings.br * 1.7, left_bottom_y - funnel_height)
        ]
        blocks.append(Block(left_funnel_vertices, self.settings.slv, restitution=self.settings.restitution, pattern=True))

        # Right funnel
        right_top_y = self.top_margin + self.playfield_height - 9/28 * self.playfield_height
        right_bottom_y = self.top_margin + self.playfield_height - 6/28 * self.playfield_height
        right_funnel_vertices = [
            (self.playfield_width - 3 * self.settings.br, right_top_y - funnel_height),
            (self.playfield_width - 3 * self.settings.br - 6, right_top_y),
            (self.playfield_width - 2/7 * self.playfield_width + self.settings.br * 1.1, right_bottom_y),
            (self.playfield_width - 2/7 * self.playfield_width + self.settings.br * 1.7, right_bottom_y - funnel_height)
        ]
        blocks.append(Block(right_funnel_vertices, self.settings.slv, self.settings.restitution, pattern=True))

        # Top left redirector
        redirector_height = 27
        redirector_top_y = self.top_margin
        redirector_bottom_y = self.top_margin + redirector_height
        redirector_vertices = [
            (0, redirector_top_y),                     # top‑left
            (redirector_height, redirector_top_y),     # top‑right
            (0, redirector_bottom_y)                   # bottom‑left
        ]
        blocks.append(Block(redirector_vertices, (220,220,220), self.settings.restitution,pattern=True))

        # Bottom stopper block
        stopper_height = 10
        stopper_top = self.screen_height - stopper_height
        stopper_vertices = [
            (self.playfield_width, self.screen_height),
            (self.playfield_width, stopper_top),
            (self.screen_width, stopper_top),
            (self.screen_width, self.screen_height)
        ]
        blocks.append(Block(stopper_vertices, (90,90,90), restitution=0.2))

        # Top guide (untextured)
        guide = self.generate_top_guide()
        blocks.append(guide)

         # Left top guide
        #left_guide = self.generate_top_guide_left()
        #blocks.append(left_guide)

        # One‑way wall (textured)
        oneway = self.generate_one_way_wall()
        blocks.append(oneway)

       

        # Top playing field border (textured)
        top_border_vertices = [
            (0, self.top_margin),
            (0, self.top_margin + self.settings.lane_wall_thickness),
            (self.screen_width, self.top_margin + self.settings.lane_wall_thickness),
            (self.screen_width, self.top_margin)
        ]
        blocks.append(Block(top_border_vertices, (100,100,100), restitution=self.settings.restitution, image=self.edge_horz))

      

        # Left border (full height, from top to bottom)
        left_border_vertices = [
            (0, 0),
            (0, self.screen_height),
            (self.settings.lane_wall_thickness, self.screen_height),
            (self.settings.lane_wall_thickness, 0)
        ]
        blocks.append(Block(left_border_vertices, (100,100,100), restitution=self.settings.restitution, image=self.edge_vert))

        # Right border (full height)
        right_border_vertices = [
            (self.screen_width - self.settings.lane_wall_thickness, 0),
            (self.screen_width - self.settings.lane_wall_thickness, self.screen_height),
            (self.screen_width, self.screen_height),
            (self.screen_width, 0)
        ]
        blocks.append(Block(right_border_vertices, (100,100,100), restitution=self.settings.restitution, image=self.edge_vert))
        



        # Lane walls (textured)
        wall_thick = self.settings.lane_wall_thickness
        lane_left = self.playfield_width
        lane_right = self.screen_width
        lane_top = self.top_margin
        lane_bottom = self.screen_height

        # Left lane walls (shortened to allow exit)
        left_wall_vertices = [
            (lane_left - wall_thick, lane_bottom - 5),
            (lane_left - wall_thick, lane_top + self.guide_height * 2),
            (lane_left, lane_top + self.guide_height * 2),
            (lane_left, lane_bottom - 5)
        ]
        blocks.append(Block(left_wall_vertices, (100,100,100), restitution=self.settings.restitution, image=self.edge_vert))

        left_wall_left_vertices = [
            (lane_left, lane_bottom - 5),
            (lane_left, lane_top + self.guide_height * 2),
            (lane_left + wall_thick, lane_top + self.guide_height * 2),
            (lane_left + wall_thick, lane_bottom - 5)
        ]
        blocks.append(Block(left_wall_left_vertices, (100,100,100), restitution=self.settings.restitution, image=self.edge_vert))

        # Left Lane wall cap
        left_wall_vertices = [
            (lane_left - 7, lane_top + self.guide_height * 2),
            (lane_left + 7, lane_top + self.guide_height * 2),
            (lane_left + 7, lane_top + self.guide_height * 2 + 5),
            (lane_left - 7, lane_top + self.guide_height * 2 + 5),
        ]
        blocks.append(Block(left_wall_vertices, (100,100,100), restitution=self.settings.restitution, image=self.edge_horz))

        # Bottom wall (textured)
       
        bottom_wall = self.generate_bottom_wall()
        blocks.append(bottom_wall)

        # Top bar (thin decorative strip at very top)
        top_bar_vertices = [
            (0, 0),
            (0, 8),                             # height 5 pixels
            (self.screen_width, 8),
            (self.screen_width, 0)
        ]
        blocks.append(Block(top_bar_vertices, (100,100,100), restitution=self.settings.restitution, image=self.edge_horz))

        

        return blocks

    def get_lane_center(self):
        lane_left = self.playfield_width
        return lane_left + self.right_margin / 2

    def get_lane_bottom(self):
        return self.screen_height - 10

    def get_plunger_base_y(self):
        return self.screen_height - 10


class MinimalistTableBuilder(TableBuilderBase):
    def __init__(self, settings, images):
        super().__init__(settings)
        self.settings = settings
        self.block_texture = None
        self.tri_texture = None
        self.tri_flipped = None
        self.tri_mirrored = None
        self.edge_vert = None
        self.edge_horz = None
        self.guide_height = 30
        self.playfield_width = settings.playfield_width
        self.playfield_height = settings.playfield_height
        self.top_margin = settings.top_margin
        self.right_margin = settings.right_margin
        self.screen_width = settings.screen_width
        self.screen_height = settings.screen_height
        self.guide_height = 30 
        self.light = None

   
    def generate_bumpers(self, images):
        bumpers = []
        lights = []
        # For minimalist, pass None
        orb_image = None
        small_orb_image = None
        tiny_bumper_image = None
        light_image = None

        # Main bumper
        x = self.playfield_width / 3
        y = self.playfield_height / 6 + self.top_margin
        bump_rad = 5.5 * self.settings.br
        color = self.settings.wht
        bumpers.append(Bumper(x, y, self.settings.red, bump_rad, orb_image))
        lights.append(Light(x, y, bump_rad + 2, self.settings.red, light_image))

        # Lower left bumper 
        x = self.playfield_width - 1/7 * self.playfield_width - (3 * self.settings.br / 4)
        y = self.top_margin + self.playfield_height - 19/56 * self.playfield_height
        bump_rad = 2 * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, bump_rad + 1, self.settings.wht, light_image))

        # Lower right bumper 
        x = (0.18 * self.settings.lane_wall_thickness) + 1/7 * self.playfield_width + (3 * self.settings.br / 4) 
        y = self.top_margin + self.playfield_height - 19/56 * self.playfield_height
        bump_rad = 2  * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.wht, bump_rad, orb_image))
        lights.append(Light(x, y, bump_rad + 1, self.settings.wht, light_image))

        # Secondary main bumper
        x = 3 * self.playfield_width // 4
        y = self.playfield_height / 2 + self.top_margin - 9 * self.settings.br
        bump_rad = 4.5  * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.blu, bump_rad, orb_image))
        lights.append(Light(x, y, bump_rad + 2, self.settings.blu, light_image))

        # Tertiary bumper 
        x = self.playfield_width // 2 - 3  * self.settings.br
        y = self.playfield_height / 2 + self.top_margin
        bump_rad = 3.5  * self.settings.br
        bumpers.append(Bumper(x, y, self.settings.ylw, bump_rad, orb_image))
        lights.append(Light(x, y, bump_rad + 2, self.settings.ylw, light_image))

        return bumpers, lights

    def generate_top_guide(self):
        """Return a concave guide at the top of the plunger lane, rotated 90° counter‑clockwise."""
        wall_thick = self.settings.lane_wall_thickness
        lane_left = self.playfield_width + 1
        lane_right = self.screen_width -4
        guide_height = 40
        y_top = self.top_margin
        y_bottom = y_top + guide_height

        vertices = []

        # Top edge (left to right)
        vertices.append((lane_left, y_top))
        vertices.append((lane_right, y_top))

        # Generate points along the concave curve (top‑right to bottom‑left)
        steps = 72
        for i in range(1, steps + 1):
            t = i / steps
            x = lane_right + (lane_left - lane_right) * t
            y = y_top + (y_bottom - y_top) * t
            offset = 15 * (1 - (2*t - 1)**2)
            x -= offset
            vertices.append((x, y))

        # Rotate the entire polygon 90° counter‑clockwise about its center
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2

        rotated_vertices = []
        for (x, y) in vertices:
            x1 = x - cx
            y1 = y - cy
            # Rotate 90° counter‑clockwise: (x1, y1) -> (-y1, x1)
            x2 = -y1
            y2 = x1
            x_new = x2 + cx
            y_new = y2 + cy
            rotated_vertices.append((x_new, y_new))

        return Block(rotated_vertices, (220, 220, 220), restitution=self.settings.restitution, pattern=True)
    
    
    
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
        
        return(OneWayBlock(vertices, (100,100,100), restitution=self.settings.restitution, direction='left', image=self.edge_vert))
        
    def generate_bottom_wall(self):
        thickness = 8  # height of the bottom strip
        vertices = [
            (0, self.screen_height - thickness),
            (0, self.screen_height),
            (self.screen_width, self.screen_height),
            (self.screen_width, self.screen_height - thickness)
        ]
        return (OneWayBlock(vertices, (180,180,180), restitution=self.settings.restitution, direction='down', image=self.edge_horz))
    
    def generate_blocks(self):
        blocks = []
        # Left block (main) – no texture
        left_vertices = [
            (0, self.screen_height - 4/14 * self.playfield_height + 0.1  * self.settings.br),
            (0, self.screen_height - 2/14 * self.playfield_height + 0.1  * self.settings.br),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 1),
            
        ]
        blocks.append(Block(left_vertices, self.settings.slv, self.settings.restitution, self.tri_flipped))

        # Left lower block
        left_lower_vertices = [
            (0, self.screen_height),
            (0, self.screen_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height),
            (2/7 * self.playfield_width, self.screen_height),
        ]
        blocks.append(Block(left_lower_vertices, self.settings.slv, self.settings.restitution, image=self.block_texture))



       
        # Right block -- triangle texture
        right_vertices = [
            (self.playfield_width, self.screen_height - 4/14 * self.playfield_height +  0.1 * self.settings.br),
            (self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 0.1  * self.settings.br),
            (self.playfield_width - 2/7 * self.playfield_width, self.top_margin + self.playfield_height - 2/14 * self.playfield_height + 1)
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
        blocks.append(Block(right_lower_vertices, self.settings.slv, self.settings.restitution, image=self.block_texture))

        

        # Funnel blocks above left and right main blocks – no texture
        funnel_height = 50
        # Left funnel
        left_top_y = self.top_margin + self.playfield_height - 9/28 * self.playfield_height
        left_bottom_y = self.top_margin + self.playfield_height - 6/28 * self.playfield_height
        left_funnel_vertices = [
            (3 * self.settings.br, left_top_y - funnel_height),
            (3 * self.settings.br + 6, left_top_y),
            (2/7 * self.playfield_width - self.settings.br * 1.1, left_bottom_y),
            (2/7 * self.playfield_width - self.settings.br * 1.7, left_bottom_y - funnel_height)
        ]
        blocks.append(Block(left_funnel_vertices, self.settings.slv, restitution=self.settings.restitution, pattern=True))

        # Right funnel
        right_top_y = self.top_margin + self.playfield_height - 9/28 * self.playfield_height
        right_bottom_y = self.top_margin + self.playfield_height - 6/28 * self.playfield_height
        right_funnel_vertices = [
            (self.playfield_width - 3 * self.settings.br, right_top_y - funnel_height),
            (self.playfield_width - 3 * self.settings.br - 6, right_top_y),
            (self.playfield_width - 2/7 * self.playfield_width + self.settings.br * 1.1, right_bottom_y),
            (self.playfield_width - 2/7 * self.playfield_width + self.settings.br * 1.7, right_bottom_y - funnel_height)
        ]
        blocks.append(Block(right_funnel_vertices, self.settings.slv, self.settings.restitution, pattern=True))

        # Top left redirector
        redirector_height = 27
        redirector_top_y = self.top_margin
        redirector_bottom_y = self.top_margin + redirector_height
        redirector_vertices = [
            (0, redirector_top_y),                     # top‑left
            (redirector_height, redirector_top_y),     # top‑right
            (0, redirector_bottom_y)                   # bottom‑left
        ]
        blocks.append(Block(redirector_vertices, (220,220,220), self.settings.restitution,pattern=True))

        # Bottom stopper block
        stopper_height = 10
        stopper_top = self.screen_height - stopper_height
        stopper_vertices = [
            (self.playfield_width, self.screen_height),
            (self.playfield_width, stopper_top),
            (self.screen_width, stopper_top),
            (self.screen_width, self.screen_height)
        ]
        blocks.append(Block(stopper_vertices, (90,90,90), restitution=0.2))

        # Top guide (untextured)
        guide = self.generate_top_guide()
        blocks.append(guide)

         # Left top guide
        #left_guide = self.generate_top_guide_left()
        #blocks.append(left_guide)

        # One‑way wall (textured)
        oneway = self.generate_one_way_wall()
        blocks.append(oneway)

       

        # Top playing field border (textured)
        top_border_vertices = [
            (0, self.top_margin),
            (0, self.top_margin + self.settings.lane_wall_thickness),
            (self.screen_width, self.top_margin + self.settings.lane_wall_thickness),
            (self.screen_width, self.top_margin)
        ]
        blocks.append(Block(top_border_vertices, self.settings.slv, restitution=self.settings.restitution, image=self.edge_horz))

      

        # Left border (full height, from top to bottom)
        left_border_vertices = [
            (0, 0),
            (0, self.screen_height),
            (self.settings.lane_wall_thickness, self.screen_height),
            (self.settings.lane_wall_thickness, 0)
        ]
        blocks.append(Block(left_border_vertices, self.settings.slv, restitution=self.settings.restitution, image=self.edge_vert))

        # Right border (full height)
        right_border_vertices = [
            (self.screen_width - self.settings.lane_wall_thickness, 0),
            (self.screen_width - self.settings.lane_wall_thickness, self.screen_height),
            (self.screen_width, self.screen_height),
            (self.screen_width, 0)
        ]
        blocks.append(Block(right_border_vertices, self.settings.slv, restitution=self.settings.restitution, image=self.edge_vert))
        



        # Lane walls (textured)
        wall_thick = self.settings.lane_wall_thickness
        lane_left = self.playfield_width
        lane_right = self.screen_width
        lane_top = self.top_margin
        lane_bottom = self.screen_height

        # Left lane walls (shortened to allow exit)
        left_wall_vertices = [
            (lane_left - wall_thick, lane_bottom - 5),
            (lane_left - wall_thick, lane_top + self.guide_height * 2),
            (lane_left, lane_top + self.guide_height * 2),
            (lane_left, lane_bottom - 5)
        ]
        blocks.append(Block(left_wall_vertices, self.settings.slv, restitution=self.settings.restitution, image=self.edge_vert))

        left_wall_left_vertices = [
            (lane_left, lane_bottom - 5),
            (lane_left, lane_top + self.guide_height * 2),
            (lane_left + wall_thick, lane_top + self.guide_height * 2),
            (lane_left + wall_thick, lane_bottom - 5)
        ]
        blocks.append(Block(left_wall_left_vertices, self.settings.slv, restitution=self.settings.restitution, image=self.edge_vert))

        # Left Lane wall cap
        left_wall_vertices = [
            (lane_left - 7, lane_top + self.guide_height * 2),
            (lane_left + 7, lane_top + self.guide_height * 2),
            (lane_left + 7, lane_top + self.guide_height * 2 + 5),
            (lane_left - 7, lane_top + self.guide_height * 2 + 5),
        ]
        blocks.append(Block(left_wall_vertices, self.settings.slv, restitution=self.settings.restitution, image=self.edge_horz))

        # Bottom wall (textured)
       
        bottom_wall = self.generate_bottom_wall()
        blocks.append(bottom_wall)

        # Top bar (thin decorative strip at very top)
        top_bar_vertices = [
            (0, 0),
            (0, 8),                             # height 5 pixels
            (self.screen_width, 8),
            (self.screen_width, 0)
        ]
        blocks.append(Block(top_bar_vertices, self.settings.slv, restitution=self.settings.restitution, image=self.edge_horz))

        

        return blocks

    def get_lane_center(self):
        lane_left = self.playfield_width
        return lane_left + self.right_margin / 2

    def get_lane_bottom(self):
        return self.screen_height - 10

    def get_plunger_base_y(self):
        return self.screen_height - 10
    
    