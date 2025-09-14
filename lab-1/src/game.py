import pygame
import os
from src.constants import *
from src.map_loader import MapLoader
from src.pacman import Pacman
from src.ghost import Ghost
from src.ui import UI


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        # Завантажуємо карту
        self.map_loader = MapLoader()
        self.load_map("map1.txt")  # базова карта

        self.state = GAME_PLAYING
        self.ui = UI(screen, self.font, self.big_font)

    def load_map(self, map_name):
        """Завантажує карту з файлу"""
        map_data = self.map_loader.load_map(map_name)
        self.walls = map_data['walls']
        self.dots = map_data['dots'].copy()  # копіюємо для подальшого видалення
        self.total_dots = len(self.dots)

        # Створюємо пакмена
        pacman_pos = map_data['pacman_start']
        self.pacman = Pacman(pacman_pos[0], pacman_pos[1])

        # Створюємо привидів
        self.ghosts = []
        for i, ghost_pos in enumerate(map_data['ghost_starts']):
            color = [RED, BLUE, PINK, ORANGE][i % 4]
            self.ghosts.append(Ghost(ghost_pos[0], ghost_pos[1], color))

    def handle_event(self, event):
        """Обробляє події"""
        if event.type == pygame.KEYDOWN:
            if self.state == GAME_PLAYING:
                if event.key == pygame.K_ESCAPE:
                    self.state = GAME_PAUSED
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.pacman.set_direction(UP)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.pacman.set_direction(DOWN)
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    self.pacman.set_direction(LEFT)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.pacman.set_direction(RIGHT)

            elif self.state == GAME_PAUSED:
                if event.key == pygame.K_ESCAPE:
                    self.state = GAME_PLAYING
                elif event.key == pygame.K_r:
                    self.restart_game()

            elif self.state in [GAME_WON, GAME_LOST]:
                if event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

    def restart_game(self):
        """Перезапускає гру"""
        self.load_map("map1.txt")
        self.state = GAME_PLAYING

    def update(self, dt):
        """Оновлює стан гри"""
        if self.state != GAME_PLAYING:
            return

        # Оновлюємо пакмена
        self.pacman.update(dt, self.walls)

        # Перевіряємо збір точок
        pacman_grid_pos = (int(self.pacman.x // CELL_SIZE), int(self.pacman.y // CELL_SIZE))
        if pacman_grid_pos in self.dots:
            self.dots.remove(pacman_grid_pos)

        # Перевіряємо перемогу
        if len(self.dots) == 0:
            self.state = GAME_WON
            return

        # Оновлюємо привидів
        for ghost in self.ghosts:
            ghost.update(dt, self.walls, self.pacman)

            # Перевіряємо зіткнення з пакменом
            if ghost.check_collision(self.pacman):
                self.state = GAME_LOST
                return

    def draw(self):
        """Відмальовує гру"""
        self.screen.fill(BLACK)

        # Малюємо стіни
        for wall_pos in self.walls:
            x, y = wall_pos[0] * CELL_SIZE, wall_pos[1] * CELL_SIZE
            pygame.draw.rect(self.screen, BLUE, (x, y, CELL_SIZE, CELL_SIZE))

        # Малюємо точки
        for dot_pos in self.dots:
            x, y = dot_pos[0] * CELL_SIZE + CELL_SIZE // 2, dot_pos[1] * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, WHITE, (x, y), 3)

        # Малюємо пакмена
        self.pacman.draw(self.screen)

        # Малюємо привидів
        for ghost in self.ghosts:
            ghost.draw(self.screen)

        # Малюємо UI
        self.ui.draw_score(len(self.dots), self.total_dots)

        if self.state == GAME_PAUSED:
            self.ui.draw_pause_screen()
        elif self.state == GAME_WON:
            self.ui.draw_win_screen()
        elif self.state == GAME_LOST:
            self.ui.draw_lose_screen()