# ghost_ai.py - Покращена система ШІ з правилами
import random
import math
from collections import deque

from src.constants import *


class GhostRule:
    """Базовий клас для правила поведінки привида"""

    def __init__(self, priority=1.0, enabled=True):
        self.priority = priority  # Пріоритет правила (вищий = важливіший)
        self.enabled = enabled  # Чи активне правило

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        """Оцінює правило і повертає (direction, strength)"""
        return None, 0.0

    def get_name(self):
        """Повертає назву правила"""
        return self.__class__.__name__


class SeekPacmanRule(GhostRule):
    """Правило: йти до пакмена якщо його видно"""

    def __init__(self, view_distance=5, priority=3.0):
        super().__init__(priority)
        self.view_distance = view_distance

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        if not ghost_ai.can_see_pacman(pacman, walls, self.view_distance):
            return None, 0.0

        # Обчислюємо напрямок до пакмена
        dx = pacman.grid_x - ghost_ai.ghost.grid_x
        dy = pacman.grid_y - ghost_ai.ghost.grid_y

        # Визначаємо основний напрямок
        if abs(dx) > abs(dy):
            direction = (1 if dx > 0 else -1, 0)
        else:
            direction = (0, 1 if dy > 0 else -1)

        # Перевіряємо чи можна рухатися в цьому напрямку
        valid_dirs = ghost_ai.get_valid_directions_no_collision(walls, other_ghosts)
        if direction in valid_dirs:
            distance = math.sqrt(dx * dx + dy * dy)
            strength = min(1.0, self.view_distance / (distance + 0.1))
            return direction, strength * self.priority

        return None, 0.0


class PredictPacmanRule(GhostRule):
    """Правило: передбачати рух пакмена і йти на перехоплення"""

    def __init__(self, prediction_steps=3, priority=2.5):
        super().__init__(priority)
        self.prediction_steps = prediction_steps

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        # Передбачаємо куди рухатиметься пакмен
        pacman_dir = pacman.direction
        if pacman_dir == (0, 0):
            return None, 0.0

        # Обчислюємо передбачувану позицію пакмена
        predicted_x = pacman.grid_x + pacman_dir[0] * self.prediction_steps
        predicted_y = pacman.grid_y + pacman_dir[1] * self.prediction_steps

        # Обчислюємо напрямок до передбачуваної позиції
        dx = predicted_x - ghost_ai.ghost.grid_x
        dy = predicted_y - ghost_ai.ghost.grid_y

        if abs(dx) > abs(dy):
            direction = (1 if dx > 0 else -1, 0)
        else:
            direction = (0, 1 if dy > 0 else -1)

        valid_dirs = ghost_ai.get_valid_directions_no_collision(walls, other_ghosts)
        if direction in valid_dirs:
            distance = math.sqrt(dx * dx + dy * dy)
            strength = min(1.0, 10.0 / (distance + 1))
            return direction, strength * self.priority

        return None, 0.0


class FlankPacmanRule(GhostRule):
    def __init__(self, priority=2.0):
        super().__init__(priority)

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        # Визначаємо напрямок руху пакмена
        pacman_dir = pacman.direction
        if pacman_dir == (0, 0):
            # Якщо пакмен не рухається, виходимо
            return None, 0.0

        # Визначаємо позицію, в якій пакмен буде через кілька кроків
        predicted_x = pacman.grid_x + pacman_dir[0] * 3
        predicted_y = pacman.grid_y + pacman_dir[1] * 3

        # Визначаємо флангову позицію (збоку від передбачуваного напрямку руху)
        # Спершу визначаємо перпендикулярні напрямки до напрямку руху пакмена
        flank_positions = []
        if pacman_dir[0] != 0:  # Рух по горизонталі
            flank_positions.append((predicted_x, predicted_y + 1))
            flank_positions.append((predicted_x, predicted_y - 1))
        else:  # Рух по вертикалі
            flank_positions.append((predicted_x + 1, predicted_y))
            flank_positions.append((predicted_x - 1, predicted_y))

        # Вибираємо найближчу флангову позицію
        best_flank = None
        min_dist = float('inf')
        for pos in flank_positions:
            dist = math.sqrt((ghost_ai.ghost.grid_x - pos[0])**2 +
                             (ghost_ai.ghost.grid_y - pos[1])**2)
            if dist < min_dist:
                min_dist = dist
                best_flank = pos

        if best_flank is None:
            return None, 0.0

        # Рухаємося до флангової позиції
        dx = best_flank[0] - ghost_ai.ghost.grid_x
        dy = best_flank[1] - ghost_ai.ghost.grid_y

        if abs(dx) > abs(dy):
            direction = (1 if dx > 0 else -1, 0)
        else:
            direction = (0, 1 if dy > 0 else -1)

        valid_dirs = ghost_ai.get_valid_directions_no_collision(walls, other_ghosts)
        if direction in valid_dirs:
            distance = math.sqrt(dx*dx + dy*dy)
            strength = min(1.0, 5.0 / (distance + 0.1))
            return direction, strength * self.priority

        return None, 0.0


class AvoidOtherGhostsRule(GhostRule):
    def __init__(self, min_distance=2, priority=1.5):
        super().__init__(priority)
        self.min_distance = min_distance

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        # Знаходимо всіх привидів у межах min_distance
        nearby_ghosts = []
        for ghost in other_ghosts:
            if ghost != ghost_ai.ghost:
                dist = math.sqrt((ghost.grid_x - ghost_ai.ghost.grid_x) ** 2 +
                                 (ghost.grid_y - ghost_ai.ghost.grid_y) ** 2)
                if dist < self.min_distance:
                    nearby_ghosts.append(ghost)

        if not nearby_ghosts:
            return None, 0.0

        # Обчислюємо середній вектор відштовхування
        repulse_x, repulse_y = 0, 0
        for ghost in nearby_ghosts:
            dx = ghost_ai.ghost.grid_x - ghost.grid_x
            dy = ghost_ai.ghost.grid_y - ghost.grid_y
            distance = max(0.1, math.sqrt(dx*dx + dy*dy))
            repulse_x += dx / distance
            repulse_y += dy / distance

        # Нормалізуємо вектор
        magnitude = math.sqrt(repulse_x*repulse_x + repulse_y*repulse_y)
        if magnitude > 0:
            repulse_x /= magnitude
            repulse_y /= magnitude

        # Знаходимо напрямок, який найкраще відповідає вектору відштовхування
        best_direction = None
        best_score = -float('inf')
        valid_dirs = ghost_ai.get_valid_directions_no_collision(walls, other_ghosts)

        for direction in valid_dirs:
            score = direction[0] * repulse_x + direction[1] * repulse_y
            if score > best_score:
                best_score = score
                best_direction = direction

        if best_direction:
            # Сила залежить від відстані до найближчого привида
            min_dist = min(math.sqrt((g.grid_x - ghost_ai.ghost.grid_x)**2 +
                                    (g.grid_y - ghost_ai.ghost.grid_y)**2) for g in nearby_ghosts)
            strength = (self.min_distance - min_dist) / self.min_distance
            return best_direction, strength * self.priority

        return None, 0.0

class PatrolRule(GhostRule):
    def __init__(self, patrol_points=None, priority=1.0):
        super().__init__(priority)
        self.patrol_points = patrol_points or []
        self.current_target_index = 0
        self.last_pacman_position = None

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        if not self.patrol_points:
            return None, 0.0

        # Якщо пакмен поруч, зменшуємо пріоритет патрулювання
        dist_to_pacman = math.sqrt((ghost_ai.ghost.grid_x - pacman.grid_x)**2 +
                                   (ghost_ai.ghost.grid_y - pacman.grid_y)**2)
        if dist_to_pacman < 5:
            return None, 0.0

        # Якщо пакмен рухається, можемо адаптувати точки патрулювання
        if pacman.direction != (0, 0) and self.last_pacman_position:
            # Визначаємо напрямок руху пакмена
            dx = pacman.grid_x - self.last_pacman_position[0]
            dy = pacman.grid_y - self.last_pacman_position[1]
            if dx != 0 or dy != 0:
                # Зміщуємо точки патрулювання в напрямку руху пакмена
                adapted_points = []
                for point in self.patrol_points:
                    new_point = (point[0] + dx * 2, point[1] + dy * 2)
                    # Перевіряємо, чи нова точка в межах карти
                    new_point = (new_point[0] % ghost_ai.game.map_width,
                                 new_point[1] % ghost_ai.game.map_height)
                    if new_point not in walls:
                        adapted_points.append(new_point)
                    else:
                        adapted_points.append(point)
                self.patrol_points = adapted_points

        self.last_pacman_position = (pacman.grid_x, pacman.grid_y)

        target_x, target_y = self.patrol_points[self.current_target_index]

        # Якщо дійшли до цілі, переходимо до наступної
        if (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y) == (target_x, target_y):
            self.current_target_index = (self.current_target_index + 1) % len(self.patrol_points)
            target_x, target_y = self.patrol_points[self.current_target_index]

        # Рухаємося до цілі
        dx = target_x - ghost_ai.ghost.grid_x
        dy = target_y - ghost_ai.ghost.grid_y

        if abs(dx) > abs(dy):
            direction = (1 if dx > 0 else -1, 0)
        else:
            direction = (0, 1 if dy > 0 else -1)

        valid_dirs = ghost_ai.get_valid_directions_no_collision(walls, other_ghosts)
        if direction in valid_dirs:
            return direction, self.priority

        return None, 0.0


class BlockEscapeRoute(GhostRule):
    def __init__(self, priority=2.2):
        super().__init__(priority)

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        # Знаходимо можливі шляхи втечі пакмена
        pacman_valid_dirs = []
        for direction in DIRECTIONS:
            next_x = pacman.grid_x + direction[0]
            next_y = pacman.grid_y + direction[1]

            next_x = (next_x + ghost_ai.game.map_width) % ghost_ai.game.map_width
            next_y = (next_y + ghost_ai.game.map_height) % ghost_ai.game.map_height

            if (next_x, next_y) not in walls:
                pacman_valid_dirs.append((next_x, next_y))

        if len(pacman_valid_dirs) <= 1:
            return None, 0.0  # Пакмен вже заблокований або в тупику

        # Сортуємо виходи за пріоритетом: спочатку ті, що в напрямку руху пакмена
        if pacman.direction != (0, 0):
            # Якщо пакмен рухається, найімовірніший вихід - попереду
            preferred_exit = (pacman.grid_x + pacman.direction[0],
                              pacman.grid_y + pacman.direction[1])
            if preferred_exit in pacman_valid_dirs:
                pacman_valid_dirs.remove(preferred_exit)
                pacman_valid_dirs.insert(0, preferred_exit)

        # Визначаємо, які виходи вже блокуються іншими привидами
        blocked_exits = set()
        for ghost in other_ghosts:
            if ghost != ghost_ai.ghost:
                # Перевіряємо, чи рухається привид до якогось виходу
                for exit_pos in pacman_valid_dirs:
                    if (ghost.target_x, ghost.target_y) == exit_pos:
                        blocked_exits.add(exit_pos)
                    # Також перевіряємо, чи вже знаходиться на виході
                    if (ghost.grid_x, ghost.grid_y) == exit_pos:
                        blocked_exits.add(exit_pos)

        # Знаходимо найважливіший незаблокований вихід
        for exit_pos in pacman_valid_dirs:
            if exit_pos not in blocked_exits:
                target_exit = exit_pos
                break
        else:
            # Всі виходи заблоковані
            return None, 0.0

        # Рухаємося до виходу
        dx = target_exit[0] - ghost_ai.ghost.grid_x
        dy = target_exit[1] - ghost_ai.ghost.grid_y

        if abs(dx) > abs(dy):
            direction = (1 if dx > 0 else -1, 0)
        else:
            direction = (0, 1 if dy > 0 else -1)

        valid_dirs = ghost_ai.get_valid_directions_no_collision(walls, other_ghosts)
        if direction in valid_dirs:
            distance = math.sqrt(dx*dx + dy*dy)
            strength = min(1.0, 5.0 / (distance + 0.1))
            return direction, strength * self.priority

        return None, 0.0


class WanderRule(GhostRule):
    def __init__(self, priority=0.5):
        super().__init__(priority)
        self.current_direction = (0, 0)
        self.last_positions = []  # Історія позицій для виявлення циклів
        self.max_history = 10
        self.stuck_counter = 0

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        valid_dirs = ghost_ai.get_valid_directions_no_collision(walls, other_ghosts)
        if not valid_dirs:
            return None, 0.0

        # Додаємо поточну позицію до історії
        current_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        self.last_positions.append(current_pos)
        if len(self.last_positions) > self.max_history:
            self.last_positions.pop(0)

        # Перевіряємо чи не застрягли в циклі (часто повторювані позиції)
        if len(set(self.last_positions)) < len(self.last_positions) // 2:
            self.stuck_counter += 1
        else:
            self.stuck_counter = max(0, self.stuck_counter - 1)

        # Якщо застрягли, змінюємо стратегію
        if self.stuck_counter > 3:
            # Скидаємо історію та обираємо абсолютно новий напрямок
            self.last_positions = []
            self.stuck_counter = 0
            return random.choice(valid_dirs), self.priority * 1.5

        # Уникаємо повернення назад, якщо є інші варіанти
        opposite = (-self.current_direction[0], -self.current_direction[1])
        preferred_dirs = [d for d in valid_dirs if d != opposite] or valid_dirs

        # Іноді дозволяємо зміну напрямку навіть якщо можемо продовжувати
        change_chance = 0.3 if len(valid_dirs) > 1 else 0.0

        if (self.current_direction not in preferred_dirs or
                random.random() < change_chance):
            new_direction = random.choice(preferred_dirs)
            self.current_direction = new_direction
            return new_direction, self.priority

        return self.current_direction, self.priority


class RuleBasedGhostAI:
    """ШІ привида на основі правил"""

    def __init__(self, ghost, game, rules=None):
        self.ghost = ghost
        self.game = game
        self.rules = rules or []
        self.current_direction = random.choice(DIRECTIONS)
        self.stuck_counter = 0
        self.recent_positions = deque(maxlen=10)  # Для відстеження циклів

    def add_rule(self, rule):
        """Додає правило до списку"""
        self.rules.append(rule)

    def get_next_direction(self, walls, pacman, other_ghosts):
        # Збираємо всі активовані правила
        direction_scores = {}

        for rule in self.rules:
            if rule.enabled:
                direction, strength = rule.evaluate(self, walls, pacman, other_ghosts)
                if direction is not None and strength > 0:
                    if direction not in direction_scores:
                        direction_scores[direction] = 0
                    direction_scores[direction] += strength

        if not direction_scores:
            valid_dirs = self.get_valid_directions_no_collision(walls, other_ghosts)
            if valid_dirs:
                return random.choice(valid_dirs)
            return (0, 0)

        # Знаходимо напрямок з найвищою сумарною вагою
        best_direction = max(direction_scores.items(), key=lambda x: x[1])[0]

        # Додаткова перевірка: чи не веде цей напрямок до циклічної поведінки
        current_pos = (self.ghost.grid_x, self.ghost.grid_y)
        self.recent_positions.append(current_pos)
        next_pos = (current_pos[0] + best_direction[0],
                    current_pos[1] + best_direction[1])

        # Якщо ми нещодавно були в цій позиції, зменшуємо його пріоритет
        if hasattr(self, 'recent_positions') and next_pos in self.recent_positions:
            # Спробуємо знайти альтернативний напрямок
            alternative_dirs = [d for d in direction_scores.keys() if d != best_direction]
            if alternative_dirs:
                # Обираємо найкращий альтернативний напрямок
                best_direction = max(alternative_dirs,
                                     key=lambda d: direction_scores[d])

        return best_direction

    def can_see_pacman(self, pacman, walls, view_distance=float('inf')):
        """Перевіряє чи може привид бачити пакмена"""
        dx = abs(self.ghost.grid_x - pacman.grid_x)
        dy = abs(self.ghost.grid_y - pacman.grid_y)
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > view_distance:
            return False

        return self.has_line_of_sight(pacman, walls)

    def has_line_of_sight(self, pacman, walls):
        """Перевіряє чи є прямий шлях до пакмена"""
        x1, y1 = self.ghost.grid_x, self.ghost.grid_y
        x2, y2 = pacman.grid_x, pacman.grid_y

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        if dx == 0 and dy == 0:
            return True

        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        x, y = x1, y1

        while True:
            if (x, y) in walls:
                return False

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return True

    def get_valid_directions_no_collision(self, walls, other_ghosts):
        """Повертає валідні напрямки без зіткнень"""
        valid_directions = []
        for direction in DIRECTIONS:
            next_x = self.ghost.grid_x + direction[0]
            next_y = self.ghost.grid_y + direction[1]

            next_x = (next_x + self.game.map_width) % self.game.map_width
            next_y = (next_y + self.game.map_height) % self.game.map_height

            if (next_x, next_y) not in walls:
                collision = False
                for other_ghost in other_ghosts:
                    if other_ghost != self.ghost:
                        if ((other_ghost.grid_x == next_x and other_ghost.grid_y == next_y) or
                                (other_ghost.target_x == next_x and other_ghost.target_y == next_y)):
                            collision = True
                            break

                if not collision:
                    valid_directions.append(direction)

        return valid_directions


# Збереження старих класів для зворотної сумісності
RandomGhostAI = RuleBasedGhostAI
ChaserGhostAI = RuleBasedGhostAI
PatrolGhostAI = RuleBasedGhostAI
CooperativeGhostAI = RuleBasedGhostAI