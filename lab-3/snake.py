# snake.py - Змійка з геномом

import numpy as np
from config import INITIAL_SNAKE_LENGTH, ENERGY, MIN_LENGTH


class Snake:
    """Клас змійки що використовує геном для прийняття рішень"""
    
    def __init__(self, start_x, start_y, genome, snake_id):
        """
        Ініціалізація змійки
        
        Args:
            start_x: початкова координата X
            start_y: початкова координата Y
            genome: об'єкт Genome
            snake_id: унікальний ідентифікатор
        """
        self.genome = genome
        self.id = snake_id
        
        # Створити тіло змійки (голова перша)
        self.body = [(start_x, start_y + i) for i in range(INITIAL_SNAKE_LENGTH)]
        
        # Випадковий початковий напрямок (0=вгору, 1=вправо, 2=вниз, 3=вліво)
        self.direction = np.random.randint(0, 4)
        
        # Статистика
        self.energy = ENERGY
        self.length = INITIAL_SNAKE_LENGTH
        self.food_eaten = 0
        self.alive = True
        self.steps = 0
    
    def get_vision(self, environment):
        """
        Отримати поле зору змійки
        
        Args:
            environment: об'єкт Environment
        
        Returns:
            numpy array (11, 11, 2) - що бачить змійка
            [y][x][0] = їжа (1 якщо є, 0 якщо немає)
            [y][x][1] = перешкода (1 якщо є, 0 якщо немає)
        """
        from config import VISION_RADIUS
        
        vision = np.zeros((VISION_RADIUS * 2 + 1, VISION_RADIUS * 2 + 1, 2))
        head_x, head_y = self.body[0]
        
        # Пройтись по всіх клітинках в радіусі огляду
        for dy in range(-VISION_RADIUS, VISION_RADIUS + 1):
            for dx in range(-VISION_RADIUS, VISION_RADIUS + 1):
                # Пропустити центральну клітинку (голова змійки)
                if dy == 0 and dx == 0:
                    continue
                
                # Координати в полі
                x = head_x + dx
                y = head_y + dy
                
                # Координати в масиві vision (зміщені на VISION_RADIUS)
                vis_y = dy + VISION_RADIUS
                vis_x = dx + VISION_RADIUS
                
                # Перевірити їжу
                if environment.is_food(x, y):
                    vision[vis_y, vis_x, 0] = 1
                
                # Перевірити перешкоду
                if environment.is_obstacle(x, y):
                    vision[vis_y, vis_x, 1] = 1
        
        return vision
    
    def decide_direction(self, vision):
        """
        Прийняти рішення про напрямок руху на основі генома
        
        Args:
            vision: numpy array (11, 11, 2) з поля зору
        """
        from config import VISION_RADIUS
        
        # Ініціалізувати виходи для кожного напрямку
        outputs = np.zeros(4)  # [вгору, вправо, вниз, вліво]
        
        # Індекс позиції в геномі (пропускаємо центральну клітинку)
        position_idx = 0
        
        # Пройтись по всіх клітинках огляду
        for vis_y in range(VISION_RADIUS * 2 + 1):
            for vis_x in range(VISION_RADIUS * 2 + 1):
                # Пропустити центральну клітинку
                if vis_y == VISION_RADIUS and vis_x == VISION_RADIUS:
                    continue
                
                # Для їжі
                if vision[vis_y, vis_x, 0] == 1:
                    outputs += self.genome.weights[position_idx, 0, :]
                
                # Для перешкоди
                if vision[vis_y, vis_x, 1] == 1:
                    outputs += self.genome.weights[position_idx, 1, :]
                
                position_idx += 1
        
        # Не можна рухатися в протилежний напрямок
        opposite_direction = (self.direction + 2) % 4
        outputs[opposite_direction] = -np.inf
        
        # Обрати напрямок з максимальним значенням
        max_output = np.max(outputs)
        
        # Якщо кілька максимумів - випадковий вибір серед них
        best_directions = np.where(outputs == max_output)[0]
        self.direction = np.random.choice(best_directions)
    
    def move(self):
        """Рух змійки на один крок"""
        # Зменшити енергію
        self.energy -= 1
        
        # Якщо енергія закінчилась, зменшити довжину
        if self.energy <= 0:
            self.length -= 1
            self.energy = ENERGY
        
        # Якщо довжина менша мінімальної - змійка помирає
        if self.length < MIN_LENGTH:
            self.alive = False
            return
        
        # Обчислити нову позицію голови
        head_x, head_y = self.body[0]
        
        if self.direction == 0:  # Вгору
            new_head = (head_x, head_y - 1)
        elif self.direction == 1:  # Вправо
            new_head = (head_x + 1, head_y)
        elif self.direction == 2:  # Вниз
            new_head = (head_x, head_y + 1)
        else:  # Вліво (3)
            new_head = (head_x - 1, head_y)
        
        # Додати нову голову
        self.body.insert(0, new_head)
        
        # Видалити хвіст якщо тіло довше ніж потрібно
        while len(self.body) > self.length:
            self.body.pop()
        
        self.steps += 1
    
    def eat(self):
        """Змійка з'їла їжу"""
        self.length += 1
        self.energy = ENERGY
        self.food_eaten += 1
    
    def check_collision(self, environment):
        """
        Перевірити чи зіткнулась змійка
        
        Args:
            environment: об'єкт Environment
        """
        head_x, head_y = self.body[0]
        
        # Перевірка меж поля
        if head_x < 0 or head_x >= environment.width or head_y < 0 or head_y >= environment.height:
            self.alive = False
            return
        
        # Перевірка зіткнення з перешкодами
        if (head_x, head_y) in environment.obstacles:
            self.alive = False
            return
        
        # Перевірка зіткнення з власним тілом (крім голови)
        if (head_x, head_y) in self.body[1:]:
            self.alive = False
            return
        
        # Перевірка зіткнення з іншими змійками
        for other_snake in environment.snakes:
            if other_snake.id != self.id and other_snake.alive:
                if (head_x, head_y) in other_snake.body:
                    self.alive = False
                    return
    
    def get_fitness(self):
        """
        Обчислити фітнес-функцію змійки
        
        Returns:
            float: значення фітнесу (базується на ПОТОЧНІЙ довжині, не максимальній)
        """
        # Використовуємо поточну довжину (len(body)), а не self.length
        # Це важливо, бо змійка може зменшуватись
        current_length = len(self.body)
        return current_length ** 2 *10 + self.food_eaten * 50