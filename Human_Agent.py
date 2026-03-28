import pygame
import numpy as np

class Human_Agent:
    '''
        1 - forward
        3 - forward + left
        9 - forward + right
        2 - left
        4 - backward
        6 - backward + left
        8 - right
        12 - backward + right
        16 - shoot
        0 - no action
        '''

    def __init__(self):
        self.action = [0]* 5  # [move_forward, move_back, rotate_left, rotate_right, shoot]
        self.shoot = False
            
    def get_Action(self, events, state, epoch = None):
            if self.action[4] == 1:
                self.action[4] = 0
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.action[0] = 1
                    if event.key == pygame.K_s:
                        self.action[1] = 1
                    if event.key == pygame.K_a:
                        self.action[2] = 1
                    if event.key == pygame.K_d:
                        self.action[3] = 1
                    if event.key == pygame.K_SPACE:
                        self.action[4] = 1
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        self.action[0] = 0
                    if event.key == pygame.K_s:
                        self.action[1] = 0
                    if event.key == pygame.K_a:
                        self.action[2] = 0
                    if event.key == pygame.K_d:
                        self.action[3] = 0
            return self.action
            
        
