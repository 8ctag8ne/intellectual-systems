# enhanced_ghost_ai.py - Покращена система з обмеженою видимістю
import random
import math
from collections import deque
import time

from src.constants import *
from src.ghost_ai import GhostRule


# Глобальна система комунікації привидів
class GhostNetwork:
    def __init__(self):
        self.shared_memory = {}
        self.communication_range = 4

    def share_pacman_sighting(self, ghost_pos, pacman_pos, timestamp, confidence=1.0):
        """Привид ділиться інформацією про пакмена"""
        self.shared_memory['pacman_pos'] = pacman_pos
        self.shared_memory['timestamp'] = timestamp
        self.shared_memory['confidence'] = confidence
        self.shared_memory['reporter_pos'] = ghost_pos

    def get_shared_pacman_info(self, ghost_pos, current_time):
        """Отримує інформацію про пакмена від інших привидів"""
        if 'timestamp' not in self.shared_memory:
            return None, 0

        # Перевіряємо чи не застаріла інформація
        age = current_time - self.shared_memory['timestamp']
        if age > 3.0:  # Інформація актуальна 3 секунди
            return None, 0

        # Перевіряємо дистанцію до привида-інформатора
        reporter_pos = self.shared_memory.get('reporter_pos', (0, 0))
        distance = math.sqrt((ghost_pos[0] - reporter_pos[0]) ** 2 + (ghost_pos[1] - reporter_pos[1]) ** 2)

        if distance > self.communication_range:
            return None, 0

        # Зменшуємо впевненість з часом і дистанцією
        confidence = self.shared_memory['confidence'] * (1 - age / 3.0) * (1 - distance / self.communication_range)
        return self.shared_memory['pacman_pos'], max(0, confidence)


# Глобальна мережа
ghost_network = GhostNetwork()


class EnhancedVisionRule(GhostRule):
    """Покращене правило зору з різними типами детекції"""

    def __init__(self, sight_radius=5, sound_radius=2, memory_duration=2.0, priority=3.0):
        super().__init__(priority)
        self.sight_radius = sight_radius
        self.sound_radius = sound_radius
        self.memory_duration = memory_duration
        self.last_known_pacman_pos = None
        self.last_seen_time = 0

    def detect_pacman(self, ghost_ai, pacman, walls, current_time):
        """Комплексна детекція пакмена"""
        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        pacman_pos = (pacman.grid_x, pacman.grid_y)
        distance = math.sqrt((ghost_pos[0] - pacman_pos[0]) ** 2 + (ghost_pos[1] - pacman_pos[1]) ** 2)

        detected = False
        detection_confidence = 0.0
        detection_method = "none"

        # 1. Пряма видимість (найсильніше)
        if distance <= self.sight_radius and self.has_line_of_sight(ghost_pos, pacman_pos, walls):
            detected = True
            detection_confidence = min(1.0, self.sight_radius / (distance + 0.1))
            detection_method = "sight"

        # 2. Детекція звуку (пакмен рухається)
        elif distance <= self.sound_radius and pacman.direction != (0, 0):
            detected = True
            detection_confidence = 0.6 * (self.sound_radius / (distance + 0.1))
            detection_method = "sound"

        # 3. Інформація від інших привидів
        if not detected:
            shared_pos, shared_confidence = ghost_network.get_shared_pacman_info(ghost_pos, current_time)
            if shared_pos and shared_confidence > 0.2:
                pacman_pos = shared_pos
                detection_confidence = shared_confidence * 0.8  # Менша впевненість для чужої інформації
                detected = True
                detection_method = "network"

        # 4. Пам'ять (найслабше)
        if not detected and self.last_known_pacman_pos:
            memory_age = current_time - self.last_seen_time
            if memory_age < self.memory_duration:
                pacman_pos = self.last_known_pacman_pos
                detection_confidence = 0.3 * (1 - memory_age / self.memory_duration)
                detected = True
                detection_method = "memory"

        # Оновлюємо пам'ять і мережу
        if detection_method in ["sight", "sound"]:
            self.last_known_pacman_pos = pacman_pos
            self.last_seen_time = current_time

            # Ділимося інформацією з іншими привидами
            ghost_network.share_pacman_sighting(ghost_pos, pacman_pos, current_time, detection_confidence)

        return detected, pacman_pos, detection_confidence, detection_method

    def has_line_of_sight(self, ghost_pos, pacman_pos, walls):
        """Перевіряє пряму видимість"""
        x0, y0 = ghost_pos
        x1, y1 = pacman_pos

        if ghost_pos == pacman_pos:
            return True

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0
        while True:
            if (x, y) != ghost_pos and (x, y) != pacman_pos and (x, y) in walls:
                return False

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return True

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        current_time = time.time()
        detected, target_pos, confidence, method = self.detect_pacman(ghost_ai, pacman, walls, current_time)

        if not detected or confidence < 0.1:
            return None, 0.0

        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        avoid_positions = {(g.grid_x, g.grid_y) for g in other_ghosts if g != ghost_ai.ghost}

        # Використовуємо BFS для пошуку шляху
        direction = bfs_next_step(ghost_pos, target_pos, walls,
                                  ghost_ai.game.map_width, ghost_ai.game.map_height,
                                  avoid_positions)

        if direction:
            # Сила залежить від впевненості в детекції
            strength = confidence * self.priority

            # Бонус за прямий зір
            if method == "sight":
                strength *= 1.2
            elif method == "sound":
                strength *= 1.0
            elif method == "network":
                strength *= 0.8
            else:  # memory
                strength *= 0.6

            return direction, strength

        return None, 0.0


class SmartPatrolRule(GhostRule):
    """Розумне патрулювання з адаптацією"""

    def __init__(self, patrol_points=None, priority=1.5):
        super().__init__(priority)
        self.patrol_points = patrol_points or []
        self.current_target = 0
        self.patrol_completion_count = 0
        self.adaptive_priority = priority

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        if not self.patrol_points:
            return None, 0.0

        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        target_pos = self.patrol_points[self.current_target]

        # Якщо досягли цілі
        if ghost_pos == target_pos:
            self.current_target = (self.current_target + 1) % len(self.patrol_points)
            if self.current_target == 0:
                self.patrol_completion_count += 1
                # Зменшуємо пріоритет патрулювання після кількох кругів
                self.adaptive_priority = max(0.5, self.priority - self.patrol_completion_count * 0.1)

            target_pos = self.patrol_points[self.current_target]

        avoid_positions = {(g.grid_x, g.grid_y) for g in other_ghosts if g != ghost_ai.ghost}

        direction = bfs_next_step(ghost_pos, target_pos, walls,
                                  ghost_ai.game.map_width, ghost_ai.game.map_height,
                                  avoid_positions)

        return (direction, self.adaptive_priority) if direction else (None, 0.0)


class IntelligentWanderRule(GhostRule):
    """Розумне блукання з уникненням циклів"""

    def __init__(self, priority=0.8):
        super().__init__(priority)
        self.position_history = deque(maxlen=8)
        self.direction_history = deque(maxlen=4)
        self.exploration_bonus = {}  # Бонуси за відвідування нових місць

    def evaluate(self, ghost_ai, walls, pacman, other_ghosts):
        ghost_pos = (ghost_ai.ghost.grid_x, ghost_ai.ghost.grid_y)
        current_time = time.time()

        # Додаємо поточну позицію до історії
        self.position_history.append(ghost_pos)

        valid_dirs = []
        for direction in DIRECTIONS:
            next_x = (ghost_pos[0] + direction[0]) % ghost_ai.game.map_width
            next_y = (ghost_pos[1] + direction[1]) % ghost_ai.game.map_height
            next_pos = (next_x, next_y)

            if next_pos not in walls:
                # Перевіряємо зіткнення з іншими привидами
                collision = False
                for ghost in other_ghosts:
                    if ghost != ghost_ai.ghost:
                        if (ghost.grid_x, ghost.grid_y) == next_pos or (ghost.target_x, ghost.target_y) == next_pos:
                            collision = True
                            break

                if not collision:
                    valid_dirs.append((direction, next_pos))

        if not valid_dirs:
            return None, 0.0

        # Оцінюємо кожен напрямок
        scored_dirs = []
        for direction, next_pos in valid_dirs:
            score = 0.0

            # Уникаємо недавно відвіданих місць
            recent_visits = sum(1 for pos in self.position_history if pos == next_pos)
            score -= recent_visits * 0.3

            # Уникаємо повернення назад
            if len(self.direction_history) > 0:
                opposite = (-self.direction_history[-1][0], -self.direction_history[-1][1])
                if direction == opposite:
                    score -= 0.4

            # Бонус за дослідження нових областей
            if next_pos not in self.exploration_bonus:
                self.exploration_bonus[next_pos] = current_time
                score += 0.3
            else:
                # Бонус зменшується з часом
                age = current_time - self.exploration_bonus[next_pos]
                if age > 10:  # Забуваємо старі області через 10 секунд
                    score += 0.2

            scored_dirs.append((direction, score))

        # Вибираємо найкращий напрямок з елементом випадковості
        scored_dirs.sort(key=lambda x: x[1], reverse=True)

        # Вибираємо з топ варіантів для збереження непередбачуваності
        top_choices = scored_dirs[:2]
        if len(top_choices) >= 2:
            chosen_direction = random.choices(top_choices, weights=[2, 1])[0][0]
        elif len(top_choices) == 1:
            chosen_direction = top_choices[0][0]
        else:
            chosen_direction = random.choice([d[0] for d in scored_dirs])

        self.direction_history.append(chosen_direction)
        return chosen_direction, self.priority

        return random.choice([d[0] for d in scored_dirs]), self.priority


# BFS функція (без змін)
def bfs_next_step(start_pos, target_pos, walls, map_width, map_height, avoid_positions=None):
    """BFS пошук наступного кроку до цілі"""
    if start_pos == target_pos:
        return None

    avoid_positions = avoid_positions or set()
    queue = deque([(start_pos, [])])
    visited = {start_pos}

    while queue:
        (x, y), path = queue.popleft()

        for direction in DIRECTIONS:
            next_x = (x + direction[0]) % map_width
            next_y = (y + direction[1]) % map_height
            next_pos = (next_x, next_y)

            if next_pos in visited or next_pos in walls or next_pos in avoid_positions:
                continue

            new_path = path + [direction]

            if next_pos == target_pos:
                return new_path[0] if new_path else None

            queue.append((next_pos, new_path))
            visited.add(next_pos)

            if len(new_path) > 15:
                break

    return None