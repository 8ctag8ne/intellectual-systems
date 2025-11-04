# config.py - Конфігурація проєкту

# Розміри
GRID_SIZE = 150          # Розмір поля (150x150)
CELL_SIZE = 5          # Розмір клітинки в пікселях
VISION_RADIUS = 5       # Радіус огляду змійки

# Гра
INITIAL_SNAKE_LENGTH = 6
ENERGY = 40             # Початкова енергія
MIN_LENGTH = 4          # Мінімальна довжина до смерті

# Геном
GENOME_SIZE = 120 * 2 * 4  # 960
WEIGHT_RANGE = 99       # Ваги від -99 до 99

# Генетичний алгоритм
POPULATION_SIZE = 128    # Змійок одночасно на полі
SURVIVORS = 32           # Скільки найкращих виживають
MAX_STEPS = 2000        # Максимум кроків для одного покоління
MUTATION_RATE = 0.05     # 5% ваг мутують
MUTATION_SIGMA = 15     # Сила мутації
ELITE_SIZE = 4          # Топ-4 переходять без змін
TOURNAMENT_SIZE = 16     # Розмір турніру для селекції

# Їжа
FOOD_COUNT = 1000         # Кількість їжі на полі одночасно

# Візуалізація
VISUALIZE = True
FPS = 60                # Швидкість відображення
HEADLESS_GENERATIONS = 200  # Скільки поколінь тренувати в headless

# Кольори (RGB)
COLOR_BACKGROUND = (20, 20, 20)
COLOR_GRID = (40, 40, 40)
COLOR_SNAKE = (0, 255, 0)
COLOR_FOOD = (255, 50, 50)
COLOR_OBSTACLE = (100, 100, 100)