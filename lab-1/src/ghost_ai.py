# ghost_ai.py - Покращена система ШІ з правилами
import random
import math
from collections import deque

from src.constants import *

import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('GhostAI')


def bfs_next_step(start_pos, target_pos, walls, map_width, map_height, avoid_positions=None):
    """
    BFS пошук наступного кроку до цілі
    Повертає напрямок для наступного кроку або None якщо шлях не знайдено
    """
    if start_pos == target_pos:
        return None

    avoid_positions = avoid_positions or set()
    queue = deque([(start_pos, [])])  # (позиція, шлях_до_неї)
    visited = {start_pos}

    while queue:
        (x, y), path = queue.popleft()

        # Перевіряємо всі можливі напрямки
        for direction in DIRECTIONS:
            next_x = (x + direction[0]) % map_width
            next_y = (y + direction[1]) % map_height
            next_pos = (next_x, next_y)

            if next_pos in visited or next_pos in walls or next_pos in avoid_positions:
                continue

            new_path = path + [direction]

            if next_pos == target_pos:
                # Знайшли шлях - повертаємо перший крок
                return new_path[0] if new_path else None

            queue.append((next_pos, new_path))
            visited.add(next_pos)

            # Обмежуємо глибину пошуку для продуктивності
            if len(new_path) > 15:
                break

    return None


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
    """Пошук пакмена з BFS"""

    def __init__(self, view_distance=5, priority=3.0):
        super().__init__(priority)
        self.view_distance = view_distance

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        # Перевіряємо чи бачимо пакмена
        distance = math.sqrt((ghost_ai.ghost.grid_x - pacman.grid_x) ** 2 +
                             (ghost_ai.ghost.grid_y - pacman.grid_y) ** 2)
        if distance > self.view_distance:
            return None, 0.0

        # Використовуємо BFS для знаходження шляху
        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        pacman_pos = (pacman.grid_x, pacman.grid_y)

        # Уникаємо позицій інших привидів
        avoid_positions = set()
        for ghost in other_ghosts:
            if ghost != ghost_ai.ghost:
                avoid_positions.add((ghost.grid_x, ghost.grid_y))
                avoid_positions.add((ghost.target_x, ghost.target_y))

        direction = bfs_next_step(ghost_pos, pacman_pos, walls,
                                  ghost_ai.game.map_width, ghost_ai.game.map_height,
                                  avoid_positions)

        if direction:
            strength = min(1.0, self.view_distance / (distance + 0.1))
            return direction, strength * self.priority

        return None, 0.0


class PredictPacmanRule(GhostRule):
    """Передбачення руху пакмена з BFS"""

    def __init__(self, prediction_steps=3, priority=2.5):
        super().__init__(priority)
        self.prediction_steps = prediction_steps

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        if pacman.direction == (0, 0):
            return None, 0.0

        # Передбачаємо позицію пакмена
        pred_x = pacman.grid_x + pacman.direction[0] * self.prediction_steps
        pred_y = pacman.grid_y + pacman.direction[1] * self.prediction_steps
        pred_pos = (pred_x % ghost_ai.game.map_width, pred_y % ghost_ai.game.map_height)

        if pred_pos in walls:
            return None, 0.0

        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        avoid_positions = {(g.grid_x, g.grid_y) for g in other_ghosts if g != ghost_ai.ghost}

        direction = bfs_next_step(ghost_pos, pred_pos, walls,
                                  ghost_ai.game.map_width, ghost_ai.game.map_height,
                                  avoid_positions)

        if direction:
            distance = math.sqrt((ghost_pos[0] - pred_pos[0]) ** 2 +
                                 (ghost_pos[1] - pred_pos[1]) ** 2)
            strength = min(1.0, 10.0 / (distance + 1))
            return direction, strength * self.priority

        return None, 0.0


class FlankPacmanRule(GhostRule):
    """Фланговий маневр з BFS"""

    def __init__(self, priority=2.0):
        super().__init__(priority)

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        if pacman.direction == (0, 0):
            return None, 0.0

        # Передбачаємо позицію пакмена
        pred_x = pacman.grid_x + pacman.direction[0] * 3
        pred_y = pacman.grid_y + pacman.direction[1] * 3

        # Знаходимо фланкові позиції
        flank_positions = []
        if pacman.direction[0] != 0:  # горизонтальний рух
            flank_positions = [(pred_x, pred_y + 2), (pred_x, pred_y - 2)]
        else:  # вертикальний рух
            flank_positions = [(pred_x + 2, pred_y), (pred_x - 2, pred_y)]

        # Знаходимо найкращу доступну фланкову позицію
        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        avoid_positions = {(g.grid_x, g.grid_y) for g in other_ghosts if g != ghost_ai.ghost}

        for target_pos in flank_positions:
            # Нормалізуємо координати для тунелів
            norm_pos = (target_pos[0] % ghost_ai.game.map_width,
                        target_pos[1] % ghost_ai.game.map_height)

            if norm_pos not in walls:
                direction = bfs_next_step(ghost_pos, norm_pos, walls,
                                          ghost_ai.game.map_width, ghost_ai.game.map_height,
                                          avoid_positions)
                if direction:
                    distance = math.sqrt((ghost_pos[0] - norm_pos[0]) ** 2 +
                                         (ghost_pos[1] - norm_pos[1]) ** 2)
                    strength = min(1.0, 5.0 / (distance + 0.1))
                    return direction, strength * self.priority

        return None, 0.0


class AvoidOtherGhostsRule(GhostRule):
    """Уникнення інших привидів"""

    def __init__(self, min_distance=2, priority=1.5):
        super().__init__(priority)
        self.min_distance = min_distance

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)

        # Знаходимо близьких привидів
        close_ghosts = []
        for ghost in other_ghosts:
            if ghost != ghost_ai.ghost:
                distance = math.sqrt((ghost.grid_x - ghost_pos[0]) ** 2 +
                                     (ghost.grid_y - ghost_pos[1]) ** 2)
                if distance < self.min_distance:
                    close_ghosts.append(ghost)

        if not close_ghosts:
            return None, 0.0

        # Знаходимо найкращий напрямок для втечі
        valid_dirs = []
        for direction in DIRECTIONS:
            next_x = (ghost_pos[0] + direction[0]) % ghost_ai.game.map_width
            next_y = (ghost_pos[1] + direction[1]) % ghost_ai.game.map_height

            if (next_x, next_y) not in walls:
                # Перевіряємо чи віддаляє цей напрямок від близьких привидів
                total_distance = 0
                for close_ghost in close_ghosts:
                    dist = math.sqrt((close_ghost.grid_x - next_x) ** 2 +
                                     (close_ghost.grid_y - next_y) ** 2)
                    total_distance += dist

                valid_dirs.append((direction, total_distance))

        if close_ghosts and valid_dirs:
            color_name = ghost_ai.ghost.get_color_name()
            logger.info(f"{color_name} ghost avoiding {len(close_ghosts)} nearby ghosts")

        if valid_dirs:
            # Обираємо напрямок, що максимізує відстань
            best_direction = max(valid_dirs, key=lambda x: x[1])[0]
            strength = (self.min_distance - min(math.sqrt((g.grid_x - ghost_pos[0]) ** 2 +
                                                          (g.grid_y - ghost_pos[1]) ** 2)
                                                for g in close_ghosts)) / self.min_distance
            return best_direction, strength * self.priority

        return None, 0.0


class PatrolRule(GhostRule):
    """Патрулювання з BFS"""

    def __init__(self, patrol_points=None, priority=1.0):
        super().__init__(priority)
        self.patrol_points = patrol_points or []
        self.current_target = 0

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        if not self.patrol_points:
            return None, 0.0

        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        target_pos = self.patrol_points[self.current_target]

        # Якщо досягли цілі, переходимо до наступної
        if ghost_pos == target_pos:
            self.current_target = (self.current_target + 1) % len(self.patrol_points)
            target_pos = self.patrol_points[self.current_target]

        avoid_positions = {(g.grid_x, g.grid_y) for g in other_ghosts if g != ghost_ai.ghost}

        direction = bfs_next_step(ghost_pos, target_pos, walls,
                                  ghost_ai.game.map_width, ghost_ai.game.map_height,
                                  avoid_positions)

        return (direction, self.priority) if direction else (None, 0.0)


class BlockEscapeRoute(GhostRule):
    """Блокування виходів з BFS"""

    def __init__(self, priority=2.2):
        super().__init__(priority)

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        # Знаходимо можливі виходи пакмена
        pacman_pos = (pacman.grid_x, pacman.grid_y)
        exit_positions = []

        for direction in DIRECTIONS:
            exit_x = (pacman.grid_x + direction[0]) % ghost_ai.game.map_width
            exit_y = (pacman.grid_y + direction[1]) % ghost_ai.game.map_height
            if (exit_x, exit_y) not in walls:
                exit_positions.append((exit_x, exit_y))

        if len(exit_positions) <= 1:
            return None, 0.0

        # Знаходимо вихід, який не блокується іншими привидами
        blocked_exits = set()
        for ghost in other_ghosts:
            if ghost != ghost_ai.ghost:
                blocked_exits.add((ghost.target_x, ghost.target_y))

        target_exit = None
        for exit_pos in exit_positions:
            if exit_pos not in blocked_exits:
                target_exit = exit_pos
                break

        if not target_exit:
            return None, 0.0

        # Рухаємося до виходу
        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        avoid_positions = {(g.grid_x, g.grid_y) for g in other_ghosts if g != ghost_ai.ghost}

        direction = bfs_next_step(ghost_pos, target_exit, walls,
                                  ghost_ai.game.map_width, ghost_ai.game.map_height,
                                  avoid_positions)

        if direction:
            distance = math.sqrt((ghost_pos[0] - target_exit[0]) ** 2 +
                                 (ghost_pos[1] - target_exit[1]) ** 2)
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
    """Спрощений ШІ з BFS"""

    def __init__(self, ghost, game, rules=None):
        self.ghost = ghost
        self.game = game
        self.rules = rules or []

    def log_decision(self, direction, strengths):
        """Логує рішення привида"""
        color_name = self.ghost.get_color_name()
        active_rules = []

        for rule_name, strength in strengths.items():
            if strength > 0.1:  # Логуємо тільки значимі правила
                active_rules.append(f"{rule_name}({strength:.1f})")

        if active_rules:
            logger.info(f"{color_name} ghost at ({self.ghost.grid_x}, {self.ghost.grid_y}) "
                        f"chose direction {direction} - Active rules: {', '.join(active_rules)}")

    def get_next_direction(self, walls, pacman, other_ghosts):
        direction_votes = {}
        rule_strengths = {}

        for rule in self.rules:
            if rule.enabled:
                direction, strength = rule.evaluate(self, walls, pacman, other_ghosts)
                if direction and strength > 0:
                    rule_name = rule.__class__.__name__
                    rule_strengths[rule_name] = strength

                    if direction not in direction_votes:
                        direction_votes[direction] = 0
                    direction_votes[direction] += strength

        if direction_votes:
            chosen_direction = max(direction_votes.items(), key=lambda x: x[1])[0]
            self.log_decision(chosen_direction, rule_strengths)
            return chosen_direction

        # Fallback до випадкового руху
        valid_dirs = self.get_valid_directions_no_collision(walls, other_ghosts)
        chosen_direction = random.choice(valid_dirs) if valid_dirs else (0, 0)
        self.log_decision(chosen_direction, {"WanderRule": 0.5})
        return chosen_direction

    def get_valid_directions_no_collision(self, walls, other_ghosts):
        """Повертає валідні напрямки без зіткнень"""
        valid_directions = []
        for direction in DIRECTIONS:
            next_x = (self.ghost.grid_x + direction[0]) % self.game.map_width
            next_y = (self.ghost.grid_y + direction[1]) % self.game.map_height

            if ((next_x, next_y) not in walls and
                    not any((g.grid_x, g.grid_y) == (next_x, next_y) or
                            (g.target_x, g.target_y) == (next_x, next_y)
                            for g in other_ghosts if g != self.ghost)):
                valid_directions.append(direction)

        return valid_directions

    def can_see_pacman(self, pacman, walls, view_distance=float('inf')):
        """Перевіряє видимість пакмена"""
        distance = math.sqrt((self.ghost.grid_x - pacman.grid_x) ** 2 +
                             (self.ghost.grid_y - pacman.grid_y) ** 2)
        return distance <= view_distance

    def has_line_of_sight(self, pacman, walls):
        """Перевіряє пряму видимість (спрощено)"""
        return True  # BFS вже враховує стіни


# Збереження старих класів для зворотної сумісності
RandomGhostAI = RuleBasedGhostAI
ChaserGhostAI = RuleBasedGhostAI
PatrolGhostAI = RuleBasedGhostAI
CooperativeGhostAI = RuleBasedGhostAI