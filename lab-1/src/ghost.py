# ghost.py (оновлений для сумісності з новою системою ШІ)
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
        self.move_progress = 0.0
        self.move_speed = GHOST_SPEED
        self.size = CELL_SIZE - 4
        self.animation_timer = 0
        self.game = game
        self.ai = None
        self.decision_timer = 0
        self.decision_delay = AI_DECISION_DELAY  # Трохи швидший відгук для кращої координації
        self.last_direction = (0, 0)

    def get_color_name(self):
        """Повертає назву кольору привида"""
        color_names = {
            (255, 0, 0): "Red",
            (0, 0, 255): "Blue",
            (255, 192, 203): "Pink",
            (255, 165, 0): "Orange"
        }
        return color_names.get(self.color, "Unknown")

    def set_ai(self, ai):
        """Встановлює ШІ для цього привида"""
        self.ai = ai
        print(f"Setting AI for ghost at ({self.grid_x}, {self.grid_y}): {type(ai).__name__}")
        if hasattr(ai, 'rules'):
            print(f"  Rules: {[rule.__class__.__name__ for rule in ai.rules]}")

    def get_valid_directions(self, walls, ghosts):
        """Повертає список валідних напрямків руху без перевірки на інших привидів (для зворотної сумісності)"""
        valid_directions = []
        for direction in DIRECTIONS:
            next_x = self.grid_x + direction[0]
            next_y = self.grid_y + direction[1]

            next_x = (next_x + self.game.map_width) % self.game.map_width
            next_y = (next_y + self.game.map_height) % self.game.map_height

            if (next_x, next_y) not in walls:
                valid_directions.append(direction)

        return valid_directions

    def update(self, dt, walls, pacman, ghosts):
        # Зберігаємо dt в game для використання в ШІ
        self.game.dt = dt

        # Оновлення анімації
        self.animation_timer += dt
        self.decision_timer += dt

        # Якщо ми досягли цільової клітинки
        if self.grid_x == self.target_x and self.grid_y == self.target_y:
            new_direction = self.direction

            # Використовуємо ШІ для прийняття рішення про напрямок
            if self.ai and self.decision_timer >= self.decision_delay:
                try:
                    # Передаємо поточний напрямок в ШІ для кращого контексту
                    if hasattr(self.ai, 'current_direction'):
                        self.ai.current_direction = self.direction

                    new_direction = self.ai.get_next_direction(walls, pacman, ghosts)
                    self.decision_timer = 0

                    # Debug інформація (рідко)
                    if hasattr(self.ai, 'rules') and random.random() < 0.005:  # 0.5% шанс
                        active_rules = []
                        for rule in self.ai.rules:
                            if rule.enabled:
                                try:
                                    direction, strength = rule.evaluate(self.ai, walls, pacman, ghosts)
                                    if direction and strength > 0:
                                        active_rules.append(f"{rule.__class__.__name__}({strength:.1f})")
                                except:
                                    pass

                        if active_rules:
                            print(f"Ghost at ({self.grid_x},{self.grid_y}) -> {new_direction}: {active_rules}")

                except Exception as e:
                    print(f"Error in AI decision making: {e}")
                    # Fallback до розумного випадкового руху
                    valid_dirs = self.get_valid_directions_with_smart_fallback(walls, ghosts)
                    new_direction = valid_dirs[0] if valid_dirs else (0, 0)

            # Перевіряємо чи можна рухатися в новому напрямку
            if new_direction != (0, 0):
                next_x = self.grid_x + new_direction[0]
                next_y = self.grid_y + new_direction[1]

                # Обробка тунелів
                next_x = (next_x + self.game.map_width) % self.game.map_width
                next_y = (next_y + self.game.map_height) % self.game.map_height

                # Перевірка на стіни
                can_move = (next_x, next_y) not in walls

                # Перевірка на зіткнення з іншими привидами
                if can_move:
                    for other_ghost in ghosts:
                        if other_ghost != self:
                            if ((other_ghost.grid_x == next_x and other_ghost.grid_y == next_y) or
                                    (other_ghost.target_x == next_x and other_ghost.target_y == next_y)):
                                can_move = False
                                break

                if can_move:
                    self.direction = new_direction
                    self.target_x = next_x
                    self.target_y = next_y
                    self.move_progress = 0.0
                    self.last_direction = new_direction
                else:
                    # Якщо не можемо рухатися, спробуємо знайти альтернативу
                    fallback_dirs = self.get_valid_directions_with_smart_fallback(walls, ghosts)
                    if fallback_dirs:
                        alt_direction = fallback_dirs[0]
                        alt_x = self.grid_x + alt_direction[0]
                        alt_y = self.grid_y + alt_direction[1]

                        alt_x = (alt_x + self.game.map_width) % self.game.map_width
                        alt_y = (alt_y + self.game.map_height) % self.game.map_height

                        self.direction = alt_direction
                        self.target_x = alt_x
                        self.target_y = alt_y
                        self.move_progress = 0.0
                    else:
                        # Якщо зовсім немає варіантів, зупиняємося
                        self.direction = (0, 0)

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
                self.x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
                self.y = self.grid_y * CELL_SIZE + CELL_SIZE // 2
            else:
                # Інтерполюємо позицію
                self.x = (self.grid_x + (self.target_x - self.grid_x) * self.move_progress) * CELL_SIZE + CELL_SIZE // 2
                self.y = (self.grid_y + (self.target_y - self.grid_y) * self.move_progress) * CELL_SIZE + CELL_SIZE // 2

    def get_valid_directions_with_smart_fallback(self, walls, ghosts):
        """Повертає валідні напрямки з розумним вибором для уникнення застрягання"""
        valid_directions = []
        for direction in DIRECTIONS:
            next_x = self.grid_x + direction[0]
            next_y = self.grid_y + direction[1]

            next_x = (next_x + self.game.map_width) % self.game.map_width
            next_y = (next_y + self.game.map_height) % self.game.map_height

            if (next_x, next_y) not in walls:
                collision = False
                for other_ghost in ghosts:
                    if other_ghost != self:
                        if ((other_ghost.grid_x == next_x and other_ghost.grid_y == next_y) or
                                (other_ghost.target_x == next_x and other_ghost.target_y == next_y)):
                            collision = True
                            break

                if not collision:
                    valid_directions.append(direction)

        if not valid_directions:
            return []

        # Сортуємо напрямки: спочатку ті, що не є поворотом назад
        opposite = (-self.last_direction[0], -self.last_direction[1])
        preferred_dirs = [d for d in valid_directions if d != opposite]

        if preferred_dirs:
            return preferred_dirs + [d for d in valid_directions if d == opposite]
        else:
            return valid_directions

    def check_collision(self, pacman):
        # Перевіряємо зіткнення з пекменом
        distance = math.sqrt((self.x - pacman.x) ** 2 + (self.y - pacman.y) ** 2)
        return self.grid_x == pacman.grid_x and self.grid_y == pacman.grid_y

    def draw(self, screen):
        center = (int(self.x), int(self.y))
        half_size = self.size // 2

        # Тіло привида
        body_rect = pygame.Rect(center[0] - half_size, center[1] - half_size,
                                self.size, self.size)
        pygame.draw.rect(screen, self.color, body_rect)

        # Голова
        pygame.draw.circle(screen, self.color,
                           (center[0], center[1] - half_size + half_size // 2),
                           half_size)

        # Хвилясті краї знизу
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

        # Очі
        eye_size = 3
        eye_y = center[1] - half_size // 2
        left_eye = (center[0] - half_size // 2, eye_y)
        right_eye = (center[0] + half_size // 2, eye_y)

        pygame.draw.circle(screen, WHITE, left_eye, eye_size)
        pygame.draw.circle(screen, WHITE, right_eye, eye_size)
        pygame.draw.circle(screen, BLACK, left_eye, eye_size // 2)
        pygame.draw.circle(screen, BLACK, right_eye, eye_size // 2)