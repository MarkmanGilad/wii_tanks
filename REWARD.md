# Reward Function

The reward function guides the DDQN agent to learn effective combat behavior.
It is computed from two consecutive state tensors (`state`, `next_state`), the action taken, and a terminal flag.

## State Layout

Each state is a 48-value tensor with normalized positions and sin/cos angles:

| Index | Content |
|-------|---------|
| 0–3   | Tank 1 (agent): `x/W`, `y/H`, `cos(angle)`, `sin(angle)` |
| 4–23  | Tank 1 bullets (5 slots × 4 values each) |
| 24–27 | Tank 2 (enemy): `x/W`, `y/H`, `cos(angle)`, `sin(angle)` |
| 28–47 | Enemy bullets (5 slots × 4 values each) |

Empty bullet slots are zero-padded.

---

## Reward Components

### 1. Terminal Rewards

| Condition | Reward | Constant |
|-----------|--------|----------|
| Enemy destroyed (win) | +100 | `REWARD_WIN` |
| Own tank destroyed (lose) | −100 | `REWARD_LOSE` |

When the episode ends, only the terminal reward is returned — no shaping is added.

### 2. Step Penalty

$$r_{\text{step}} = -0.02$$

A small negative reward every step (`STEP_PENALTY`), discouraging the agent from stalling and encouraging it to end the episode quickly.

### 3. Aim Improvement

$$r_{\text{aim}} = K_{\text{AIM}} \times (\text{prev\_err} - \text{curr\_err})$$

- **Aim error** is the absolute angular difference (in degrees) between where tank 1 is facing and the direction toward tank 2.
- The reward is proportional to the *reduction* in aim error between consecutive steps.
- `K_AIM = 0.1` scales this component.

**How aim error is computed:**
1. Compute the bearing from tank 1 to tank 2: $\phi = \text{atan2}(\Delta y, \Delta x)$
2. Get tank 1's heading: $\theta = \text{atan2}(\sin(a), \cos(a))$
3. Error = $|\phi - \theta|$ wrapped to $[0°, 180°]$

### 4. Alignment Bonuses

| Condition | Bonus | Constants |
|-----------|-------|-----------|
| Aim error < 8° | +0.05 | `AIM_BONUS_NEAR`, `AIM_THRESH_NEAR` |
| Aim error < 5° | +0.10 (additional) | `AIM_BONUS_LOCK`, `AIM_THRESH_LOCK` |

These flat bonuses reward the agent for maintaining good alignment with the enemy.
When aim error is below 5°, both bonuses are received (total +0.15 per step).

### 5. Shoot Shaping

When the agent fires (action bit 4 = 1):

| Condition | Reward | Constant |
|-----------|--------|----------|
| Any shot fired | −0.2 | `SHOOT_PENALTY` |
| Shot fired while aim error < 8° | +1.0 (additional) | `SHOOT_BONUS_AIMED` |

- **Anti-spam:** every shot incurs a −0.2 penalty to discourage random shooting.
- **Good-shot bonus:** if the agent shoots while well-aimed (< 8°), it receives +1.0 additional, for a net reward of +0.8 per well-aimed shot.

### 6. Danger Reduction

$$r_{\text{danger}} = K_{\text{DANGER}} \times (\text{danger}_{\text{prev}} - \text{danger}_{\text{curr}})$$

- `K_DANGER = 0.5`

**Danger score** is the sum over all active enemy bullets of:

$$\frac{1}{d + 1}$$

where $d$ is the Euclidean distance from the bullet to tank 1, but **only** for bullets whose velocity vector points toward the tank (i.e., the bullet is approaching).

This rewards the agent for moving away from incoming bullets and penalizes moving into danger.

---

## Full Formula (non-terminal)

$$r = \underbrace{-0.02}_{\text{step}} + \underbrace{0.1 \cdot \Delta\text{aim}}_{\text{aim improvement}} + \underbrace{\text{alignment bonuses}}_{\text{if aligned}} + \underbrace{\text{shoot shaping}}_{\text{if shooting}} + \underbrace{0.5 \cdot \Delta\text{danger}}_{\text{danger reduction}}$$

---

## Constants Summary

| Constant | Value | Purpose |
|----------|-------|---------|
| `REWARD_WIN` | +100 | Terminal win reward |
| `REWARD_LOSE` | −100 | Terminal loss reward |
| `STEP_PENALTY` | −0.02 | Per-step cost |
| `K_AIM` | 0.1 | Aim improvement scale |
| `AIM_BONUS_NEAR` | +0.05 | Bonus for aim error < 8° |
| `AIM_THRESH_NEAR` | 8° | Near-aim threshold |
| `AIM_BONUS_LOCK` | +0.10 | Bonus for aim error < 5° |
| `AIM_THRESH_LOCK` | 5° | Lock-on threshold |
| `SHOOT_PENALTY` | −0.2 | Firing cost |
| `SHOOT_BONUS_AIMED` | +1.0 | Well-aimed shot bonus |
| `K_DANGER` | 0.5 | Danger reduction scale |

All constants are defined in `Constants.py`.
