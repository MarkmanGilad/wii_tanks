import pygame
import numpy as np
import random
import math

class Random_Agent:


    def __init__(self):
        self.action = [0]* 5  # [move_forward, move_back, rotate_left, rotate_right, shoot]
        self.shoot = False
        self.action_timer = 0
        self.action_num = 0
        self.action_history = []  # Track which action was done when
            
    def get_Action(self, events = None, state = None, epoch = None):
        # If the timer has expired, generate a new random action
        self.action[4] = 0  # Reset shoot action
        if self.action_timer <= 0:
            turns = random.randint(0,2)
            movment = random.randint(0,2)
            if turns == 0:
                self.action[0] = 0
                self.action[1] = 0
            elif turns == 1:
                self.action[0] = 1
                self.action[1] = 0
            else:
                self.action[0] = 0
                self.action[1] = 1
            if movment == 0:
                self.action[2] = 0
                self.action[3] = 0
            elif movment == 1:
                self.action[2] = 1
                self.action[3] = 0
            else:
                self.action[2] = 0
                self.action[3] = 1
            
            if random.random() < 0.7:
                self.action[4] = 1
            
            
            
            self.action_timer = random.randint(20, 30)  # Hold the action for 20-50 frames
        else:
            self.action_timer -= 1  # Decrease the timer
        return self.action
        # action = [0]*9
        # action[random.randint(0,8)] = 1  
        # return  action
            
        
