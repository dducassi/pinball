import math
from blocks import Block

class OneWayBlock(Block):
    def __init__(self, vertices, color, restitution=0.8, direction='left'):
        """
        direction: 'left' means ball can pass through when moving leftwards (exiting lane).
        """
        super().__init__(vertices, color, restitution)
        self.direction = direction
        # Precompute average x (for side detection)
        self.center_x = sum(v[0] for v in vertices) / len(vertices)

    def collide(self, ball_x, ball_y, ball_dx, ball_dy, ball_radius):
        # First, let base collision detect and resolve normally
        new_x, new_y, new_dx, new_dy, hit = super().collide(
            ball_x, ball_y, ball_dx, ball_dy, ball_radius)

        if not hit:
            return new_x, new_y, new_dx, new_dy, False

        # Determine which side the ball is on
        if ball_x < self.center_x:
            side = 'left'
        else:
            side = 'right'

        # Determine if motion is towards the wall
        if self.direction == 'left':
            # Allow passage only when moving left from right side (exiting lane)
            if side == 'right' and ball_dx < 0:
                # Allowed direction – ignore collision (let ball pass)
                return ball_x, ball_y, ball_dx, ball_dy, False
            else:
                # Blocked direction – apply collision
                return new_x, new_y, new_dx, new_dy, True
        else:
            # (for completeness, could handle other directions)
            return new_x, new_y, new_dx, new_dy, True