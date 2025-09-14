import pygame
import random
import math
from src.constants import *


class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.direction = random.choice(DIRECTIONS)
        self.speed = GHOST_SPEED
        self.size = CELL_SIZE - 4

        # Для анімації
        self.animation_timer = 0

    def get_valid_directions(self, walls):
        """Повертає список доступних напрямків руху"""
        valid_directions = []

        for direction in DIRECTIONS:
            test_x = self.x + direction[0] * self.speed * 0.1  # маленький крок для перевірки
            test_y = self.y + direction[1] * self.speed * 0.1

            if self.can_move(test_x, test_y, walls):
                valid_directions.append(direction)

        return valid_directions

    def can_move(self, x, y, walls):
        """Перевіряє чи може привид рухатися в дану позицію"""
        half_size = self.size // 2

        left = int((x - half_size) // CELL_SIZE)
        right = int((x + half_size) // CELL_SIZE)
        top = int((y - half_size) // CELL_SIZE)
        bottom = int((y + half_size) // CELL_SIZE)

        corners = [(left, top), (right, top), (left, bottom), (right, bottom)]
        for corner in corners:
            if corner in walls:
                return False
        return True

    def simple_ai_move(self, walls, pacman):
        """Проста ШІ для привida - поки просто випадковий рух"""
        valid_directions = self.get_valid_directions(walls)

        if not valid_directions:
            return  # Якщо немає доступних напрямків

        # Якщо поточний напрямок більше недоступний, обираємо новий
        if self.direction not in valid_directions:
            self.direction = random.choice(valid_directions)
        else:
            # Іноді змінюємо напрямок випадково (5% шансу)
            if random.random() < 0.05:
                self.direction = random.choice(valid_directions)

    def update(self, dt, walls, pacman):
        """Оновлює позицію привида"""
        # ШІ привида
        self.simple_ai_move(walls, pacman)

        # Рухаємося
        new_x = self.x + self.direction[0] * self.speed * dt
        new_y = self.y + self.direction[1] * self.speed * dt

        if self.can_move(new_x, new_y, walls):
            self.x = new_x
            self.y = new_y
        else:
            # Якщо не можемо рухатися, обираємо новий напрямок
            valid_directions = self.get_valid_directions(walls)
            if valid_directions:
                self.direction = random.choice(valid_directions)

        # Оновлюємо анімацію
        self.animation_timer += dt

    def check_collision(self, pacman):
        """Перевіряє зіткнення з пакменом"""
        distance = math.sqrt((self.x - pacman.x) ** 2 + (self.y - pacman.y) ** 2)
        return distance < (self.size // 2 + pacman.radius)

    def draw(self, screen):
        """Малює привида"""
        center = (int(self.x), int(self.y))
        half_size = self.size // 2

        # Малюємо тіло привида (прямокутник з округленим верхом)
        body_rect = pygame.Rect(center[0] - half_size, center[1] - half_size,
                                self.size, self.size)
        pygame.draw.rect(screen, self.color, body_rect)

        # Малюємо округлений верх
        pygame.draw.circle(screen, self.color,
                           (center[0], center[1] - half_size + half_size // 2),
                           half_size)

        # Малюємо хвилястий низ (спрощено - трикутники)
        bottom_y = center[1] + half_size
        wave_width = self.size // 4

        for i in range(4):
            x1 = center[0] - half_size + i * wave_width
            x2 = x1 + wave_width
            x_mid = (x1 + x2) // 2

            # Анімація хвиль
            wave_offset = int(3 * math.sin(self.animation_timer * 5 + i))

            points = [(x1, bottom_y), (x_mid, bottom_y - wave_width // 2 + wave_offset),
                      (x2, bottom_y)]
            pygame.draw.polygon(screen, self.color, points)

        # Малюємо очі
        eye_size = 3
        eye_y = center[1] - half_size // 2

        left_eye = (center[0] - half_size // 2, eye_y)
        right_eye = (center[0] + half_size // 2, eye_y)

        pygame.draw.circle(screen, WHITE, left_eye, eye_size)
        pygame.draw.circle(screen, WHITE, right_eye, eye_size)
        pygame.draw.circle(screen, BLACK, left_eye, eye_size // 2)
        pygame.draw.circle(screen, BLACK, right_eye, eye_size // 2)