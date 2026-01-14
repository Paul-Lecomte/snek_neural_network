import pygame
import numpy as np

class IsometricRenderer:
    def __init__(self, grid_size=(10,10,10), cell_size=32):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.width = 800
        self.height = 600
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

    def iso_coords(self, x, y, z):
        # Simple isometric projection
        cx, cy = self.width//2, self.height//2
        iso_x = cx + (x - y) * self.cell_size // 2
        iso_y = cy + (x + y) * self.cell_size // 4 - z * self.cell_size // 2
        return iso_x, iso_y

    def draw(self, snake, target, obstacles):
        self.screen.fill((30,30,30))
        # Draw obstacles
        for o in obstacles:
            ox, oy = self.iso_coords(*o)
            pygame.draw.rect(self.screen, (100,100,100), (ox, oy, self.cell_size//2, self.cell_size//2))
        # Draw target
        tx, ty = self.iso_coords(*target)
        pygame.draw.rect(self.screen, (255,0,0), (tx, ty, self.cell_size//2, self.cell_size//2))
        # Draw snake
        for i, s in enumerate(snake):
            sx, sy = self.iso_coords(*s)
            color = (0,255,0) if i == 0 else (0,200,0)
            pygame.draw.rect(self.screen, color, (sx, sy, self.cell_size//2, self.cell_size//2))
        pygame.display.flip()
        self.clock.tick(15)

