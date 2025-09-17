import pygame
import random
import math
from src.constants import *


class Ghost:
    def __init__(self, x, y, color, game):
        self.grid_x = x // CELL_SIZE
        self.grid_y = y // CELL_SIZE
        self.target_x = self.grid_x
        self.target_y = self.grid_y
        self.x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
        self.y = self.grid_y * CELL_SIZE + CELL_SIZE // 2
        self.color = color
        self.direction = random.choice(DIRECTIONS)
        self.move_progress = 0.0  # 0.0 - 1.0, прогрес руху до наступної клітинки
        self.move_speed = 4.0  # швидкість анімації (клітинок в секунду)
        self.size = CELL_SIZE - 4
        self.animation_timer = 0
        self.game = game

    def get_valid_directions(self, walls, ghosts):
        valid_directions = []
        for direction in DIRECTIONS:
            next_x = self.grid_x + direction[0]
            next_y = self.grid_y + direction[1]

            # Дозволяємо рух через тунелі
            next_x = (next_x + self.game.map_width) % self.game.map_width
            next_y = (next_y + self.game.map_height) % self.game.map_height

            # Перевірка на стіни та інших привидів
            if (next_x, next_y) not in walls:
                ghost_collision = False
                for ghost in ghosts:
                    if ghost != self and ghost.grid_x == next_x and ghost.grid_y == next_y:
                        ghost_collision = True
                        break
                if not ghost_collision:
                    valid_directions.append(direction)

        return valid_directions

    def update(self, dt, walls, pacman, ghosts):
        # Оновлення анімації
        self.animation_timer += dt

        # Якщо ми досягли цільової клітинки
        if self.grid_x == self.target_x and self.grid_y == self.target_y:
            valid_directions = self.get_valid_directions(walls, ghosts)

            if not valid_directions:
                self.direction = (0, 0)
                return

            # Зміна напрямку тільки при зіткненні
            if self.direction not in valid_directions:
                self.direction = random.choice(valid_directions)

            # Рух у поточному напрямку
            if self.direction in valid_directions:
                self.target_x = self.grid_x + self.direction[0]
                self.target_y = self.grid_y + self.direction[1]

                # Обробка тунелів
                self.target_x = (self.target_x + self.game.map_width) % self.game.map_width
                self.target_y = (self.target_y + self.game.map_height) % self.game.map_height

                self.move_progress = 0.0

        # Якщо рухаємося до цільової клітинки
        if self.grid_x != self.target_x or self.grid_y != self.target_y:
            self.move_progress += dt * self.move_speed

            if self.move_progress >= 1.0:
                # Досягли цільової клітинки
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.move_progress = 0.0
            else:
                # Інтерполюємо позицію
                self.x = (self.grid_x + (self.target_x - self.grid_x) * self.move_progress) * CELL_SIZE + CELL_SIZE // 2
                self.y = (self.grid_y + (self.target_y - self.grid_y) * self.move_progress) * CELL_SIZE + CELL_SIZE // 2

    def check_collision(self, pacman):
        # Перевіряємо зіткнення з пекменом на основі їхніх поточних позицій
        distance = math.sqrt((self.x - pacman.x) ** 2 + (self.y - pacman.y) ** 2)
        return self.grid_x == pacman.grid_x and self.grid_y == pacman.grid_y

    def draw(self, screen):
        center = (int(self.x), int(self.y))
        half_size = self.size // 2

        body_rect = pygame.Rect(center[0] - half_size, center[1] - half_size,
                                self.size, self.size)
        pygame.draw.rect(screen, self.color, body_rect)

        pygame.draw.circle(screen, self.color,
                           (center[0], center[1] - half_size + half_size // 2),
                           half_size)

        bottom_y = center[1] + half_size
        wave_width = self.size // 4

        for i in range(4):
            x1 = center[0] - half_size + i * wave_width
            x2 = x1 + wave_width
            x_mid = (x1 + x2) // 2
            wave_offset = int(3 * math.sin(self.animation_timer * 5 + i))
            points = [(x1, bottom_y), (x_mid, bottom_y - wave_width // 2 + wave_offset),
                      (x2, bottom_y)]
            pygame.draw.polygon(screen, self.color, points)

        eye_size = 3
        eye_y = center[1] - half_size // 2
        left_eye = (center[0] - half_size // 2, eye_y)
        right_eye = (center[0] + half_size // 2, eye_y)

        pygame.draw.circle(screen, WHITE, left_eye, eye_size)
        pygame.draw.circle(screen, WHITE, right_eye, eye_size)
        pygame.draw.circle(screen, BLACK, left_eye, eye_size // 2)
        pygame.draw.circle(screen, BLACK, right_eye, eye_size // 2)