# genetic_algorithm.py - Генетичний алгоритм

import numpy as np
from genome import Genome
from snake import Snake
from environment import Environment
from config import (
    POPULATION_SIZE, MAX_STEPS, MUTATION_RATE, MUTATION_SIGMA,
    ELITE_SIZE, TOURNAMENT_SIZE, GRID_SIZE, SURVIVORS, FOOD_COUNT
)


class GeneticAlgorithm:
    """Клас що керує еволюцією популяції змійок"""
    
    def __init__(self, population_size=POPULATION_SIZE):
        """
        Ініціалізація генетичного алгоритму
        
        Args:
            population_size: розмір популяції
        """
        self.population_size = population_size
        self.population = [Genome() for _ in range(population_size)]
        self.generation = 0
        self.best_genome = None
        self.best_fitness = -np.inf
        self.stats_history = []
    
    def evaluate_population(self):
        """
        Оцінити всю популяцію - всі змійки грають одночасно
        
        Returns:
            list: список fitness для кожного генома
        """
        # Створити середовище
        env = Environment(GRID_SIZE, GRID_SIZE)
        
        # Створити всі змійки одночасно на полі
        # Розмістити їх рівномірно по полю, уникаючи бар'єру
        grid_positions = []
        grid_step = (GRID_SIZE - 4) // int(np.sqrt(POPULATION_SIZE))
        
        for i in range(int(np.sqrt(POPULATION_SIZE)) + 1):
            for j in range(int(np.sqrt(POPULATION_SIZE)) + 1):
                if len(grid_positions) < POPULATION_SIZE:
                    x = 2 + j * grid_step + np.random.randint(-2, 3)
                    y = 2 + i * grid_step + np.random.randint(-2, 3)
                    # Переконатися що не на бар'єрі
                    x = max(2, min(GRID_SIZE - 3, x))
                    y = max(2, min(GRID_SIZE - 3, y))
                    grid_positions.append((x, y))
        
        # Створити змійок
        for i, genome in enumerate(self.population):
            x, y = grid_positions[i]
            snake = Snake(x, y, genome, snake_id=i + 1)
            env.add_snake(snake)
        
        # Створити їжу (фіксована кількість)
        env.spawn_food(FOOD_COUNT)
        
        # Запустити симуляцію
        step = 0
        while env.get_alive_count() > 0 and step < MAX_STEPS:
            env.step()
            step += 1
        
        # Зібрати fitness
        fitnesses = [snake.get_fitness() for snake in env.snakes]
        
        # Зібрати додаткову статистику (поточна довжина, а не максимальна)
        max_length = max(len(snake.body) for snake in env.snakes)
        max_food = max(snake.food_eaten for snake in env.snakes)
        
        return fitnesses, max_length, max_food
    
    def tournament_selection(self, fitnesses):
        """
        Турнірна селекція
        
        Args:
            fitnesses: список fitness значень
        
        Returns:
            int: індекс обраної особини
        """
        # Вибрати випадкові індекси для турніру
        tournament_indices = np.random.choice(
            len(fitnesses), 
            size=TOURNAMENT_SIZE, 
            replace=False
        )
        
        # Знайти найкращого в турнірі
        tournament_fitnesses = [fitnesses[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitnesses)]
        
        return winner_idx
    
    def evolve(self):
        """Виконати один цикл еволюції"""
        # Оцінити популяцію (всі 16 змійок одночасно)
        fitnesses, max_length, max_food = self.evaluate_population()
        
        # Зібрати статистику
        max_fitness = max(fitnesses)
        avg_fitness = np.mean(fitnesses)
        
        # Оновити найкращий геном
        if max_fitness > self.best_fitness:
            best_idx = np.argmax(fitnesses)
            self.best_genome = Genome(self.population[best_idx].weights.copy())
            self.best_fitness = max_fitness
        
        # Зберегти статистику
        stats = {
            'generation': self.generation,
            'max_fitness': max_fitness,
            'avg_fitness': avg_fitness,
            'best_overall_fitness': self.best_fitness,
            'max_length': max_length,
            'max_food': max_food
        }
        self.stats_history.append(stats)
        
        # НОВА ЛОГІКА: Відібрати 8 найкращих
        sorted_indices = np.argsort(fitnesses)[::-1]  # Від найкращих до найгірших
        survivors_indices = sorted_indices[:SURVIVORS]  # Топ-8
        
        # Створити нову популяцію з 16 особин
        new_population = []
        
        # 1. Еліта: топ-2 переходять без змін
        for i in range(ELITE_SIZE):
            elite_genome = Genome(self.population[survivors_indices[i]].weights.copy())
            new_population.append(elite_genome)
        
        # 2. Решта 14 особин - схрещування та мутація з 8 виживших
        while len(new_population) < POPULATION_SIZE:
            # Вибрати двох батьків випадково з виживших (топ-8)
            parent1_idx = np.random.choice(survivors_indices)
            parent2_idx = np.random.choice(survivors_indices)
            
            # Схрещування
            child = self.population[parent1_idx].crossover(
                self.population[parent2_idx]
            )
            
            # Мутація
            child.mutate(MUTATION_RATE, MUTATION_SIGMA)
            
            new_population.append(child)
        
        # Оновити популяцію
        self.population = new_population
        self.generation += 1
    
    def save_population(self, filename):
        """
        Зберегти популяцію в CSV файл
        
        Args:
            filename: шлях до файлу
        """
        # Перетворити всі геніти в плоскі масиви
        flat_genomes = np.array([genome.to_flat() for genome in self.population])
        
        # Зберегти в CSV
        np.savetxt(filename, flat_genomes, delimiter=',', fmt='%d')
        
        print(f"✓ Популяцію збережено в {filename}")
    
    def load_population(self, filename):
        """
        Завантажити популяцію з CSV файлу
        
        Args:
            filename: шлях до файлу
        """
        # Завантажити з CSV
        flat_genomes = np.loadtxt(filename, delimiter=',')
        
        # Якщо завантажено один геном, перетворити в 2D масив
        if len(flat_genomes.shape) == 1:
            flat_genomes = flat_genomes.reshape(1, -1)
        
        # Відновити геноми
        self.population = [Genome.from_flat(flat) for flat in flat_genomes]
        self.population_size = len(self.population)
        
        print(f"✓ Популяцію завантажено з {filename} ({self.population_size} геномів)")