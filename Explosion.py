import pygame

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.images = [pygame.image.load(f"Data/explosions/explosion{i}.png") for i in range(1, 6)]  # Load explosion frames
        self.images = [pygame.transform.scale(img, (200, 200)) for img in self.images]  # Scale images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0  # Timer to control frame rate

    def update(self):
        self.timer += 1
        if self.timer % 5 == 0:  # Change frame every 5 ticks
            self.index += 1
            if self.index < len(self.images):
                self.image = self.images[self.index]
            else:
                self.kill()  # Remove the explosion sprite when animation ends