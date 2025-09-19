# game.py (оновлений з новою системою ШІ)
import pygame
import os
from src.constants import *
from src.map_loader import MapLoader
from src.pacman import Pacman
from src.ghost import Ghost
from src.ui import UI
from src.difficulty import DifficultyManager


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        self.total_time = 0.0

        self.map_width = 0
        self.map_height = 0

        # Ініціалізуємо менеджер складності
        self.difficulty_manager = DifficultyManager()
        self.ghost_ais = []

        # Завантажуємо карту
        self.map_loader = MapLoader()
        self.load_map(MAP)  # базова карта

        self.state = GAME_PLAYING
        self.ui = UI(screen, self.font, self.big_font)

    def load_map(self, map_name):
        """Завантажує карту з файлу"""
        map_data = self.map_loader.load_map(map_name)
        self.walls = map_data['walls']
        self.map_width = max(x for x, y in self.walls) + 1
        self.map_height = max(y for x, y in self.walls) + 1
        self.dots = map_data['dots'].copy()  # копіюємо для подальшого видалення
        self.total_dots = len(self.dots)

        # Створюємо пакмена
        pacman_pos = map_data['pacman_start']
        self.pacman = Pacman(pacman_pos[0], pacman_pos[1], self)

        # Створюємо привидів
        self.ghosts = []
        colors = [RED, BLUE, PINK, ORANGE]
        for i, ghost_pos in enumerate(map_data['ghost_starts']):
            color = colors[i % len(colors)]
            ghost = Ghost(ghost_pos[0], ghost_pos[1], color, self)
            self.ghosts.append(ghost)

        # Створюємо ШІ для привидів відповідно до поточного рівня складності
        self.setup_ghost_ai()

    def setup_ghost_ai(self):
        """Налаштовує ШІ для привидів відповідно до поточного рівня складності"""
        self.ghost_ais = self.difficulty_manager.create_ghost_ais(self.ghosts, self)

        # Встановлюємо ШІ для кожного привида
        for i, ghost in enumerate(self.ghosts):
            if i < len(self.ghost_ais):
                ghost.set_ai(self.ghost_ais[i])
                print(f"Ghost {i+1} AI rules: {[rule.__class__.__name__ for rule in self.ghost_ais[i].rules]}")

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
                # Керування рівнем складності під час гри
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    if self.difficulty_manager.next_level():
                        self.setup_ghost_ai()
                        print(f"Difficulty increased to: {self.difficulty_manager.get_current_level().name}")
                elif event.key == pygame.K_MINUS:
                    if self.difficulty_manager.prev_level():
                        self.setup_ghost_ai()
                        print(f"Difficulty decreased to: {self.difficulty_manager.get_current_level().name}")

            elif self.state == GAME_PAUSED:
                if event.key == pygame.K_ESCAPE:
                    self.state = GAME_PLAYING
                elif event.key == pygame.K_r:
                    self.restart_game()
                # Керування рівнем складності в паузі
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    if self.difficulty_manager.next_level():
                        self.setup_ghost_ai()
                        print(f"Difficulty increased to: {self.difficulty_manager.get_current_level().name}")
                elif event.key == pygame.K_MINUS:
                    if self.difficulty_manager.prev_level():
                        self.setup_ghost_ai()
                        print(f"Difficulty decreased to: {self.difficulty_manager.get_current_level().name}")
                # Цифрові клавіші для прямого вибору рівня
                elif pygame.K_1 <= event.key <= pygame.K_4:
                    level_index = event.key - pygame.K_1
                    if self.difficulty_manager.set_level(level_index):
                        self.setup_ghost_ai()
                        print(f"Difficulty set to: {self.difficulty_manager.get_current_level().name}")

            elif self.state in [GAME_WON, GAME_LOST]:
                if event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                # Керування рівнем складності після завершення гри
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    if self.difficulty_manager.next_level():
                        self.setup_ghost_ai()
                        print(f"Difficulty increased to: {self.difficulty_manager.get_current_level().name}")
                elif event.key == pygame.K_MINUS:
                    if self.difficulty_manager.prev_level():
                        self.setup_ghost_ai()
                        print(f"Difficulty decreased to: {self.difficulty_manager.get_current_level().name}")

    def restart_game(self):
        """Перезапускає гру"""
        print(f"Restarting game on difficulty: {self.difficulty_manager.get_current_level().name}")
        self.load_map(MAP)
        self.state = GAME_PLAYING

    def update(self, dt):
        if self.state != GAME_PLAYING:
            return

        # Зберігаємо dt для використання в ШІ
        self.dt = dt

        self.total_time += dt

        self.pacman.update(dt, self.walls)

        # Перевіряємо збір точок на основі поточної позиції пекмена
        pacman_grid_pos = (int(self.pacman.grid_x), int(self.pacman.grid_y))
        if pacman_grid_pos in self.dots:
            self.dots.remove(pacman_grid_pos)

        if len(self.dots) == 0:
            self.state = GAME_WON
            return

        # Оновлюємо привидів
        for ghost in self.ghosts:
            ghost.update(dt, self.walls, self.pacman, self.ghosts)
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
        self.ui.draw_difficulty_info(self.difficulty_manager)

        if self.state == GAME_PAUSED:
            self.ui.draw_pause_screen(self.difficulty_manager)
        elif self.state == GAME_WON:
            self.ui.draw_win_screen()
        elif self.state == GAME_LOST:
            self.ui.draw_lose_screen()

    def get_ghost_debug_info(self):
        """Повертає інформацію про поточні дії привидів для дебагу"""
        debug_info = []
        for i, ghost in enumerate(self.ghosts):
            if hasattr(ghost, 'ai') and ghost.ai:
                active_rules = []
                if hasattr(ghost.ai, 'rules'):
                    for rule in ghost.ai.rules:
                        if rule.enabled:
                            direction, strength = rule.evaluate(ghost.ai, self.walls, self.pacman, self.ghosts)
                            if direction and strength > 0:
                                active_rules.append(f"{rule.__class__.__name__}({strength:.1f})")
                debug_info.append(f"Ghost {i+1}: {', '.join(active_rules) if active_rules else 'No active rules'}")
            else:
                debug_info.append(f"Ghost {i+1}: No AI")
        return debug_info