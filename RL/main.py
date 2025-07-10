from collections import defaultdict
from tqdm import tqdm
import random
import math
import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from in_between_env import InBetweenEnv  # your gymnasium.Env
from deck import Deck

# Use your native Gymnasium env directly
env = InBetweenEnv(Deck)
env.reset()

N_EPISODES = 100_000

def train_q_agent(env, episodes: int = 400_000, alpha = 0.1, eps_start = 0.2, eps_end = 0.01, eps_decay = 2e5):
    Q = defaultdict(lambda: np.zeros(env.action_space.n, dtype = float))
    for ep in tqdm(range(episodes)):
        state, _ = env.reset()
        done = False
        while not done:
            eps = eps_end + (eps_start-eps_end) * math.exp(-ep / eps_decay)
            if random.random() < eps:
                action = env.action_space.sample()          # explore
            else:
                action = int(np.argmax(Q[state]))
            state, reward, done, _, _ = env.step(action)

            Q[state][action] += alpha * (reward - Q[state][action])
    return Q

## code credit to joshua
def print_q_table(Q):
    header = "gap\\pot | " + " ".join(f"{p:>3}" for p in range(13))
    line   = "-" * len(header)
    print(header)
    print(line)
    for gap in range(-1, 12):
        row = [f"{gap:>3}    |"]
        for pot_bucket in range(11):
            state = (gap, pot_bucket)
            if state in Q:
                best_a = int(np.argmax(Q[state]))
            else:
                best_a = -1               # unvisited state
            row.append(f"{best_a:>3}")
        print(" ".join(row))
    print(line)
    print("best_a meaning: 0=pass, 1=5 %, …, 20=100 %,  -1=never trained")

Q = train_q_agent(env, N_EPISODES, eps_start = 1)

print(Q.keys())

print_q_table(Q)