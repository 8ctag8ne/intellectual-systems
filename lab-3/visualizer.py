# visualizer.py - Візуалізація гри

import pygame
from config import (
    GRID_SIZE, CELL_SIZE, FPS,
    COLOR_BACKGROUND, COLOR_GRID, COLOR_SNAKE, COLOR_FOOD, COLOR_OBSTACLE
)


class Visualizer:
    """Клас для відображення гри через pygame"""
    
    def __init__(self):
        """Ініціалізація pygame та вікна"""
        pygame.init()
        
        # Розміри вікна
        self.grid_width = GRID_SIZE * CELL_SIZE
        self.grid_height = GRID_SIZE * CELL_SIZE
        self.info_height = 100
        
        self.width = self.grid_width
        self.height = self.grid_height + self.info_height
        
        # Створити вікно
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Генетичний алгоритм для змійки")
        
        # Створити шрифт
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        
        # Годинник для FPS
        self.clock = pygame.time.Clock()
    
    def draw_grid(self):
        """Намалювати сітку"""
        for x in range(0, self.grid_width, CELL_SIZE):
            pygame.draw.line(
                self.screen, 
                COLOR_GRID, 
                (x, 0), 
                (x, self.grid_height)
            )
        
        for y in range(0, self.grid_height, CELL_SIZE):
            pygame.draw.line(
                self.screen, 
                COLOR_GRID, 
                (0, y), 
                (self.grid_width, y)
            )
    
    def draw_environment(self, environment, generation=0, best_fitness=0, title = ""):
        """
        Намалювати середовище
        
        Args:
            environment: об'єкт Environment
            generation: номер покоління
            best_fitness: найкращий fitness за всю історію
        """
        # Очистити екран
        self.screen.fill(COLOR_BACKGROUND)
        
        # Намалювати сітку
        self.draw_grid()

        
        # Намалювати перешкоди (включаючи бар'єр)
        for obs_x, obs_y in environment.obstacles:
            if 0 <= obs_x < GRID_SIZE and 0 <= obs_y < GRID_SIZE:
                rect = pygame.Rect(
                    obs_x * CELL_SIZE,
                    obs_y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                # Бар'єр на краях - темніший колір
                if obs_x == 0 or obs_x == GRID_SIZE - 1 or obs_y == 0 or obs_y == GRID_SIZE - 1:
                    color = (80, 80, 80)  # Темніший для бар'єру
                else:
                    color = COLOR_OBSTACLE
                pygame.draw.rect(self.screen, color, rect)
        
        # Намалювати їжу
        for food in environment.foods:
            rect = pygame.Rect(
                food.x * CELL_SIZE,
                food.y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_FOOD, rect)
        
        # Намалювати змійок
        for snake in environment.snakes:
            if not snake.alive:
                continue
            
            # Намалювати тіло (використовуємо поточну довжину body, а не self.length)
            for i, (seg_x, seg_y) in enumerate(snake.body):
                rect = pygame.Rect(
                    seg_x * CELL_SIZE,
                    seg_y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                if i == 0:
                    # Голова - яскравіший зелений
                    color = (0, 255, 100)
                else:
                    # Тіло - звичайний зелений
                    color = COLOR_SNAKE
                
                pygame.draw.rect(self.screen, color, rect)
            
            # Намалювати ID змійки біля голови
            head_x, head_y = snake.body[0]
            id_text = self.small_font.render(
                str(snake.id), 
                True, 
                (255, 255, 255)
            )
            self.screen.blit(
                id_text,
                (head_x * CELL_SIZE + 2, head_y * CELL_SIZE + 2)
            )
        
        # Намалювати інформаційну панель внизу
        info_y = self.grid_height
        
        # Фон для інфо-панелі
        info_rect = pygame.Rect(0, info_y, self.width, self.info_height)
        pygame.draw.rect(self.screen, (30, 30, 30), info_rect)
        
        # Текст з інформацією
        alive_count = environment.get_alive_count()
        
        # Рядок 1: Покоління та найкращий fitness
        gen_text = self.font.render(
            f"Generation: {generation}  |  Best Fitness: {best_fitness:.0f}",
            True,
            (255, 255, 255)
        )
        self.screen.blit(gen_text, (10, info_y + 10))
        
        # Рядок 2: Кількість живих змійок та їжі
        alive_text = self.font.render(
            f"Alive: {alive_count} / {len(environment.snakes)}  |  Food: {len(environment.foods)}",
            True,
            (0, 255, 100) if alive_count > 0 else (255, 100, 100)
        )
        self.screen.blit(alive_text, (10, info_y + 40))
        
        # Якщо є живі змійки, показати статистику найкращої
        if alive_count > 0:
            best_snake = max(
                [s for s in environment.snakes if s.alive],
                key=lambda s: s.get_fitness()
            )
            
            # Використовуємо len(body) для поточної довжини
            current_length = len(best_snake.body)
            
            stats_text = self.font.render(
                f"Best: Snake #{best_snake.id}  Length: {current_length}  "
                f"Food: {best_snake.food_eaten}  Steps: {best_snake.steps}",
                True,
                (200, 200, 200)
            )
            self.screen.blit(stats_text, (10, info_y + 70))
        
        # Оновити дисплей
        pygame.display.flip()
        
        # Контроль FPS
        self.clock.tick(FPS)
    
    def handle_events(self):
        """
        Обробити події pygame
        
        Returns:
            bool: False якщо треба закрити вікно, інакше True
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Додаткові клавіші для контролю
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Пробіл для паузи (можна додати в майбутньому)
                # if event.key == pygame.K_SPACE:
                #     pass
        
        return True
    
    def close(self):
        """Закрити pygame"""
        pygame.quit()