import pygame
import torch
from Constants import *
from Enviorment import Enviroment
from Human_Agent import Human_Agent
from Dqn_Agent import DQN_Agent
from Random_Agent import Random_Agent



def main():
    
    env = Enviroment()
    env.init_screen()

    player1 = DQN_Agent(device=torch.device('cpu'))
    player2 = Human_Agent()
    # player2 = Random_Agent()
    

    pygame.init()

    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    backround = pygame.image.load("Data/wood.png")
    screen.blit(backround, (0,0))
    pygame.display.set_caption("TANKS!")

    clock = pygame.time.Clock()
    FPS = 60

    run = True
    eplosion_timer = 0
    game_ended = False
    result = 0

    while run:
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
        if not game_ended:
            action1 = player1.get_Action(events=events, state = env.state())
            action2 = player2.get_Action(events=events, state = env.state())
            
            env.move(action1, action2)
            

            env.render()

            result = env.end_of_game()
            if result != 0:
                game_ended = True
                eplosion_timer = pygame.time.get_ticks()
                # show_end_screen(result)  # Show the end screen
        else:
            env.render()
            if pygame.time.get_ticks() - eplosion_timer > 900:
                run = False
                show_end_screen(result)
        pygame.display.update()
        clock.tick(FPS)
        
def show_end_screen(result):
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT + 100))
    pygame.display.set_caption("Game Over")

    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))  # Position above the restart text

    winner_font = pygame.font.Font(None, 50)
    if result == 1:
        winner_text = winner_font.render("You Win!", True, (0, 255, 0))  # Green for win
    else:
        winner_text = winner_font.render("You Lose!", True, (255, 0, 0))  # Red for lose
    winner_text_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # Position below the game over text

    restart_font = pygame.font.Font(None, 50)
    restart_text = restart_font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
    restart_text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))  # Position below the game over text

    run = True
    while run:
        screen.fill((0, 0, 0))  # Black background
        screen.blit(text, text_rect)
        screen.blit(winner_text, winner_text_rect)
        screen.blit(restart_text, restart_text_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press 'R' to restart
                    main()  # Restart the game
                    return
                if event.key == pygame.K_q:  # Press 'Q' to quit
                    run = False
    
if __name__ == "__main__":
    main()