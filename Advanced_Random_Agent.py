import random
import math
from Constants import BULLET_SPEED


class Advanced_Random_Agent:
    """A smarter scripted opponent for training.

    epsilon controls randomness:
      1.0 = pure random (like Random_Agent)
      0.0 = fully advanced (aim / dodge / shoot)
      0.5 = 50% chance of random each step

    State tensor layout (mirrors Enviorment.state()):
      [0..3]       tank1: x/W, y/H, cos(a), sin(a)
      [4..23]      tank1 bullets  (5 × x/W, y/H, cos(a), sin(a))
      [24..27]     tank2: x/W, y/H, cos(a), sin(a)  ← this agent IS tank2
      [28..47]     tank2 bullets  (5 × x/W, y/H, cos(a), sin(a))
    """

    # Tunable
    AIM_THRESH      = 12    # degrees: close enough to shoot
    DODGE_DIST      = 250   # pixels: bullet this close triggers dodge

    def __init__(self, epsilon=0.0):
        """epsilon: probability of taking a fully random action each step (0.0–1.0)."""
        self.epsilon = epsilon
        self._action = [0] * 5   # [forward, back, rotate_left, rotate_right, shoot]
        self._timer = 0

    # ------------------------------------------------------------------

    def get_Action(self, events=None, state=None, epoch=None):
        if state is None or random.random() < self.epsilon:
            return self._random_action()

        # --- Unpack relevant state values ----------------------------
        from Constants import WIDTH, HEIGHT
        t1x  = float(state[0]) * WIDTH;   t1y  = float(state[1]) * HEIGHT
        t2x  = float(state[24]) * WIDTH;  t2y  = float(state[25]) * HEIGHT
        t2a  = math.degrees(math.atan2(float(state[27]), float(state[26])))

        # --- 1. Dodge check (tank1 bullets toward tank2) -------------
        dodge = self._dodge_needed(state, t2x, t2y)
        if dodge:
            # strafe: move forward + rotate away
            self._set(forward=1, back=0, left=0, right=1, shoot=0)
            return self._action

        # --- 2. Aim toward tank1 -------------------------------------
        dx = t1x - t2x
        dy = t2y - t1y   # flip pygame y
        phi = math.degrees(math.atan2(dy, dx))
        err = self._wrap(phi - t2a)

        # --- 3. Shoot when aimed -------------------------------------
        if abs(err) < self.AIM_THRESH:
            self._set(forward=0, back=0, left=0, right=0, shoot=1)
            return self._action

        # Rotate toward tank1 (also keep moving forward occasionally)
        moving = 1 if random.random() < 0.4 else 0
        if err > 0:
            self._set(forward=moving, back=0, left=1, right=0, shoot=0)
        else:
            self._set(forward=moving, back=0, left=0, right=1, shoot=0)
        return self._action

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _random_action(self):
        """Purely random action (same logic as Random_Agent)."""
        move = random.randint(0, 2)
        turn = random.randint(0, 2)
        self._action[0] = 1 if move == 1 else 0
        self._action[1] = 1 if move == 2 else 0
        self._action[2] = 1 if turn == 1 else 0
        self._action[3] = 1 if turn == 2 else 0
        self._action[4] = 1 if random.random() < 0.1 else 0
        return self._action

    def _dodge_needed(self, state, t2x, t2y):
        """Return True if any tank1 bullet is close and heading toward tank2."""
        from Constants import WIDTH, HEIGHT
        for i in range(5):
            base = 4 + i * 4
            bx  = float(state[base]) * WIDTH
            by  = float(state[base + 1]) * HEIGHT
            bc  = float(state[base + 2])
            bs  = float(state[base + 3])
            if bx == 0 and by == 0:
                continue
            vx =  BULLET_SPEED * bc
            vy = -BULLET_SPEED * bs
            tx, ty = t2x - bx, t2y - by
            dist = math.hypot(tx, ty)
            if dist < self.DODGE_DIST and vx * tx + vy * ty > 0:
                return True
        return False

    @staticmethod
    def _wrap(a):
        a = a % 360
        if a > 180:
            a -= 360
        return a

    @staticmethod
    def _set_list(lst, forward, back, left, right, shoot):
        lst[0] = forward
        lst[1] = back
        lst[2] = left
        lst[3] = right
        lst[4] = shoot

    def _set(self, forward, back, left, right, shoot):
        self._action[0] = forward
        self._action[1] = back
        self._action[2] = left
        self._action[3] = right
        self._action[4] = shoot
