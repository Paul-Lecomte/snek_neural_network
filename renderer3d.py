import pygame
from pygame.locals import *

class Renderer3DModernGL:
    def __init__(self, grid_size=(10,10,10), cell_size=40):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.width = grid_size[0] * cell_size
        self.height = grid_size[1] * cell_size
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))  # SANS OPENGL
        self.clock = pygame.time.Clock()

    def draw(self, snake, target, obstacles):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys; sys.exit()
        # Fond bleu clair
        self.screen.fill((100, 150, 255))
        # Obstacles en gris
        for o in obstacles:
            pygame.draw.rect(self.screen, (100,100,100), (o[0]*self.cell_size, o[1]*self.cell_size, self.cell_size, self.cell_size))
        # Cible en rouge
        pygame.draw.rect(self.screen, (255,0,0), (target[0]*self.cell_size, target[1]*self.cell_size, self.cell_size, self.cell_size))
        # Serpent (tête en vert vif, corps en vert foncé)
        for i, s in enumerate(snake):
            color = (0,255,0) if i == 0 else (0,180,0)
            pygame.draw.rect(self.screen, color, (s[0]*self.cell_size, s[1]*self.cell_size, self.cell_size, self.cell_size))
        pygame.display.flip()
        self.clock.tick(30)
        print("[DEBUG] Affichage pygame 2D OK")
