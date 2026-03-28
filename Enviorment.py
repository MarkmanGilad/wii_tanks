import pygame
import numpy as np
import torch
from Constants import *
import Dqn_Agent
from Tank import Tank
from Explosion import Explosion
import random

class Enviroment:
    def __init__(self) -> None:
        self._rng = random.Random()
        self.Bullet_Group = []
        self.Enemy_Bullet_Group = []
        self.Explosion_Group = pygame.sprite.Group()
        self.init_tank()
        # self.tank1 = Tank((200,800),0, PLAYER_IMAGE,self.Bullet_Group)
        # self.tank2 = Tank((1300,200),180, ENEMY_IMAGE,self.Enemy_Bullet_Group)
        # self.tank2 = Dqn_Agent((1300,200),180, ENEMY_URL,self.Enemy_Bullet_Group)

    def init_tank (self):
        xl, yl, dl = self._rng.randint(190, 210), self._rng.randint(200, 800), self._rng.randint(0, 360) #200, 800, 0
        xr, yr, dr = self._rng.randint(1290, 1310), self._rng.randint(200, 800), self._rng.randint(0, 360) #1300, 200, 180
        if self._rng.random() < 0.5:
            self.tank1 = Tank((xl,yl),dl, PLAYER_IMAGE,self.Bullet_Group)
            self.tank2 = Tank((xr,yr),dr, ENEMY_IMAGE,self.Enemy_Bullet_Group)
        else:
            self.tank1 = Tank((xr,yr),dr, PLAYER_IMAGE,self.Bullet_Group)
            self.tank2 = Tank((xl,yl),dl, ENEMY_IMAGE,self.Enemy_Bullet_Group)
    
    def reset(self):
        self.Bullet_Group = []
        self.Enemy_Bullet_Group = []
        self.Explosion_Group = pygame.sprite.Group()
        self.init_tank()
        return self.state()

    def init_screen(self):
        
        pygame.init()
        
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        pygame.display.set_caption('Tanks')
        self.clock = pygame.time.Clock()

        self.main_surf = pygame.Surface((WIDTH, HEIGHT))
        self.backround = pygame.image.load("Data\wood.png")
        self.backround = pygame.transform.scale(self.backround,(WIDTH,HEIGHT))
        self.main_surf.blit(self.backround, (0,0))
        screen.blit(self.main_surf, (0,0))

    def render (self):
        self.main_surf.blit(self.backround, (0,0))
        self.tank1.draw(self.main_surf)
        self.tank2.draw(self.main_surf)
        self.Explosion_Group.update()
        for bullet in self.Bullet_Group:
            bullet.draw(self.main_surf)
        for bullet in self.Enemy_Bullet_Group:
            bullet.draw(self.main_surf)
        self.Explosion_Group.draw(self.main_surf)
        screen.blit(self.main_surf, (0,0))
        pygame.display.update()
        self.clock.tick(FPS)
    

    def move(self, action1 ,action2):
        
        self.tank1.action(action1)
        for bullet in self.Bullet_Group:
            bullet.move()
            if bullet.rect.x > WIDTH or bullet.rect.x < 0 or bullet.rect.y > HEIGHT or bullet.rect.y < 0:
                self.Bullet_Group.remove(bullet)
    
        self.tank2.action(action2)
        for bullet in self.Enemy_Bullet_Group:
            bullet.move()
            if bullet.rect.x > WIDTH or bullet.rect.x < 0 or bullet.rect.y > HEIGHT or bullet.rect.y < 0:
                self.Enemy_Bullet_Group.remove(bullet)
        
    # reward() was previously a placeholder; real implementation below
        
    
    def end_of_game(self):
        for bullet in self.Bullet_Group:
            if bullet.rect.colliderect(self.tank2.rect):
                self.Bullet_Group.remove(bullet)
                explosion = Explosion(self.tank2.rect.center)  # Create explosion at tank2's position
                self.Explosion_Group.add(explosion)
                return 1
        for bullet in self.Enemy_Bullet_Group:
            if bullet.rect.colliderect(self.tank1.rect):
                self.Enemy_Bullet_Group.remove(bullet)
                explosion = Explosion(self.tank1.rect.center)  # Create explosion at tank1's position
                self.Explosion_Group.add(explosion)
                return 2
        return 0
    
    def state(self):
        state_list = []
        state_list.append(self.tank1.rect.x) #1
        state_list.append(self.tank1.rect.y) #2
        state_list.append(self.tank1.angle)  #3
        for bullet in self.Bullet_Group:      #18
            state_list.append(bullet.rect.x)
            state_list.append(bullet.rect.y)
            state_list.append(bullet.angle)
        for i in range(5 - len(self.Bullet_Group)):
            state_list.append(0)
            state_list.append(0)
            state_list.append(0)
        state_list.append(self.tank2.rect.x) #6
        state_list.append(self.tank2.rect.y)
        state_list.append(self.tank2.angle) #8
        for bullet in self.Enemy_Bullet_Group:
            state_list.append(bullet.rect.x)
            state_list.append(bullet.rect.y)
            state_list.append(bullet.angle)
        for i in range(5 - len(self.Enemy_Bullet_Group)):
            state_list.append(0)
            state_list.append(0)
            state_list.append(0)
        return torch.tensor(state_list, dtype=torch.float32)

    def reward_old(self):
        """Return a scalar reward based on distance of bullets to targets.
        - Own bullets that are heading toward the enemy and are close give
          positive reward (closer -> larger).
        - Enemy bullets heading toward our tank give negative reward (closer -> larger magnitude).
        Uses `BULLET_SPEED` so checks are consistent with bullet velocity magnitude.
        """
        import math

        reward = 0.0
        # Tunable parameters
        perp_threshold = 30.0   # pixels: how close the path must be
        max_dist = 1000.0       # pixels: beyond this distance reward is negligible
        contrib = 1.0           # base magnitude per bullet

        # Own bullets: positive reward if on-course and close to enemy
        # Also penalize recent shots that clearly don't head near the enemy
        recent_fire_dist = 40.0    # pixels: how far from shooter counts as "just fired"
        miss_dist_threshold = 200.0
        miss_penalty = 0.5
        for b in self.Bullet_Group:
            bx, by = b.rect.center
            tx = self.tank2.rect.centerx - bx
            ty = self.tank2.rect.centery - by
            vx, vy = b.vx, b.vy
            speed = BULLET_SPEED
            dot = vx * tx + vy * ty
            perp = abs(vx * ty - vy * tx) / (speed if speed != 0 else 1.0)
            dist = math.hypot(tx, ty)

            on_course = (dot > 0 and perp <= perp_threshold and dist <= max_dist)
            if on_course:
                scale = max(0.0, (max_dist - dist) / max_dist)
                reward += contrib * scale

            # If the bullet was just fired (close to our tank) and is not on-course
            # or is already too far from the enemy, apply a miss penalty.
            sx = bx - self.tank1.rect.centerx
            sy = by - self.tank1.rect.centery
            dist_from_shooter = math.hypot(sx, sy)
            if dist_from_shooter <= recent_fire_dist and (not on_course or dist > miss_dist_threshold):
                reward -= miss_penalty

        # Enemy bullets: negative reward if on-course and close to our tank
        for b in self.Enemy_Bullet_Group:
            bx, by = b.rect.center
            tx = self.tank1.rect.centerx - bx
            ty = self.tank1.rect.centery - by
            vx, vy = b.vx, b.vy
            speed = BULLET_SPEED
            dot = vx * tx + vy * ty
            if dot <= 0:
                continue
            perp = abs(vx * ty - vy * tx) / (speed if speed != 0 else 1.0)
            if perp > perp_threshold:
                continue
            dist = math.hypot(tx, ty)
            if dist > max_dist:
                continue
            scale = max(0.0, (max_dist - dist) / max_dist)
            reward -= contrib * scale

        return float(reward)


    def reward(self, state, action, next_state, done=0):
        import math
        
        # Terminal
        if done == 1:
            return REWARD_WIN
        if done == 2:
            return REWARD_LOSE

        # State indices:
        # [0,1,2] = tank1 x,y,angle  [18,19,20] = tank2 x,y,angle
        # [21+i*3 .. 23+i*3] for i in 0..4 = enemy bullet x,y,angle
        def aim_err(s):
            dx = s[18].item() - s[0].item()
            dy = s[1].item()  - s[19].item()  # flip pygame y-axis
            phi = math.degrees(math.atan2(dy, dx))
            err = (phi - s[2].item()) % 360
            if err > 180:
                err -= 360
            return abs(err)

        def danger(s):
            t1x, t1y = s[0].item(), s[1].item()
            total = 0.0
            for i in range(5):
                bx, by, ba = s[21+i*3].item(), s[22+i*3].item(), s[23+i*3].item()
                if bx == 0 and by == 0:
                    continue  # padded empty slot
                vx =  BULLET_SPEED * math.cos(math.radians(ba))
                vy = -BULLET_SPEED * math.sin(math.radians(ba))
                tx, ty = t1x - bx, t1y - by
                if vx * tx + vy * ty > 0:
                    total += 1.0 / (math.hypot(tx, ty) + 1.0)
            return total

        r = STEP_PENALTY

        prev_err = aim_err(state)
        curr_err = aim_err(next_state)

        r += K_AIM * (prev_err - curr_err)         # aim improvement
        if curr_err < AIM_THRESH_NEAR:
            r += AIM_BONUS_NEAR                     # alignment bonus
        if curr_err < AIM_THRESH_LOCK:
            r += AIM_BONUS_LOCK                     # lock-on bonus

        if action is not None and len(action) > 4 and action[4] == 1:
            r += SHOOT_PENALTY                      # shoot penalty (anti-spam)
            if curr_err < AIM_THRESH_NEAR:
                r += SHOOT_BONUS_AIMED              # good-shot bonus

        r += K_DANGER * (danger(state) - danger(next_state))  # danger reduction

        return float(r)