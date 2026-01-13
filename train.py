import numpy as np
import torch
import torch.optim as optim
from env3d import Snake3DEnv
from ppo_agent import PPOAgent
# from renderer import IsometricRenderer
from renderer3d import Renderer3DModernGL
from renderer3d_mglwindow import Snake3DRenderer  # Nouveau renderer 3D

# Hyperparameters
EPISODES = 1000
STEPS_PER_EPISODE = 200
GAMMA = 0.99
LR = 3e-4
EPS_CLIP = 0.2
UPDATE_EPOCHS = 4


def compute_returns(rewards, masks, gamma):
    R = 0
    returns = []
    for r, m in zip(reversed(rewards), reversed(masks)):
        R = r + gamma * R * m
        returns.insert(0, R)
    return returns


def main():
    env = Snake3DEnv()
    obs_dim = np.prod(env.grid_size)
    action_dim = 6
    agent = PPOAgent(obs_dim, action_dim)
    optimizer = optim.Adam(agent.parameters(), lr=LR)
    renderer = Renderer3DModernGL(env.grid_size)  # Utilisation du renderer moderngl

    for episode in range(EPISODES):
        obs = env.reset()
        log_probs = []
        values = []
        rewards = []
        masks = []
        entropies = []
        states = []
        actions = []
        for step in range(STEPS_PER_EPISODE):
            action, log_prob, entropy = agent.act(obs)
            next_obs, reward, done, _ = env.step(action)
            states.append(torch.tensor(obs, dtype=torch.float32))
            actions.append(torch.tensor(action))
            log_probs.append(log_prob)
            entropies.append(entropy)
            rewards.append(reward)
            masks.append(1 - float(done))
            values.append(agent.critic(torch.tensor(obs, dtype=torch.float32).unsqueeze(0)))
            obs = next_obs
            renderer.draw(env.snake, env.target, env.obstacles)
            if done:
                break
        returns = compute_returns(rewards, masks, GAMMA)
        returns = torch.tensor(returns, dtype=torch.float32)
        log_probs = torch.stack(log_probs)
        values = torch.cat(values).squeeze(-1)
        advantage = returns - values.detach()
        for _ in range(UPDATE_EPOCHS):
            new_log_probs, entropy, new_values = agent.evaluate(torch.stack(states), torch.stack(actions))
            ratio = (new_log_probs - log_probs.detach()).exp()
            surr1 = ratio * advantage
            surr2 = torch.clamp(ratio, 1-EPS_CLIP, 1+EPS_CLIP) * advantage
            actor_loss = -torch.min(surr1, surr2).mean()
            critic_loss = (returns - new_values.squeeze(-1)).pow(2).mean()
            loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy.mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f"Episode {episode}, score: {sum(rewards):.2f}")

if __name__ == "__main__":
    main()

# Remplacer l'appel du renderer par un appel à moderngl-window si besoin
# Pour l'entraînement, tu peux garder le renderer 2D, mais pour la visualisation 3D, lance :
# python renderer3d_mglwindow.py
