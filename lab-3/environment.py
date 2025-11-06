# environment.py - Середовище гри

import numpy as np
from food import Food


class Environment:
    """Клас що управляє ігровим полем, їжею та перешкодами"""
    
    def __init__(self, width, height):
        """
        Ініціалізація середовища
        
        Args:
            width: ширина поля
            height: висота поля
        """
        self.width = width
        self.height = height
        self.snakes = []
        self.foods = []
        self.obstacles = []
        
        # Створити бар'єр навколо поля
        self._create_barrier()
        
        # Сітка для швидкої перевірки зайнятості
        # 0 = пусто, 1 = їжа, 2 = перешкода, 3 = тіло змійки
        self.grid = np.zeros((height, width), dtype=int)
    
    def _create_barrier(self):
        """Створити бар'єр навколо поля"""
        # Верхня та нижня стіни
        for x in range(self.width):
            self.obstacles.append((x, 0))
            self.obstacles.append((x, self.height - 1))
        
        # Ліва та права стіни
        for y in range(self.height):
            self.obstacles.append((0, y))
            self.obstacles.append((self.width - 1, y))
    
    def add_snake(self, snake):
        """
        Додати змійку в середовище
        
        Args:
            snake: об'єкт Snake
        """
        self.snakes.append(snake)
    
    def spawn_food(self, count=1):
        """
        Створити їжу на випадкових вільних клітинках
        
        Args:
            count: кількість їжі для створення
        """
        spawned = 0
        attempts = 0
        max_attempts = count * 100  # Уникнення нескінченного циклу
        
        while spawned < count and attempts < max_attempts:
            attempts += 1
            x = np.random.randint(1, self.width - 1)  # Уникаємо бар'єру (0 та width-1)
            y = np.random.randint(1, self.height - 1)  # Уникаємо бар'єру (0 та height-1)
            
            # Перевірити чи клітинка вільна (не бар'єр, не їжа, не змійка)
            if self.grid[y, x] == 0:
                self.foods.append(Food(x, y))
                spawned += 1
    
    def update_grid(self):
        """Оновити сітку з поточними об'єктами"""
        # Очистити сітку
        self.grid.fill(0)
        
        # Позначити перешкоди
        for obs_x, obs_y in self.obstacles:
            if 0 <= obs_x < self.width and 0 <= obs_y < self.height:
                self.grid[obs_y, obs_x] = 2
        
        # Позначити їжу
        for food in self.foods:
            if 0 <= food.x < self.width and 0 <= food.y < self.height:
                self.grid[food.y, food.x] = 1
        
        # Позначити тіла змійок
        for snake in self.snakes:
            if snake.alive:
                for seg_x, seg_y in snake.body:
                    if 0 <= seg_x < self.width and 0 <= seg_y < self.height:
                        self.grid[seg_y, seg_x] = 3
    
    def is_food(self, x, y):
        """
        Перевірити чи є їжа на координатах
        
        Args:
            x, y: координати
        
        Returns:
            bool: True якщо є їжа
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x] == 1
        return False
    
    def is_obstacle(self, x, y):
        """
        Перевірити чи є перешкода на координатах
        
        Args:
            x, y: координати
        
        Returns:
            bool: True якщо є перешкода (включаючи межі, перешкоди, тіла змійок)
        """
        # Межі поля
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        
        # Перешкода або тіло змійки
        return self.grid[y, x] in [2, 3]
    
    def step(self):
        """Виконати один крок симуляції"""
        # Оновити сітку перед рухом
        self.update_grid()
        
        # Рухати кожну живу змійку
        for snake in self.snakes:
            if not snake.alive:
                continue
            
            # Отримати поле зору та прийняти рішення
            vision = snake.get_vision(self)
            snake.decide_direction(vision)
            
            # Рух
            snake.move()
            
            # Перевірити чи з'їла їжу
            if snake.alive:
                head_x, head_y = snake.body[0]
                
                # Шукаємо їжу на координатах голови
                for food in self.foods[:]:  # Копія списку для безпечного видалення
                    if food.x == head_x and food.y == head_y:
                        snake.eat()
                        self.foods.remove(food)
                        self.spawn_food(1)
                        break
            
            # Перевірити колізії
            if snake.alive:
                snake.check_collision(self)
        
        # Фінальне оновлення сітки
        self.update_grid()
    
    def get_alive_count(self):
        """
        Отримати кількість живих змійок
        
        Returns:
            int: кількість живих змійок
        """
        return sum(1 for snake in self.snakes if snake.alive)
    
    def reset(self):
        """Очистити середовище"""
        self.snakes.clear()
        self.foods.clear()
        self.grid.fill(0)