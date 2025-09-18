# constants.py (оновлений)
# Розміри екрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Розміри клітинок
CELL_SIZE = 25

# Кольори
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)

# Швидкості (тепер це затримки між кроками в секундах)
PACMAN_MOVE_DELAY = 0.2
GHOST_MOVE_DELAY = 0.21

PACMAN_SPEED = 4.0
GHOST_SPEED = 3.7

# ASCII символи для карти
WALL = '#'
DOT = '.'
PACMAN_START = 'P'
GHOST_START = 'G'
EMPTY = ' '
BIG_DOT = 'O'

# Стани гри
GAME_PLAYING = "playing"
GAME_PAUSED = "paused"
GAME_WON = "won"
GAME_LOST = "lost"

# Напрямки
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Вибрана карта
MAP = "classic_adapted_2.txt"

# ШІ константи
AI_DECISION_DELAY = 0.05  # Затримка між рішеннями ШІ в секундах
DEFAULT_VIEW_DISTANCE = 5  # Стандартна дальність видимості
MAX_VIEW_DISTANCE = float('inf')  # Необмежена видимість