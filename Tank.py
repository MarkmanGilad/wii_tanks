import pygame
from Constants import *
import math
from Bullet import Bullet


class Tank(pygame.sprite.Sprite):
    def __init__(self, pos, angle, image, Bullet_group) -> None:
        super().__init__()
        self.image = image
        self.image = pygame.transform.scale(self.image, (175,175))
        self.rect = self.image.get_rect(midbottom = pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.Bullet_group = Bullet_group
        self.speed = TANK_SPEED
        self.angle = angle


        # random enemy tank attributes
        self.current_action = 0 
        self.action_timer = 0
        self.shooting = False
        self.shots_remaining = 0
        self.shoot_timer = 0
        

    def update(self) -> None:
        pass

    def rotate_left(self):
        self.angle += 5
    
    def rotate_right(self):
        self.angle -= 5
    
    def move_forward (self):
        speed_x = self.speed * math.cos(self.angle * (math.pi/180))
        speed_y = self.speed * -math.sin(self.angle * (math.pi/180))
        self.rect.y += speed_y
        self.rect.x += speed_x
        if(self.rect.bottom >= HEIGHT):
            self.rect.bottom = HEIGHT
        if(self.rect.top <= 0):
            self.rect.top = 0
        if(self.rect.right >= WIDTH):
            self.rect.right = WIDTH
        if(self.rect.left <= 0):
            self.rect.left = 0
        
    
    def move_back (self):
        speed_x = self.speed * math.cos(self.angle * (math.pi/180))
        speed_y = self.speed * -math.sin(self.angle * (math.pi/180))
        if(self.rect.bottom >= HEIGHT):
            self.rect.bottom = HEIGHT
        if(self.rect.top <= 0):
            self.rect.top = 0
        if(self.rect.right >= WIDTH):
            self.rect.right = WIDTH
        if(self.rect.left <= 0):
            self.rect.left = 0
        self.rect.x -= speed_x
        self.rect.y -= speed_y

    def shoot(self):
        barrel_length = self.rect.width // 2 
        x = self.rect.centerx + barrel_length * math.cos(math.radians(self.angle))
        y = self.rect.centery - barrel_length * math.sin(math.radians(self.angle))
        if (len(self.Bullet_group) < MAX_AMMUNITION):
            self.Bullet_group.append(Bullet((x, y), self.angle))
        else:
            pass

    def shoot_random(self):
        if not self.shooting:  # Start shooting sequence
            self.shooting = True
            self.shots_remaining = 3  # Number of bullets to shoot
            self.shoot_timer = 30  # Half a second delay (30 frames at 60 FPS)
        if self.shooting and self.shoot_timer <= 0 and self.shots_remaining > 0:
            # Fire a bullet
            barrel_length = self.rect.width // 2
            x = self.rect.centerx + barrel_length * math.cos(math.radians(self.angle))
            y = self.rect.centery - barrel_length * math.sin(math.radians(self.angle))
            self.Bullet_group.append(Bullet((x, y), self.angle))
            # Decrease the number of remaining shots
            self.shots_remaining -= 1
            # Reset the timer for the next shot
            self.shoot_timer = 30
        elif self.shooting:
            self.shoot_timer -= 1
        if self.shots_remaining <= 0:
            self.shooting = False

    def action(self,action):
        if action[0] == 1:
            self.move_forward()
        if action[1] == 1:
            self.move_back()
        if action[2] == 1:
            self.rotate_left()
        if action[3] == 1:
            self.rotate_right()
        if action[4] == 1:
            self.shoot()
            # if isRandom:
            #     self.shoot_random()
            # else:
            #     self.shoot()
            

        

    def draw(self, surface):
        image_rotated = pygame.transform.rotozoom(self.image, self.angle, 1.0)
        rect_rotated = image_rotated.get_rect(center=self.rect.center)
        surface.blit(image_rotated,rect_rotated)

