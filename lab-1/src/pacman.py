import pygame
import math
from src.constants import *


class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.speed = PACMAN_SPEED
        self.radius = CELL_SIZE // 2 - 2

        # Для анімації пасти
        self.mouth_angle = 0
        self.mouth_opening = True

    def set_direction(self, direction):
        """Встановлює наступний напрямок руху"""
        self.next_direction = direction

    def can_move(self, x, y, walls):
        """Перевіряє чи може пакмен рухатися в дану позицію"""
        # Перевіряємо кути пакмена
        left = int((x - self.radius) // CELL_SIZE)
        right = int((x + self.radius) // CELL_SIZE)
        top = int((y - self.radius) // CELL_SIZE)
        bottom = int((y + self.radius) // CELL_SIZE)

        # Перевіряємо чи немає стін в усіх кутах
        corners = [(left, top), (right, top), (left, bottom), (right, bottom)]
        for corner in corners:
            if corner in walls:
                return False
        return True

    def is_at_grid_center(self):
        """Перевіряє чи пакмен знаходиться близько до центру клітинки сітки"""
        center_x = (self.x // CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2
        center_y = (self.y // CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2

        return abs(self.x - center_x) < 5 and abs(self.y - center_y) < 5

    def update(self, dt, walls):
        """Оновлює позицію пакмена"""
        # Спробуємо змінити напрямок якщо пакмен в центрі клітинки
        if self.is_at_grid_center() and self.next_direction != (0, 0):
            test_x = self.x + self.next_direction[0] * self.speed * dt
            test_y = self.y + self.next_direction[1] * self.speed * dt

            if self.can_move(test_x, test_y, walls):
                self.direction = self.next_direction
                self.next_direction = (0, 0)

        # Рухаємося в поточному напрямку
        if self.direction != (0, 0):
            new_x = self.x + self.direction[0] * self.speed * dt
            new_y = self.y + self.direction[1] * self.speed * dt

            if self.can_move(new_x, new_y, walls):
                self.x = new_x
                self.y = new_y
            else:
                # Зупиняємося якщо не можемо рухатися
                self.direction = (0, 0)

        # Оновлюємо анімацію пасти
        if self.direction != (0, 0):
            if self.mouth_opening:
                self.mouth_angle += 300 * dt  # швидкість анімації
                if self.mouth_angle >= 45:
                    self.mouth_angle = 45
                    self.mouth_opening = False
            else:
                self.mouth_angle -= 300 * dt
                if self.mouth_angle <= 0:
                    self.mouth_angle = 0
                    self.mouth_opening = True

    def draw(self, screen):
        """Малює пакмена"""
        center = (int(self.x), int(self.y))

        if self.direction == (0, 0):
            # Якщо не рухається - просто коло
            pygame.draw.circle(screen, YELLOW, center, self.radius)
        else:
            # Малюємо пакмена з пастою
            # Обчислюємо кут напрямку
            angle_offset = 0
            if self.direction == RIGHT:
                angle_offset = 0
            elif self.direction == UP:
                angle_offset = 90
            elif self.direction == LEFT:
                angle_offset = 180
            elif self.direction == DOWN:
                angle_offset = 270

            # Створюємо поверхню для малювання пакмена
            surf = pygame.Surface((self.radius * 2 + 2, self.radius * 2 + 2), pygame.SRCALPHA)
            surf_center = (self.radius + 1, self.radius + 1)

            # Малюємо повне коло
            pygame.draw.circle(surf, YELLOW, surf_center, self.radius)

            # Видаляємо трикутник для пасти
            if self.mouth_angle > 0:
                points = [surf_center]

                # Обчислюємо точки трикутника пасти
                angle1 = math.radians(angle_offset + self.mouth_angle)
                angle2 = math.radians(angle_offset - self.mouth_angle)

                x1 = surf_center[0] + self.radius * math.cos(angle1)
                y1 = surf_center[1] - self.radius * math.sin(angle1)
                x2 = surf_center[0] + self.radius * math.cos(angle2)
                y2 = surf_center[1] - self.radius * math.sin(angle2)

                points.extend([(x1, y1), (x2, y2)])

                # Малюємо чорний трикутник щоб створити пасту
                pygame.draw.polygon(surf, (0, 0, 0, 0), points)

            # Переносимо на основний екран
            screen.blit(surf, (center[0] - self.radius - 1, center[1] - self.radius - 1))

        # Малюємо очі
        if self.direction == RIGHT:
            eye_pos = (center[0] - 3, center[1] - 5)
        elif self.direction == LEFT:
            eye_pos = (center[0] + 3, center[1] - 5)
        elif self.direction == UP:
            eye_pos = (center[0] + 5, center[1] + 3)
        elif self.direction == DOWN:
            eye_pos = (center[0] - 5, center[1] - 3)
        else:
            eye_pos = (center[0], center[1] - 5)

        pygame.draw.circle(screen, BLACK, eye_pos, 2)