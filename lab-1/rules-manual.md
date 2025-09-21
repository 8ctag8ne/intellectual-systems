# Система правил поведінки привидів у грі Pacman

## Загальна архітектура системи правил

Система правил побудована на принципі "голосування" - кожне правило оцінює ситуацію і пропонує напрямок руху з певною силою (вагою). Кінцевий напрямок вибирається на основі сумарної сили всіх активних правил.

### Клас RuleBasedGhostAI

Це основний клас ШІ, який:
1. Зберігає список активних правил для конкретного привида
2. Викликає метод `evaluate()` для кожного правила
3. Агрегує результати голосування правил
4. Вибирає напрямок з найвищою сумарною силою

```python
def get_next_direction(self, walls, pacman, other_ghosts):
    direction_votes = {}
    for rule in self.rules:
        if rule.enabled:
            direction, strength = rule.evaluate(self, walls, pacman, other_ghosts)
            if direction and strength > 0:
                if direction not in direction_votes:
                    direction_votes[direction] = 0
                direction_votes[direction] += strength
    # Вибираємо напрямок з найвищою сумарною силою
    return max(direction_votes.items(), key=lambda x: x[1])[0] if direction_votes else random_direction
```

## Детальний опис механізмів правил

### 1. EnhancedVisionRule (Покращене правило зору)

**Механізм роботи:**
1. **Пряма видимість**: Використовує алгоритм Брезенхема для перевірки лінії зору
```python
def has_line_of_sight(self, ghost_pos, pacman_pos, walls):
    # Реалізація алгоритму Брезенхема для перевірки прямої видимості
    # Перевіряє кожну клітинку між привидом і гравцем на наявність стін
```

2. **Детекція звуку**: Визначає рух гравця за рахунок перевірки його напрямку
3. **Мережева комунікація**: Використовує глобальний об'єкт `GhostNetwork` для обміну інформацією
4. **Пам'ять**: Зберігає останню відому позицію гравця з часом затухання впевненості

**Сила рекомендації** обчислюється на основі:
- Відстані до гравця
- Типу детекції (прямий зір > звук > мережа > пам'ять)
- Часу з моменту останнього виявлення

### 2. PredictPacmanRule (Передбачення руху)

**Механізм роботи:**
1. Аналізує поточний напрямок руху гравця
2. Екстраполює позицію на `prediction_steps` кроків вперед
3. Шукає шлях до передбаченої позиції за допомогою BFS

```python
pred_x = pacman.grid_x + pacman.direction[0] * self.prediction_steps
pred_y = pacman.grid_y + pacman.direction[1] * self.prediction_steps
pred_pos = (pred_x % ghost_ai.game.map_width, pred_y % ghost_ai.game.map_height)
```

### 3. FlankPacmanRule (Фланговий маневр)

**Що таке фланг:**
Фланг - це позиція збоку або позаду від напрямку руху гравця, яка дозволяє перехопити його.

**Механізм роботи:**
1. Визначає напрямок руху гравця
2. Обчислює перпендикулярні напрямки для створення флангових позицій
3. Обирає найкращу флангову позицію, доступну для досягнення

```python
if pacman.direction[0] != 0:  # горизонтальний рух
    flank_positions = [(pred_x, pred_y + 2), (pred_x, pred_y - 2)]
else:  # вертикальний рух
    flank_positions = [(pred_x + 2, pred_y), (pred_x - 2, pred_y)]
```

### 4. BlockEscapeRoute (Блокування виходів)

**Як визначаються виходи:**
1. Аналізуються всі сусідні клітинки позиції гравця
2. Визначаються валідні напрямки руху (без стін)
3. Визначаються вже заблоковані іншими привидами виходи

**Механізм роботи:**
1. Знаходить всі можливі шляхи втечі гравця
2. Визначає, які шляхи вже блокуються іншими привидами
3. Обирає найбільш загрозливий вільний шлях
4. Шукає маршрут для блокування цього шляху

```python
# Знаходимо можливі виходи пакмена
exit_positions = []
for direction in DIRECTIONS:
    exit_x = (pacman.grid_x + direction[0]) % ghost_ai.game.map_width
    exit_y = (pacman.grid_y + direction[1]) % ghost_ai.game.map_height
    if (exit_x, exit_y) not in walls:
        exit_positions.append((exit_x, exit_y))
```

### 5. AvoidOtherGhostsRule (Уникнення інших привидів)

**Механізм роботи:**
1. Обчислює відстань до кожного іншого привида
2. Якщо відстань менша за `min_distance`, додає штраф до напрямку
3. Шукає напрямок, який максимізує відстань до найближчих привидів

```python
for close_ghost in close_ghosts:
    dist = math.sqrt((close_ghost.grid_x - next_x) ** 2 +
                     (close_ghost.grid_y - next_y) ** 2)
    total_distance += dist
```

### 6. SmartPatrolRule (Розумне патрулювання)

**Механізм роботи:**
1. Рухається по заданих точках патрулювання
2. Адаптує пріоритет після кожного повного кола
3. Використовує BFS для знаходження шляху до наступної точки

### 7. IntelligentWanderRule (Розумне блукання)

**Механізм роботи:**
1. Зберігає історію позицій для уникнення циклів
2. Дає бонуси за дослідження нових територій
3. Штрафує за повернення назад
4. Використовує ваговий вибір з топ-2 напрямків

## BFS (Пошук в ширину) - ключовий алгоритм навігації

Більшість правил використовують BFS для знаходження шляху до цілі:

```python
def bfs_next_step(start_pos, target_pos, walls, map_width, map_height, avoid_positions=None):
    queue = deque([(start_pos, [])])  # (позиція, шлях_до_неї)
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
```

## Система комунікації GhostNetwork

Привиди можуть обмінюватися інформацією через глобальну мережу:

```python
class GhostNetwork:
    def share_pacman_sighting(self, ghost_pos, pacman_pos, timestamp, confidence=1.0):
        # Зберігає інформацію про позицію гравця
        
    def get_shared_pacman_info(self, ghost_pos, current_time):
        # Отримує інформацію від інших привидів
        # Впевненість зменшується з часом і відстанню
```

## Адаптивність системи

Система має кілька рівнів адаптивності:
1. **Динамічні пріоритети** - правила можуть змінювати свою силу в залежності від ситуації
2. **Адаптивне патрулювання** - зменшення пріоритету після кількох кругів
3. **Згасання пам'яті** - впевненість у знанні позиції гравця зменшується з часом
4. **Координація через мережу** - привиди діляться інформацією з урахуванням відстані

Ця архітектура дозволяє створювати складну поведінку шляхом комбінування відносно простих правил, кожне з яких відповідає за окремий аспект поведінки привидів.