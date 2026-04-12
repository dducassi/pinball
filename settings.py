##SETTINGS##

#Settings for Pinball



class Settings:

    def __init__(self):
        
        # Ball properties
        self.br = 10  # ball radius
        self.phys_runs = 10

        # Margins for UI and plunger lane
        self.top_margin = 100          # height of top message area
        self.right_margin = self.br * 3.5         # width of right plunger lane

        # Screen dimensions
        self.screen_width = 335 + self.right_margin
        self.screen_height = 670 + self.top_margin

        
        

        # Playfield dimensions (where game elements are placed)
        self.playfield_width = self.screen_width - self.right_margin
        self.playfield_height = self.screen_height - self.top_margin




        # Block properties
        self.block_bounce = 0.75
        

        # Flipper properties
        self.f_length = 31/168 * self.playfield_width + (self.br / 20)
        self.restitution = 0.75


        # Bumper properties
        self.bump_rad = 8/100 * self.playfield_height   # bumper radius
        self.num_bumps = 3
        self.ocolors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                         (255, 130, 0), (130, 0, 255)]  # Colors for the bumpers
        self.pph = 100  # Points per hit
        self.bump_bounce = 1.2

        # Lane properties:s
        self.lane_wall_thickness = 7

        # Colors
        self.wht = (255, 255, 255)
        self.blk = (0, 0, 0)
        self.red = (255, 30, 0)
        self.blu = (0, 100, 255)
        self.grn = (0, 255, 0)
        self.ylw = (255, 255, 255)
        self.ong = (255, 130, 0)
        self.ppl = (130, 0, 255)
        self.gry = (100, 100, 100)
        self.slv = (150, 150, 150)

        self.music_volume = 0.8   # 0.0 to 1.0

        self.init_dynamic_settings()
    
    def init_dynamic_settings(self):
        self.bs = 1   # ball speed
        self.bsmax = (3 * self.br) / self.phys_runs # max ball speed














