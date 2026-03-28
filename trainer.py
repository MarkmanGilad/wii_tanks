import os
import pygame
import torch
from Constants import *
from Enviorment import Enviroment
from Human_Agent import Human_Agent
from Dqn_Agent import DQN_Agent
from Random_Agent import Random_Agent
from ReplayBuffer import ReplayBuffer
from Advanced_Random_Agent import Advanced_Random_Agent
import wandb

def main():
    num = 2
    env = Enviroment()
    env.init_screen()
    buffer = ReplayBuffer(path=None)
    
    player1 = DQN_Agent(device=torch.device('cpu'))
    player1_hat = DQN_Agent(device=torch.device('cpu'))
    # player2 = Human_Agent()
    player2 = Random_Agent()
    player2 = Advanced_Random_Agent(0.5)

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
    learning_rate = 0.0001
    start_epoch = 0
    C, tau = 3, 0.001
    loss = torch.tensor(0)
    avg = 0
    scores, losses, avg_score = [], [], []
    optim = torch.optim.Adam(player1.DQN.parameters(), lr=learning_rate)
    # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optim,[5000*1000, 10000*1000, 15000*1000, 20000*1000, 25000*1000, 30000*1000], gamma=0.5)
    step = 0

    win_count = 0
    win_rate_window = []   # 1=win, 0=lose for last 100 episodes
    steps_to_win_list = []
    steps_to_lose_list = []

    project = "TankAI"
    wandb.init(
        # set the wandb project where this run will be logged
        project=project,
        name=f'{project}_{num}',
        id=f'{project}_{num}',
        # track hyperparameters and run metadata
        config={
        "learning_rate": learning_rate,
        "Schedule": f'{str(scheduler.milestones)} gamma={str(scheduler.gamma)}',
        "epochs": epochs,
        "start_epoch": start_epoch,
        "decay": epsiln_decay,
        "gamma": gamma,
        "batch_size": batch_size, 
        "C": C,
        "Model":str(player1.DQN),
        "REWARD_WIN": REWARD_WIN,
        "REWARD_LOSE": REWARD_LOSE,
        "STEP_PENALTY": STEP_PENALTY,
        "K_AIM": K_AIM,
        "AIM_BONUS_NEAR": AIM_BONUS_NEAR,
        "AIM_THRESH_NEAR": AIM_THRESH_NEAR,
        "AIM_BONUS_LOCK": AIM_BONUS_LOCK,
        "AIM_THRESH_LOCK": AIM_THRESH_LOCK,
        "SHOOT_PENALTY": SHOOT_PENALTY,
        "SHOOT_BONUS_AIMED": SHOOT_BONUS_AIMED,
        "K_DANGER": K_DANGER,
        })
    
    
    for epoch in range(epochs):
        print(epoch, end='\r')
        env.reset()
        episode_reward = 0.0
        episode_loss = 0.0
        loss_steps = 0
        step = 0
        while True:
            print(step, end='\r')
            step += 1
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return
                    
            state = env.state()
            action1 = player1.get_Action(events=events, state = state, epoch=epoch)
            action2 = player2.get_Action(events=events, state = env.state(), epoch=epoch)

            env.move(action1, action2)
            env.render()
            next = env.state()
            done = env.end_of_game()
            reward = env.reward(state, action1, next, done)
            episode_reward += reward
            buffer.push(state, action1, reward, next, done)


            if done != 0:
                # Episode finished: record metrics and optionally checkpoint
                avg_loss = (episode_loss / loss_steps) if loss_steps > 0 else 0.0
                scores.append(episode_reward)
                losses.append(avg_loss)
                if done == 1:
                    win_count += 1
                    steps_to_win_list.append(step)
                    win_rate_window.append(1)
                else:
                    steps_to_lose_list.append(step)
                    win_rate_window.append(0)
                if len(win_rate_window) > 100:
                    win_rate_window.pop(0)
                win_rate = sum(win_rate_window) / len(win_rate_window)
                print(f"Epoch {epoch} step {step} Reward {episode_reward:.3f}  AvgLoss {avg_loss:.4f}  Wins {win_count}  WinRate {win_rate:.2f}")
                wandb.log({
                    "episode_reward": episode_reward,
                    "avg_loss": avg_loss,
                    "win_rate_100": win_rate,
                    "steps_this_episode": step,
                    "steps_to_win": steps_to_win_list[-1] if done == 1 else None,
                    "steps_to_lose": steps_to_lose_list[-1] if done == 2 else None,
                })
                if epoch % 100 == 0:
                    os.makedirs('checkpoints', exist_ok=True)
                    player1.save_param(f'checkpoints/dqn_epoch_{epoch}.pth')
                # Restart the game immediately
                break

            state = next

            if len(buffer) < MIN_BUFFER:
                continue

            states, actions, rewards, next_states, dones = buffer.sample(batch_size)
            actions_index = player1.actions_to_indices(actions)
            Q_values = player1.Q(states, actions_index)
            next_action, Q_hat_values = player1_hat.get_Actions_Values(next_states)

            loss = player1.DQN.loss(Q_values, rewards, Q_hat_values, dones)
            loss.backward()
            optim.step()
            optim.zero_grad()
            scheduler.step()
            try:
                lv = float(loss.item())
            except Exception:
                lv = 0.0
            episode_loss += lv
            loss_steps += 1

            if epoch % C == 0:
                # player1_hat.DQN.load_state_dict(player1.DQN.state_dict())
                player1_hat.fix_update(dqn=player1.DQN)
                # player1_hat.soft_update(dqn=player1.DQN, tau=tau)
            
            pygame.display.update()
            clock.tick(FPS)
            

    
if __name__ == "__main__":
    main()