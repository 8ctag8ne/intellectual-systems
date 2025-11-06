# test_basic.py - Базові тести системи

import numpy as np
from config import GRID_SIZE, INITIAL_SNAKE_LENGTH
from genome import Genome
from snake import Snake
from environment import Environment
from genetic_algorithm import GeneticAlgorithm


def test_genome():
    """Тест класу Genome"""
    print("=" * 50)
    print("ТЕСТ GENOME")
    print("=" * 50)
    
    genome = Genome()
    print(f"✓ Створено геном з shape: {genome.weights.shape}")
    print(f"  Мін: {genome.weights.min()}, Макс: {genome.weights.max()}")
    
    original_weights = genome.weights.copy()
    genome.mutate(mutation_rate=0.5, sigma=10)
    changes = np.sum(genome.weights != original_weights)
    print(f"✓ Мутація змінила {changes} ваг")
    
    genome2 = Genome()
    child = genome.crossover(genome2)
    print(f"✓ Схрещування створило дочірній геном")
    
    flat = genome.to_flat()
    restored = Genome.from_flat(flat)
    print(f"✓ Серіалізація працює: {np.array_equal(genome.weights, restored.weights)}")
    print()


def test_vision():
    """Тест системи зору"""
    print("=" * 50)
    print("ТЕСТ СИСТЕМИ ЗОРУ")
    print("=" * 50)
    
    env = Environment(GRID_SIZE, GRID_SIZE)
    genome = Genome()
    snake = Snake(25, 25, genome, snake_id=1)
    env.add_snake(snake)
    
    from food import Food
    env.foods.append(Food(25, 20))
    env.foods.append(Food(30, 25))
    env.update_grid()
    
    vision = snake.get_vision(env)
    food_seen = np.sum(vision[:, :, 0])
    obstacles_seen = np.sum(vision[:, :, 1])
    
    print(f"✓ Поле зору shape: {vision.shape}")
    print(f"  Їжі в полі зору: {food_seen}")
    print(f"  Перешкод: {obstacles_seen}")
    print()


def test_genetic_algorithm():
    """Тест генетичного алгоритму"""
    print("=" * 50)
    print("ТЕСТ ГЕНЕТИЧНОГО АЛГОРИТМУ")
    print("=" * 50)
    
    ga = GeneticAlgorithm(population_size=15)
    print(f"✓ Створено GA з популяцією {ga.population_size}")
    
    print(f"✓ Еволюція 3 поколінь...")
    for gen in range(3):
        ga.evolve()
        stats = ga.stats_history[-1]
        print(f"  Gen {stats['generation']}: Max={stats['max_fitness']:.0f}, "
              f"Avg={stats['avg_fitness']:.2f}")
    
    first_max = ga.stats_history[0]['max_fitness']
    last_max = ga.stats_history[-1]['max_fitness']
    print(f"✓ Прогрес: {first_max:.0f} → {last_max:.0f} ({last_max - first_max:+.0f})")
    print()


def run_all_tests():
    """Запустити всі тести"""
    print("\n" + "=" * 50)
    print("БАЗОВІ ТЕСТИ СИСТЕМИ")
    print("=" * 50 + "\n")
    
    test_genome()
    test_vision()
    test_genetic_algorithm()
    
    print("=" * 50)
    print("ВСІ ТЕСТИ ПРОЙДЕНО!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_all_tests()