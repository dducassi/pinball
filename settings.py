##SETTINGS##

#Settings for Pinball



class Settings:

    def __init__(self):
        # Screen dimensions
        self.screen_width = 350
        self.screen_height = 700

        # Ball properties
        self.br = 10  # ball radius
        self.phys_runs = 2

        # Block properties
        self.block_bounce = 0.8
        

        # Flipper properties
        self.f_length = 4/21 * self.screen_width
        self.flip_force = 1.25
        self.deadf_bounce = 0.75
        self.collision_samples = 4  # Number of path samples
        self.collision_tolerance = 2  # Collision margin

        # Obstacle properties
        self.orad = 8/100 * self.screen_height   # obstacle radius
        self.num_obs = 3
        self.ocolors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                         (255, 130, 0), (130, 0, 255)]  # Colors for the obstacles
        self.pph = 10  # Points per hit
        self.obs_bounce = 1.2

        # Colors
        self.wht = (255, 255, 255)
        self.blk = (0, 0, 0)
        self.red = (255, 0, 0)
        self.blu = (0, 100, 255)
        self.grn = (0, 255, 0)
        self.ylw = (255, 255, 0)
        self.ong = (255, 130, 0)
        self.ppl = (130, 0, 255)
        self.gry = (100, 100, 100)
        self.slv = (240, 240, 240)

        self.init_dynamic_settings()
    
    def init_dynamic_settings(self):
        self.bs = 5   # ball speed
        self.bsmax = 20 # max ball speed














