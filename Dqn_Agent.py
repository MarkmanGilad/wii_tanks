import torch
import random
import math
from Dqn import DQN
from Constants import *

class DQN_Agent:
    def __init__(self, parametes_path = None, device = torch.device('cpu')):
        self.DQN = DQN(device=device)
        if parametes_path:
            self.DQN.load_params(parametes_path)
        
        self.actions = [[0,0,0,0,0],[0,1,0,0,0],[0,1,0,1,0],[0,1,0,1,1],
                        [0,1,1,0,0],[0,1,1,0,1],[1,0,0,0,0],[1,0,1,0,0],
                        [1,0,1,0,1],[1,0,0,1,0],[1,0,0,1,1],[0,0,1,0,0],
                        [0,0,0,1,0],[0,0,1,0,1],[0,0,0,1,1],[1,0,0,0,1],
                        [0,1,0,0,1],[0,0,0,0,1]]                       
        # make a tensor copy for fast batch operations
        self.actions_tensor = torch.tensor(self.actions, dtype=torch.int)


    def get_Action (self, state, epoch = 0, events= None, train = True) -> tuple:
        # Epsilon-greedy: choose random discrete action
        if train:
            epsilon = self.epsilon_greedy(epoch)
            rnd = random.random()
            if rnd < epsilon:
                chosen = random.choice(self.actions)
                return chosen

        with torch.no_grad():
            Q_values = self.DQN(state)
        max_index = int(torch.argmax(Q_values).item())
        chosen = self.actions[max_index]
        return chosen
    
    def action_to_index(self, action_tensor):
        """Single action index lookup (unmodified simple version)."""
        # convert tensor to list; otherwise assume it’s already a sequence
        action_list = action_tensor.detach().cpu().tolist()
        return self.actions.index(action_list)

    def actions_to_indices(self, actions_mat: torch.Tensor) -> torch.Tensor:
        actions_tensor = self.actions_tensor.to(actions_mat.device)
        # mask[N, num_actions]
        mask = (actions_mat.unsqueeze(1) == actions_tensor.unsqueeze(0)).all(dim=2)
        return torch.argmax(mask.to(torch.int64), dim=1)

    def get_Actions_Values (self, states):
        with torch.no_grad():
            Q_values = self.DQN(states)
            max_values, max_indices = torch.max(Q_values,dim=1) # best_values, best_actions
        return max_indices.reshape(-1,1), max_values.reshape(-1,1)
    
    def Q (self, states, actions):
        Q_values = self.DQN(states) # try: Q_values = self.DQN(states).gather(dim=1, actions) ; check if shape of actions is [-1, 1] otherwise dim=0
        rows = torch.arange(Q_values.shape[0]).reshape(-1,1)
        cols = actions.reshape(-1,1)
        return Q_values[rows, cols]
    
    def epsilon_greedy(self,epoch, start = epsilon_start, final=epsilon_final, decay=epsiln_decay):
        # res = final + (start - final) * math.exp(-1 * epoch/decay)
        if epoch < decay:
            return start - (start - final) * epoch/decay
        return final
    
    def loadModel (self, file):
        self.model = torch.load(file)
    
    def save_param (self, path):
        self.DQN.save_params(path)

    def load_params (self, path):
        self.DQN.load_params(path)

    def fix_update (self, dqn, tau=0.001):
        self.DQN.load_state_dict(dqn.state_dict())

    def __call__(self, events= None, state=None):
        return self.get_Action(state)