import numpy as np
import random

class Snake3DEnv:
    def __init__(self, grid_size=(10, 10, 10)):
        self.grid_size = grid_size
        self.reset()

    def reset(self):
        self.snake = [(self.grid_size[0]//2, self.grid_size[1]//2, self.grid_size[2]//2)]
        self.direction = (1, 0, 0)
        self.spawn_target()
        self.spawn_obstacles()
        self.steps = 0
        self.stuck_steps = 0
        self.done = False
        return self.get_observation()

    def spawn_target(self):
        while True:
            self.target = tuple(np.random.randint(0, s) for s in self.grid_size)
            if self.target not in self.snake:
                break

    def spawn_obstacles(self, n=5):
        self.obstacles = set()
        while len(self.obstacles) < n:
            pos = tuple(np.random.randint(0, s) for s in self.grid_size)
            if pos not in self.snake and pos != self.target:
                self.obstacles.add(pos)

    def step(self, action):
        # action: 0=+x, 1=-x, 2=+y, 3=-y, 4=+z, 5=-z
        directions = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]
        self.direction = directions[action]
        new_head = tuple(np.add(self.snake[0], self.direction))
        self.steps += 1
        reward = -0.01
        if (min(new_head) < 0 or
            new_head[0] >= self.grid_size[0] or
            new_head[1] >= self.grid_size[1] or
            new_head[2] >= self.grid_size[2] or
            new_head in self.snake or
            new_head in self.obstacles):
            self.done = True
            reward = -1.0
        elif new_head == self.target:
            self.snake.insert(0, new_head)
            reward = 1.0
            self.spawn_target()
            self.spawn_obstacles()
            self.stuck_steps = 0
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()
            if len(self.snake) > 1 and self.snake[0] == self.snake[1]:
                self.stuck_steps += 1
            else:
                self.stuck_steps = 0
            if self.stuck_steps > 20:
                self.done = True
                reward = -0.5
        return self.get_observation(), reward, self.done, {}

    def get_observation(self):
        # Flattened grid with snake, target, obstacles
        obs = np.zeros(self.grid_size, dtype=np.float32)
        for x, y, z in self.snake:
            obs[x, y, z] = 0.5
        obs[self.target] = 1.0
        for o in self.obstacles:
            obs[o] = -1.0
        return obs.flatten()
