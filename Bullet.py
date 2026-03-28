import pygame
from Constants import *
import math

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle) -> None:
        super().__init__()
        self.image = pygame.image.load(BULLET_URL)
        self.image = pygame.transform.scale(self.image, (30,30))
        self.rect = self.image.get_rect(midbottom = pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = angle
        self.speed = BULLET_SPEED
        self.vx = self.speed * math.cos(self.angle * (math.pi/180))
        self.vy = self.speed * -math.sin(self.angle * (math.pi/180))
        
    def move(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        

    def update(self) -> None:
        self.move()

    def draw(self, surface):
        image_rotated = pygame.transform.rotozoom(self.image, self.angle + 180, 1.0)
        rect_rotated = image_rotated.get_rect(center=self.rect.center)
        surface.blit(image_rotated,rect_rotated)
        