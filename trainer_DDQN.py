import pygame
import torch
from Constants import *
from Enviorment import Environment
from Dqn_Agent import DQN_Agent
from ReplayBuffer import ReplayBuffer
import os
import wandb

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("TANKS")
    backround = pygame.image.load("Data/wood.png")
    screen.blit(backround, (0,0))