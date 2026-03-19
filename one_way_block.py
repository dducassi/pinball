import math
from blocks import Block

class OneWayBlock(Block):
    def __init__(self, vertices, color, restitution=0.8, direction='left'):
        super().__init__(vertices, color, restitution)
        self.direction = direction  # 'left' means allow leftward movement

    def collide(self, ball_x, ball_y, ball_dx, ball_dy, ball_radius):
        new_x, new_y, new_dx, new_dy, hit = super().collide(
            ball_x, ball_y, ball_dx, ball_dy, ball_radius)

        if not hit:
            return new_x, new_y, new_dx, new_dy, False

        # Allow passage only when moving left (exiting lane)
        if self.direction == 'left' and ball_dx < 0:
            return ball_x, ball_y, ball_dx, ball_dy, False
        else:
            return new_x, new_y, new_dx, new_dy, True