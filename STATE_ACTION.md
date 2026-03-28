# State & Action Representation

## Action

### Raw Form (before tensor)

An action is a **list of 5 binary integers** `[forward, back, rotate_left, rotate_right, shoot]`:

| Index | Bit | Effect |
|-------|-----|--------|
| 0 | `forward` | Move forward (`TANK_SPEED` = 7 px/frame in facing direction) |
| 1 | `back` | Move backward |
| 2 | `rotate_left` | Rotate +5° |
| 3 | `rotate_right` | Rotate −5° |
| 4 | `shoot` | Fire a bullet (if ammo < `MAX_AMMUNITION` = 5) |

Multiple bits can be set simultaneously (e.g. move forward + rotate + shoot).

### Discrete Action Space

Only **18 predefined combinations** are used (not all 32 possible):

| Index | Action | Description |
|-------|--------|-------------|
| 0 | `[0,0,0,0,0]` | Do nothing |
| 1 | `[0,1,0,0,0]` | Back |
| 2 | `[0,1,0,1,0]` | Back + rotate right |
| 3 | `[0,1,0,1,1]` | Back + rotate right + shoot |
| 4 | `[0,1,1,0,0]` | Back + rotate left |
| 5 | `[0,1,1,0,1]` | Back + rotate left + shoot |
| 6 | `[1,0,0,0,0]` | Forward |
| 7 | `[1,0,1,0,0]` | Forward + rotate left |
| 8 | `[1,0,1,0,1]` | Forward + rotate left + shoot |
| 9 | `[1,0,0,1,0]` | Forward + rotate right |
| 10 | `[1,0,0,1,1]` | Forward + rotate right + shoot |
| 11 | `[0,0,1,0,0]` | Rotate left |
| 12 | `[0,0,0,1,0]` | Rotate right |
| 13 | `[0,0,1,0,1]` | Rotate left + shoot |
| 14 | `[0,0,0,1,1]` | Rotate right + shoot |
| 15 | `[1,0,0,0,1]` | Forward + shoot |
| 16 | `[0,1,0,0,1]` | Back + shoot |
| 17 | `[0,0,0,0,1]` | Shoot only |

### Tensor Form

- The DQN outputs **18 Q-values** (one per action index).
- During training, actions are stored in the replay buffer as `torch.int` tensors of shape `(5,)`.
- `actions_to_indices()` converts a batch of 5-bit action tensors to their discrete indices for Q-value gathering.

---

## State

### Raw Form (game objects)

Before conversion, the state lives in pygame game objects:

| Entity | Raw Properties |
|--------|----------------|
| Tank 1 (agent) | `rect.x` (px), `rect.y` (px), `angle` (degrees, 0°=right, CCW positive) |
| Tank 1 bullets | List of up to 5 bullets, each with `rect.x`, `rect.y`, `angle` |
| Tank 2 (enemy) | `rect.x` (px), `rect.y` (px), `angle` (degrees) |
| Enemy bullets | List of up to 5 bullets, each with `rect.x`, `rect.y`, `angle` |

- Positions are in **pixels**: x ∈ [0, 1500], y ∈ [0, 900]
- Angles are in **degrees**: pygame convention (0° = right, positive = counter-clockwise)
- Bullet lists are variable-length (0 to 5)

### Tensor Form

`state()` returns a `torch.float32` tensor of **48 values**:

| Index | Content | Encoding |
|-------|---------|----------|
| 0 | Tank 1 x | `rect.x / WIDTH` → [0, 1] |
| 1 | Tank 1 y | `rect.y / HEIGHT` → [0, 1] |
| 2 | Tank 1 cos | `cos(angle°)` → [−1, 1] |
| 3 | Tank 1 sin | `sin(angle°)` → [−1, 1] |
| 4–7 | Bullet 1 (tank 1) | Same 4-value encoding |
| 8–11 | Bullet 2 (tank 1) | Same 4-value encoding |
| 12–15 | Bullet 3 (tank 1) | Same 4-value encoding |
| 16–19 | Bullet 4 (tank 1) | Same 4-value encoding |
| 20–23 | Bullet 5 (tank 1) | Same 4-value encoding |
| 24 | Tank 2 x | `rect.x / WIDTH` → [0, 1] |
| 25 | Tank 2 y | `rect.y / HEIGHT` → [0, 1] |
| 26 | Tank 2 cos | `cos(angle°)` → [−1, 1] |
| 27 | Tank 2 sin | `sin(angle°)` → [−1, 1] |
| 28–31 | Bullet 1 (enemy) | Same 4-value encoding |
| 32–35 | Bullet 2 (enemy) | Same 4-value encoding |
| 36–39 | Bullet 3 (enemy) | Same 4-value encoding |
| 40–43 | Bullet 4 (enemy) | Same 4-value encoding |
| 44–47 | Bullet 5 (enemy) | Same 4-value encoding |

### Normalization Details

| Property | Raw Range | Normalized Range | Transform |
|----------|-----------|------------------|-----------|
| x position | 0 – 1500 px | 0 – 1 | `x / WIDTH` |
| y position | 0 – 900 px | 0 – 1 | `y / HEIGHT` |
| angle | 0° – 360° | −1 – 1 (×2) | `cos(angle)`, `sin(angle)` |

**Why sin/cos?** A raw angle has a discontinuity at 0°/360° — the network would see 1° and 359° as far apart when they are nearly the same direction. Sin/cos encoding is continuous and wraps smoothly.

### Empty Bullet Slots

When fewer than 5 bullets exist, the remaining slots are **zero-padded** with `[0, 0, 0, 0]`. Note that `cos=0, sin=0` is not a valid unit vector, so the network can learn to distinguish padding from real bullets.

---

## Conversion Summary

```
Game Objects                     →  state() tensor
─────────────────────────────        ──────────────
tank1.rect.x = 750               →  750/1500 = 0.5
tank1.rect.y = 450               →  450/900  = 0.5
tank1.angle  = 45°                →  cos(45°) = 0.707, sin(45°) = 0.707
bullet.rect.x = 300              →  300/1500 = 0.2
(no bullet in slot)               →  [0, 0, 0, 0]

Action list [1,0,1,0,1]          →  torch.tensor([1,0,1,0,1], dtype=int)
  ↓ DQN output index             →  index 8 (forward + rotate left + shoot)
```
