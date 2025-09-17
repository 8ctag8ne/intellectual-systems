import pygame
import math
from src.constants import *


class Pacman:
    def __init__(self, x, y, game):
        self.grid_x = x // CELL_SIZE
        self.grid_y = y // CELL_SIZE
        self.target_x = self.grid_x
        self.target_y = self.grid_y
        self.x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
        self.y = self.grid_y * CELL_SIZE + CELL_SIZE // 2
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.move_progress = 0.0  # 0.0 - 1.0, прогресс руху до наступної клітинки
        self.move_speed = 5.0  # швидкість анімації (клітинок в секунду)
        self.radius = CELL_SIZE // 2 - 2
        self.mouth_angle = 0
        self.mouth_opening = True
        self.game = game

    def set_direction(self, direction):
        self.next_direction = direction

    def can_move(self, direction, walls):
        next_x = self.grid_x + direction[0]
        next_y = self.grid_y + direction[1]

        # Дозволяємо рух через тунелі
        next_x = (next_x + self.game.map_width) % self.game.map_width
        next_y = (next_y + self.game.map_height) % self.game.map_height

        return (next_x, next_y) not in walls

    def update(self, dt, walls):
        # Якщо ми досягли цільової клітинки
        if self.grid_x == self.target_x and self.grid_y == self.target_y:
            # Спробувати змінити напрямок
            if self.next_direction != (0, 0) and self.can_move(self.next_direction, walls):
                self.direction = self.next_direction
                self.next_direction = (0, 0)

            # Почати рух у поточному напрямку
            if self.direction != (0, 0) and self.can_move(self.direction, walls):
                self.target_x = self.grid_x + self.direction[0]
                self.target_y = self.grid_y + self.direction[1]

                # Обробка тунелів
                self.target_x = (self.target_x + self.game.map_width) % self.game.map_width
                self.target_y = (self.target_y + self.game.map_height) % self.game.map_height

                self.move_progress = 0.0

            is_tunnel_move = (
                    abs(self.target_x - self.grid_x) > 1 or
                    abs(self.target_y - self.grid_y) > 1
            )

            if is_tunnel_move:
                # Миттєвий перехід для тунелів
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
                self.y = self.grid_y * CELL_SIZE + CELL_SIZE // 2
                self.move_progress = 0.0
            else:
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

        # Оновлення анімації пасти
        if self.direction != (0, 0):
            if self.mouth_opening:
                self.mouth_angle += 300 * dt
                if self.mouth_angle >= 45:
                    self.mouth_angle = 45
                    self.mouth_opening = False
            else:
                self.mouth_angle -= 300 * dt
                if self.mouth_angle <= 0:
                    self.mouth_angle = 0
                    self.mouth_opening = True

    # draw метод залишається незмінним

    def draw(self, screen):
        # [Малювання залишається незмінним]
        center = (int(self.x), int(self.y))

        if self.direction == (0, 0):
            pygame.draw.circle(screen, YELLOW, center, self.radius)
        else:
            angle_offset = 0
            if self.direction == RIGHT:
                angle_offset = 0
            elif self.direction == UP:
                angle_offset = 90
            elif self.direction == LEFT:
                angle_offset = 180
            elif self.direction == DOWN:
                angle_offset = 270

            surf = pygame.Surface((self.radius * 2 + 2, self.radius * 2 + 2), pygame.SRCALPHA)
            surf_center = (self.radius + 1, self.radius + 1)
            pygame.draw.circle(surf, YELLOW, surf_center, self.radius)

            if self.mouth_angle > 0:
                points = [surf_center]
                angle1 = math.radians(angle_offset + self.mouth_angle)
                angle2 = math.radians(angle_offset - self.mouth_angle)
                x1 = surf_center[0] + self.radius * math.cos(angle1)
                y1 = surf_center[1] - self.radius * math.sin(angle1)
                x2 = surf_center[0] + self.radius * math.cos(angle2)
                y2 = surf_center[1] - self.radius * math.sin(angle2)
                points.extend([(x1, y1), (x2, y2)])
                pygame.draw.polygon(surf, (0, 0, 0, 0), points)

            screen.blit(surf, (center[0] - self.radius - 1, center[1] - self.radius - 1))

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