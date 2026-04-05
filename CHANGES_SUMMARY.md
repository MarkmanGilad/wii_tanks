# Summary of Changes (since initial commit)

All changes were made on **March 28, 2026**, across 5 commits on top of the initial `init` commit.

---

## Overview

| File | Change Type |
|------|-------------|
| `Enviorment.py` | Modified — state representation overhauled |
| `Dqn.py` | Modified — input size updated |
| `Advanced_Random_Agent.py` | Modified — adapted to new state layout |
| `Constants.py` | Modified — tuned reward values, added training constants |
| `trainer.py` | Modified — DDQN fix, logging improvements, configurable constants |
| `trainer_DDQN.py` | **Deleted** — stub file removed |
| `REWARD.md` | **Added** — reward function documentation |
| `STATE_ACTION.md` | **Added** — state & action representation documentation |
| `ADVANCED_AGENT.md` | **Added** — advanced random agent documentation |

**Total: +419 lines, −80 lines across 9 files.**

---

## 1. State Representation Overhaul (`Enviorment.py`, `Dqn.py`)

The state tensor was completely reworked:

| Aspect | Before | After |
|--------|--------|-------|
| **Size** | 36 values | 48 values |
| **Positions** | Raw pixels (0–1500, 0–900) | Normalized (`x/WIDTH`, `y/HEIGHT`) → [0, 1] |
| **Angles** | Raw degrees (0°–360°) | `cos(angle)`, `sin(angle)` → [−1, 1] |
| **Values per entity** | 3 (x, y, angle) | 4 (x/W, y/H, cos, sin) |
| **Empty bullet padding** | `[0, 0, 0]` | `[0, 0, 0, 0]` |

**Why:** Raw angles have a discontinuity at 0°/360° — sin/cos encoding is continuous and wraps smoothly. Normalized positions put all features on similar scales for the neural network.

The DQN input size in `Dqn.py` was updated from `36` to `48` to match.

---

## 2. Reward Function Tuning (`Constants.py`)

Several reward shaping constants were reduced to avoid overwhelming the terminal reward signal:

| Constant | Before | After |
|----------|--------|-------|
| `AIM_BONUS_NEAR` | 0.3 | 0.05 |
| `AIM_BONUS_LOCK` | 1.0 | 0.1 |

---

## 3. Training Constants Centralized (`Constants.py`)

New training hyperparameters were moved from `trainer.py` into `Constants.py` for better configurability:

| Constant | Value | Purpose |
|----------|-------|---------|
| `LEARNING_RATE` | 0.0001 | Optimizer LR |
| `TARGET_UPDATE_FREQ` | 1000 | Gradient steps between target-net copies |
| `WIN_RATE_WINDOW` | 20 | Episodes for rolling win-rate |
| `CHECKPOINT_INTERVAL` | 100 | Save checkpoint every N epochs |
| `OPPONENT_EPSILON` | 0.5 | Advanced Random Agent randomness |

---

## 4. Trainer Improvements (`trainer.py`)

### 4a. Switched from DQN to **Double DQN (DDQN)**

The Q-learning target was changed from standard DQN to DDQN to reduce overestimation bias:

- **Before:** Target network both selects and evaluates the next action.
- **After:** Online network selects the best next action; target network evaluates it. Target evaluation wrapped in `torch.no_grad()`.

### 4b. Target Network Update Changed

- **Before:** Target net updated every `C` **episodes** (epoch-based), with soft-update code commented out.
- **After:** Target net updated every `C` **gradient steps** (step-based, `TARGET_UPDATE_FREQ = 1000`), using hard copy (`fix_update`).

### 4c. Optimizer Step Order Fixed

- **Before:** `loss.backward()` → `optim.step()` → `optim.zero_grad()` (zero-grad after step).
- **After:** `optim.zero_grad()` → `loss.backward()` → `optim.step()` (zero-grad before backward, standard practice).

### 4d. Logging & Config Improvements

- Win-rate window reduced from 100 to 20 episodes for faster feedback.
- WandB config now logs additional hyperparameters: epsilon range, buffer size, opponent epsilon, tank/bullet speeds, max ammo.
- Window title shows training run number.
- Print output includes run number.

### 4e. Deleted `trainer_DDQN.py`

A stub file (only 15 lines of boilerplate, no actual training logic) was removed since DDQN was integrated into the main `trainer.py`.

---

## 5. Advanced Random Agent Updated (`Advanced_Random_Agent.py`)

Adapted to match the new 48-value state tensor layout:

- State indices updated (e.g., tank2 position moved from `[18,19,20]` to `[24,25,26,27]`).
- Positions are denormalized back to pixels (`× WIDTH`, `× HEIGHT`) for distance calculations.
- Angles reconstructed from cos/sin using `atan2` instead of reading raw degrees.
- Bullet loop stride changed from 3 to 4 values per bullet.

---

## 6. Documentation Added

Three new markdown files were added to document the project:

- **`STATE_ACTION.md`** — Describes the 48-value state tensor layout, the 18 discrete actions, normalization details, and conversion examples.
- **`REWARD.md`** — Documents the full reward function: terminal rewards, step penalty, aim improvement, alignment bonuses, shoot shaping, and danger reduction, with formulas.
- **`ADVANCED_AGENT.md`** — Explains the advanced random agent's decision pipeline (dodge → aim → shoot → wander), tunable parameters, and state reading.
