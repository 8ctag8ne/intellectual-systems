# genome.py - Геном змійки

import numpy as np
from config import WEIGHT_RANGE, VISION_RADIUS


class Genome:
    """
    Клас що представляє геном змійки - набір ваг для прийняття рішень
    
    Структура ваг: (120, 2, 4)
    - 120 позицій в полі огляду (11x11 - 1 центральна клітинка)
    - 2 типи датчиків: 0=їжа, 1=перешкода
    - 4 напрямки: 0=вгору, 1=вправо, 2=вниз, 3=вліво
    """
    
    def __init__(self, weights=None):
        """
        Ініціалізація генома
        
        Args:
            weights: numpy array (120, 2, 4) або None для випадкової ініціалізації
        """
        if weights is None:
            # Ініціалізувати випадково цілими числами з {-1, 0, 1}
            vision_size = (VISION_RADIUS * 2 + 1) ** 2 - 1  # 11*11 - 1 = 120
            self.weights = np.random.randint(-1, 2, size=(vision_size, 2, 4))
            
            # Додати від'ємні ваги для сусідніх перешкод
            self._add_obstacle_penalties()
        else:
            self.weights = weights.copy()
    
    def _add_obstacle_penalties(self):
        """
        Додає від'ємні ваги для напрямків, що ведуть до перешкод у сусідніх клітинках
        Використовує прямі формули для обчислення індексів
        """
        r = VISION_RADIUS  # 5
        size = 2 * r + 1   # 11
        
        # Обчислити індекси сусідніх клітинок за формулами
        top_index = (r - 1) * size + (r + 1) - 1
        left_index = r * size + r - 1
        right_index = r * size + r
        bottom_index = (r + 1) * size + (r + 1) - 1 - 1
        
        # Відповідність індексів напрямкам:
        # 0: вгору, 1: вправо, 2: вниз, 3: вліво
        direction_indices = [top_index, right_index, bottom_index, left_index]
        
        # Для кожного напрямку встановити вагу -5 для датчика перешкод (індекс 1)
        for direction, neighbor_idx in enumerate(direction_indices):
            if neighbor_idx < len(self.weights):
                self.weights[neighbor_idx, 1, direction] = -7
    
    def mutate(self, mutation_rate, sigma):
        """
        Мутує геном додаванням гаусівського шуму
        
        Args:
            mutation_rate: ймовірність мутації кожної ваги (0.0-1.0)
            sigma: стандартне відхилення гаусівського шуму
        """
        # Створити маску для мутації
        mutation_mask = np.random.random(self.weights.shape) < mutation_rate
        
        # Додати гаусівський шуму до обраних ваг
        noise = np.random.normal(0, sigma, self.weights.shape)
        self.weights = self.weights + (noise * mutation_mask).astype(int)
        
        # Обрізати до діапазону [-WEIGHT_RANGE, WEIGHT_RANGE]
        self.weights = np.clip(self.weights, -WEIGHT_RANGE, WEIGHT_RANGE)
    
    def crossover(self, other_genome, alpha=None):
        """
        Схрещування з іншим геномом
        
        Args:
            other_genome: інший об'єкт Genome
            alpha: коефіцієнт змішування (якщо None, буде випадковим від 0.3 до 0.7)
        
        Returns:
            Новий об'єкт Genome
        """
        if alpha is None:
            alpha = np.random.uniform(0.3, 0.7)
        
        # Змішати ваги
        new_weights = alpha * self.weights + (1 - alpha) * other_genome.weights
        
        # Округлити до цілих чисел
        new_weights = np.round(new_weights).astype(int)
        
        return Genome(new_weights)
    
    def to_flat(self):
        """
        Перетворює геном в одновимірний масив для збереження
        
        Returns:
            numpy array з 960 елементами
        """
        return self.weights.flatten()
    
    @staticmethod
    def from_flat(flat_array):
        """
        Відновлює геном з одновимірного масиву
        
        Args:
            flat_array: numpy array з 960 елементами
        
        Returns:
            Новий об'єкт Genome
        """
        vision_size = (VISION_RADIUS * 2 + 1) ** 2 - 1  # 120
        weights = flat_array.reshape((vision_size, 2, 4))
        return Genome(weights)