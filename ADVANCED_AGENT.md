# Advanced Random Agent

A scripted opponent used during DDQN training. It combines basic combat behaviors (dodge, aim, shoot) with controllable randomness via an `epsilon` parameter.

## Epsilon (Randomness Control)

| Epsilon | Behavior |
|---------|----------|
| `1.0` | Pure random — identical to `Random_Agent` |
| `0.0` | Fully advanced — always uses aim/dodge/shoot logic |
| `0.5` | 50/50 — each step has a 50% chance of random action |

Set via `OPPONENT_EPSILON` in `Constants.py` (default: 0.5).

## Decision Flow

Each step, the agent runs through a priority-based pipeline:

```
┌────────────────────────┐
│  random.random() < ε?  │──yes──▶ Random action
└──────────┬─────────────┘
           no
           ▼
┌────────────────────────┐
│  Incoming bullet close │──yes──▶ Dodge (forward + rotate right)
│  and heading toward me?│
└──────────┬─────────────┘
           no
           ▼
┌────────────────────────┐
│  Aim error < 12°?      │──yes──▶ Shoot
└──────────┬─────────────┘
           no
           ▼
┌────────────────────────┐
│  Rotate toward enemy   │
│  (40% chance also move)│
└────────────────────────┘
```

## 1. Random Action

Same logic as `Random_Agent`:
- **Move**: 1/3 forward, 1/3 backward, 1/3 stay
- **Turn**: 1/3 left, 1/3 right, 1/3 none
- **Shoot**: 10% chance

## 2. Dodge

Checks all 5 of tank 1's bullet slots. A dodge is triggered if **any** bullet satisfies both:
- Distance to this agent (tank 2) < `DODGE_DIST` (250 px)
- Bullet velocity vector is pointing **toward** tank 2 (positive dot product)

**Dodge action**: move forward + rotate right — a simple strafe to get out of the way.

### How "heading toward me" works

The bullet's velocity vector is $(v_x, v_y)$ and the vector from bullet to tank 2 is $(t_x, t_y)$. If their **dot product** $v_x \cdot t_x + v_y \cdot t_y > 0$, the bullet is approaching.

## 3. Aim

Computes the angular error between tank 2's current heading and the bearing toward tank 1:

1. **Bearing**: $\phi = \text{atan2}(t2_y - t1_y,\; t1_x - t2_x)$ (y flipped for pygame)
2. **Current heading**: $\theta = \text{atan2}(\sin(a),\; \cos(a))$ from state tensor
3. **Error**: $|\phi - \theta|$ wrapped to $[-180°, 180°]$

If the error is within `AIM_THRESH` (12°), the agent **shoots**.

Otherwise, it **rotates** in the direction that reduces the error (left if positive, right if negative). There's a 40% chance it also moves forward while turning, making it harder to hit.

## Tunable Parameters

| Parameter | Value | Location |
|-----------|-------|----------|
| `epsilon` | 0.5 | `Constants.py` → `OPPONENT_EPSILON` |
| `AIM_THRESH` | 12° | Class constant |
| `DODGE_DIST` | 250 px | Class constant |

## State Reading

The agent reads from the same 48-value state tensor as the DQN agent. It denormalizes positions back to pixels (`× WIDTH`, `× HEIGHT`) for distance calculations, and reconstructs angles from the `cos`/`sin` components using `atan2`.

| State Index | Used For |
|-------------|----------|
| 0, 1 | Tank 1 position (enemy to aim at) |
| 24–27 | Tank 2 position + heading (self) |
| 4–23 | Tank 1 bullets (to dodge) |
