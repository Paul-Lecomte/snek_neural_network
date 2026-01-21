import sys
import math
import pygame
from pygame import Rect, Surface
from pygame.math import Vector2

class IsoCamera:
    def __init__(self, screen_size, cell_size=48, zoom=1.0):
        self.screen_w, self.screen_h = screen_size
        self.cell_size = float(cell_size)
        self.zoom = float(zoom)
        self.offset = Vector2(0, 0)
        self._dragging = False
        self._last_mouse = Vector2(0, 0)
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        self.zoom_speed = 1.18

    def world_to_screen(self, x, y, z=0):
        cx, cy = self.screen_w * 0.5, self.screen_h * 0.45
        s = self.cell_size * self.zoom
        iso_x = (x - y) * (s * 0.5)
        iso_y = (x + y) * (s * 0.25) - z * (s * 0.5)
        return Vector2(cx + iso_x, cy + iso_y) + self.offset

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2 or (event.button == 1 and pygame.key.get_mods() & pygame.KMOD_CTRL):
                self._dragging = True
                self._last_mouse = Vector2(event.pos)
            elif event.button == 4:  # wheel up
                self._zoom_at(event.pos, self.zoom * self.zoom_speed)
            elif event.button == 5:  # wheel down
                self._zoom_at(event.pos, self.zoom / self.zoom_speed)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 2):
                self._dragging = False
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            mp = Vector2(event.pos)
            delta = mp - self._last_mouse
            self.offset += delta
            self._last_mouse = mp
        elif event.type == pygame.VIDEORESIZE:
            self.screen_w, self.screen_h = event.w, event.h

    def _zoom_at(self, mouse_pos, new_zoom):
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        if abs(new_zoom - self.zoom) < 1e-6:
            return
        mouse = Vector2(mouse_pos)
        center = Vector2(self.screen_w*0.5, self.screen_h*0.45)
        before = (mouse - self.offset - center) / self.zoom
        self.zoom = new_zoom
        after = before * self.zoom
        self.offset += (mouse - center) - after

    def set_center(self, wx, wy, wz=0):
        screen_pos = self.world_to_screen(wx, wy, wz)
        center = Vector2(self.screen_w*0.5, self.screen_h*0.45)
        self.offset += center - screen_pos


class IsometricRenderer:
    """Rendu isométrique 2D amélioré pour le jeu Snake.

    Méthodes:
    - draw(snake, target, obstacles)
    - handle_events() pour integrer à la boucle principale
    - run_demo() pour lancer une démo autonome
    """

    def __init__(self, grid_size=(12, 12, 4), cell_size=48, width=1200, height=800):
        pygame.init()
        pygame.display.set_caption("Isometric Snake Renderer")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 14)
        self.grid_size = tuple(grid_size)
        self.cell_size = cell_size
        self.camera = IsoCamera((self.width, self.height), cell_size=self.cell_size, zoom=1.0)

        # Colors
        self.bg_color = (30, 30, 34)
        self.tile_color = (75, 80, 90)
        self.tile_edge = (40, 45, 50)
        self.obstacle_color = (120, 80, 60)
        self.target_color = (200, 40, 40)
        self.snake_head = (100, 220, 100)
        self.snake_body = (40, 160, 40)

    def _tile_polygon(self, x, y, z=0):
        cx = self.camera.world_to_screen(x, y, z)
        s = self.cell_size * self.camera.zoom
        dx = s * 0.5
        dy = s * 0.25
        top = cx + Vector2(0, -dy)
        left = cx + Vector2(-dx, 0)
        right = cx + Vector2(dx, 0)
        bottom = cx + Vector2(0, dy)
        return [top, right, bottom, left]

    def _draw_tile(self, surf, x, y, z=0, color=None):
        poly = self._tile_polygon(x, y, z)
        col = color if color else self.tile_color
        # shadow slightly offset
        shadow = [(p.x, p.y + (self.cell_size * 0.12 * self.camera.zoom)) for p in poly]
        pygame.draw.polygon(surf, (6, 6, 6), shadow)
        pygame.draw.polygon(surf, col, [(p.x, p.y) for p in poly])
        pygame.draw.polygon(surf, self.tile_edge, [(p.x, p.y) for p in poly], 1)

    def _draw_entity(self, surf, pos, size=0.6, color=(255,255,255), outline=(0,0,0)):
        x, y, z = pos
        center = self.camera.world_to_screen(x, y, z + 0.5)
        s = self.cell_size * self.camera.zoom * size
        # shadow ellipse
        shadow_rect = Rect(0,0, s*0.9, s*0.38)
        shadow_rect.center = (center.x, center.y + s*0.6)
        pygame.draw.ellipse(surf, (0,0,0,100), shadow_rect)
        # main rectangle with slight rounded effect
        rect = Rect(0,0, s, s)
        rect.center = (center.x, center.y)
        surface = Surface((rect.w+4, rect.h+4), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (2,2, rect.w, rect.h), border_radius=6)
        pygame.draw.rect(surface, outline, (2,2, rect.w, rect.h), 2, border_radius=6)
        surf.blit(surface, rect.topleft)

    def draw(self, snake, target, obstacles):
        self.screen.fill(self.bg_color)
        width, height = self.screen.get_size()
        self.camera.screen_w, self.camera.screen_h = width, height

        items = []
        gx, gy, gz = self.grid_size
        # Draw grid tiles (only ground z=0 for efficiency)
        for x in range(gx):
            for y in range(gy):
                items.append(((x,y,0), lambda surf, p=(x,y,0): self._draw_tile(surf, *p)))

        # obstacles and target
        for o in obstacles:
            items.append((o, lambda surf, p=o: self._draw_tile(surf, *p, color=self.obstacle_color)))

        if target is not None:
            items.append((target, lambda surf, p=target: self._draw_tile(surf, *p, color=self.target_color)))

        # snake parts (draw tile underneath + entity)
        for i, s in enumerate(snake):
            color = self.snake_head if i == 0 else self.snake_body
            items.append((s, lambda surf, p=s, c=color, idx=i: (self._draw_tile(surf, *p), self._draw_entity(surf, p, size=0.8 if idx>0 else 1.0, color=c))))

        # Depth sort by x+y (isometric depth), then by z
        items.sort(key=lambda it: (it[0][0] + it[0][1], it[0][2]))

        for _, drawfn in items:
            # drawfn can return tuple; ignore
            drawfn(self.screen)

        # HUD
        fps = int(self.clock.get_fps())
        text = self.font.render(f"FPS: {fps}  Zoom: {self.camera.zoom:.2f}", True, (230,230,230))
        self.screen.blit(text, (8,8))

        pygame.display.flip()
        self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            self.camera.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    self.camera.offset = Vector2(0,0)
                    self.camera.zoom = 1.0
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    def run_demo(self):
        snake = [(5,5,0), (4,5,0), (3,5,0)]
        target = (8, 6, 0)
        obstacles = [(6,6,0), (2,3,0), (7,3,0)]
        t = 0.0
        while True:
            self.handle_events()
            # simple bob animation for head
            head = snake[0]
            animated_head = (head[0], head[1], 0 if int(t*2)%2==0 else 1)
            s2 = [animated_head] + snake[1:]
            self.draw(s2, target, obstacles)
            t += self.clock.get_time() / 1000.0


if __name__ == '__main__':
    renderer = IsometricRenderer(grid_size=(12,12,4), cell_size=48, width=1200, height=800)
    renderer.run_demo()
