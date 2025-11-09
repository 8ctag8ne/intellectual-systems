# main.py - Головний файл з візуалізацією

import numpy as np
import os
from config import GRID_SIZE, POPULATION_SIZE, FOOD_COUNT, MAX_STEPS
from genome import Genome
from snake import Snake
from environment import Environment
from genetic_algorithm import GeneticAlgorithm
from visualizer import Visualizer


def create_population_environment(ga, food_count=FOOD_COUNT):
    """
    Універсальна функція для створення середовища з популяцією змійок
    
    Args:
        ga: GeneticAlgorithm об'єкт
        food_count: кількість їжі
    
    Returns:
        Environment: середовище з популяцією
    """
    env = Environment(GRID_SIZE, GRID_SIZE)
    
    # Розмістити змійки рівномірно по полю
    grid_positions = []
    grid_step = (GRID_SIZE - 4) // int(np.sqrt(ga.population_size))
    
    for i in range(int(np.sqrt(ga.population_size)) + 1):
        for j in range(int(np.sqrt(ga.population_size)) + 1):
            if len(grid_positions) < ga.population_size:
                x = 2 + j * grid_step + np.random.randint(-2, 3)
                y = 2 + i * grid_step + np.random.randint(-2, 3)
                x = max(2, min(GRID_SIZE - 3, x))
                y = max(2, min(GRID_SIZE - 3, y))
                grid_positions.append((x, y))
    
    # Додати всіх змійок
    for i, genome in enumerate(ga.population):
        x, y = grid_positions[i]
        snake = Snake(x, y, genome, snake_id=i + 1)
        env.add_snake(snake)
    
    # Додати їжу
    env.spawn_food(food_count)
    
    return env


def run_simulation_visualized(env, generation=0, best_fitness=0, max_steps=MAX_STEPS, title=""):
    """
    Універсальна функція для запуску симуляції з візуалізацією
    
    Args:
        env: середовище для симуляції
        generation: номер покоління
        best_fitness: найкращий fitness
        max_steps: максимальна кількість кроків
        title: заголовок для візуалізації
    
    Returns:
        bool: True якщо симуляція завершилася нормально, False якщо перервана
    """
    viz = Visualizer()
    
    try:
        step = 0
        running = True
        
        while env.get_alive_count() > 0 and step < max_steps and running:
            # Обробити події
            if not viz.handle_events():
                running = False
                break
            
            # Крок симуляції
            env.step()
            
            # Намалювати
            viz.draw_environment(env, generation, best_fitness, title)
            
            step += 1
        
        return running
    
    finally:
        viz.close()


def run_training_visualized(generations=10):
    """
    Тренування з візуалізацією кожного покоління
    """
    print("=" * 50)
    print("ТРЕНУВАННЯ З ВІЗУАЛІЗАЦІЄЮ")
    print("=" * 50)
    
    ga = GeneticAlgorithm(population_size=POPULATION_SIZE)
    
    print(f"✓ Початок тренування {generations} поколінь")
    print(f"  Популяція: {POPULATION_SIZE} змійок одночасно")
    print(f"  Їжі на полі: {FOOD_COUNT}")
    print("  Натисніть ESC для виходу\n")
    
    try:
        for gen in range(generations):
            print(f"\n{'=' * 50}")
            print(f"ПОКОЛІННЯ {gen + 1}/{generations}")
            print(f"{'=' * 50}")
            
            # Створити середовище з поточною популяцією
            env = create_population_environment(ga)
            
            # Запустити симуляцію з візуалізацією
            completed = run_simulation_visualized(
                env, 
                generation=gen + 1, 
                best_fitness=ga.best_fitness
            )
            
            if not completed:
                print("\n✗ Візуалізацію зупинено користувачем")
                break
            
            # Виконати еволюцію
            print(f"\n✓ Еволюція покоління {gen + 1}...")
            ga.evolve()
            
            # Вивести статистику
            stats = ga.stats_history[-1]
            print(f"  Макс fitness: {stats['max_fitness']:.0f}")
            print(f"  Середнє fitness: {stats['avg_fitness']:.2f}")
            print(f"  Найкраще за всю історію: {stats['best_overall_fitness']:.0f}")
            print(f"  Макс довжина: {stats['max_length']}")
            print(f"  Макс їжі: {stats['max_food']}")
            
            # Зберегти кожні 5 поколінь
            if (gen + 1) % 5 == 0:
                os.makedirs("data/populations", exist_ok=True)
                filename = f"data/populations/gen_{gen + 1}.csv"
                ga.save_population(filename)
    
    except Exception as e:
        print(f"\n✗ Помилка: {e}")
        import traceback
        traceback.print_exc()
    
    return ga


def run_training_headless(generations=100, save_stats=True):
    """
    Швидке тренування без візуалізації
    """
    print("=" * 50)
    print("ШВИДКЕ ТРЕНУВАННЯ (БЕЗ ВІЗУАЛІЗАЦІЇ)")
    print("=" * 50)
    
    ga = GeneticAlgorithm(population_size=POPULATION_SIZE)
    
    print(f"✓ Початок тренування {generations} поколінь")
    print(f"  Популяція: {POPULATION_SIZE} змійок одночасно")
    print(f"  Їжі на полі: {FOOD_COUNT}")
    print(f"  Виживають найкращі {POPULATION_SIZE // 2}\n")
    
    # Підготувати CSV файл для статистики
    if save_stats:
        import csv
        import datetime
        
        os.makedirs("data/stats", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_filename = f"data/stats/training_{timestamp}.csv"
        
        stats_file = open(stats_filename, 'w', newline='')
        stats_writer = csv.writer(stats_file)
        stats_writer.writerow([
            'Generation', 'Max_Fitness', 'Avg_Fitness', 
            'Best_Overall_Fitness', 'Max_Length', 'Max_Food'
        ])
    
    try:
        for gen in range(generations):
            ga.evolve()
            
            stats = ga.stats_history[-1]
            
            # Виводити кожне покоління
            print(f"Gen {stats['generation']:3d} | "
                  f"Max: {stats['max_fitness']:7.0f} | "
                  f"Avg: {stats['avg_fitness']:7.2f} | "
                  f"Best: {stats['best_overall_fitness']:7.0f} | "
                  f"Len: {stats['max_length']:2d} | "
                  f"Food: {stats['max_food']:2d}")
            
            # Записати статистику в CSV
            if save_stats:
                stats_writer.writerow([
                    stats['generation'],
                    stats['max_fitness'],
                    stats['avg_fitness'],
                    stats['best_overall_fitness'],
                    stats['max_length'],
                    stats['max_food']
                ])
            
            # Зберегти кожні 50 поколінь
            if (gen + 1) % 50 == 0:
                os.makedirs("data/populations", exist_ok=True)
                filename = f"data/populations/gen_{gen + 1}.csv"
                ga.save_population(filename)
    
    finally:
        if save_stats:
            stats_file.close()
            print(f"\n✓ Статистика збережена в {stats_filename}")
    
    print(f"\n✓ Тренування завершено!")
    print(f"  Найкращий fitness: {ga.best_fitness:.0f}")
    
    return ga


def watch_best_snake(genome, steps=MAX_STEPS):
    """
    Переглянути найкращу змійку
    """
    print("=" * 50)
    print("ПЕРЕГЛЯД НАЙКРАЩОЇ ЗМІЙКИ")
    print("=" * 50)
    
    # Створити середовище з однією змійкою
    env = Environment(GRID_SIZE, GRID_SIZE)
    snake = Snake(GRID_SIZE // 2, GRID_SIZE // 2, genome, snake_id=1)
    env.add_snake(snake)
    env.spawn_food(FOOD_COUNT)
    
    print(f"✓ Перегляд змійки (макс {MAX_STEPS} кроків)")
    print(f"  Їжі на полі: {FOOD_COUNT}")
    print(f"  Натисніть ESC для виходу\n")
    
    # Запустити симуляцію з візуалізацією
    completed = run_simulation_visualized(
        env,
        generation=0,
        best_fitness=genome.get_fitness() if hasattr(genome, 'get_fitness') else 0,
        max_steps=steps,
        title="Перегляд найкращої змійки"
    )
    
    # Фінальна статистика
    print("\n✓ Симуляція завершена")
    print(f"  Кроків: {snake.steps}")
    print(f"  Довжина: {snake.length}")
    print(f"  З'їдено їжі: {snake.food_eaten}")
    print(f"  Фінальний fitness: {snake.get_fitness():.0f}")
    print(f"  Статус: {'жива' if snake.alive else 'мертва'}")
    
    return completed


def load_population_interactive():
    """
    Інтерактивне завантаження популяції
    
    Returns:
        GeneticAlgorithm: завантажений GA або None
    """
    print("\nДоступні файли популяцій:")
    
    if not os.path.exists("data/populations"):
        print("  Папка data/populations не існує")
        return None
    
    files = [f for f in os.listdir("data/populations") if f.endswith('.csv')]
    
    if not files:
        print("  Немає збережених популяцій")
        return None
    
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    
    try:
        file_idx = input("\nОберіть файл (номер): ").strip()
        file_idx = int(file_idx) - 1
        
        if file_idx < 0 or file_idx >= len(files):
            print("✗ Невірний номер файлу")
            return None
        
        filename = f"data/populations/{files[file_idx]}"
        
        # Завантажити популяцію
        ga = GeneticAlgorithm(population_size=POPULATION_SIZE)
        ga.load_population(filename)
        
        print(f"✓ Завантажено популяцію з {files[file_idx]}")
        print(f"  Покоління: {ga.generation}")
        print(f"  Найкращий fitness: {ga.best_fitness:.0f}")
        
        return ga
    
    except (ValueError, IndexError):
        print("✗ Невірний номер файлу")
        return None


def continue_training_visualized(ga, generations=10):
    """
    Продовжити тренування з візуалізацією для завантаженої популяції
    """
    print(f"\n✓ Продовження тренування для {generations} поколінь")
    
    try:
        for gen in range(generations):
            current_gen = ga.generation + 1
            
            print(f"\n{'=' * 50}")
            print(f"ПОКОЛІННЯ {current_gen}")
            print(f"{'=' * 50}")
            
            # Створити середовище з поточною популяцією
            env = create_population_environment(ga)
            
            # Запустити симуляцію з візуалізацією
            completed = run_simulation_visualized(
                env,
                generation=current_gen,
                best_fitness=ga.best_fitness,
                title=f"Продовження тренування - Покоління {current_gen}"
            )
            
            if not completed:
                print("\n✗ Візуалізацію зупинено користувачем")
                break
            
            # Виконати еволюцію
            print(f"\n✓ Еволюція покоління {current_gen}...")
            ga.evolve()
            
            # Вивести статистику
            stats = ga.stats_history[-1]
            print(f"  Макс fitness: {stats['max_fitness']:.0f}")
            print(f"  Середнє fitness: {stats['avg_fitness']:.2f}")
            print(f"  Найкраще за всю історію: {stats['best_overall_fitness']:.0f}")
            print(f"  Макс довжина: {stats['max_length']}")
            print(f"  Макс їжі: {stats['max_food']}")
            
            # Зберегти кожні 5 поколінь
            if (gen + 1) % 5 == 0:
                filename = f"data/populations/continued_gen_{current_gen}.csv"
                ga.save_population(filename)
    
    except Exception as e:
        print(f"\n✗ Помилка: {e}")
        import traceback
        traceback.print_exc()
    
    return ga


def continue_training_headless(ga, generations=10):
    """
    Продовжити тренування без візуалізації
    """
    print(f"\n✓ Продовження тренування для {generations} поколінь (без візуалізації)")
    
    for gen in range(generations):
        ga.evolve()
        stats = ga.stats_history[-1]
        
        print(f"Gen {stats['generation']:3d} | "
              f"Max: {stats['max_fitness']:7.0f} | "
              f"Avg: {stats['avg_fitness']:7.2f} | "
              f"Best: {stats['best_overall_fitness']:7.0f} | "
              f"Len: {stats['max_length']:2d} | "
              f"Food: {stats['max_food']:2d}")
        
        # Зберегти кожні 10 поколінь
        if (gen + 1) % 10 == 0:
            filename = f"data/populations/continued_gen_{stats['generation']}.csv"
            ga.save_population(filename)
    
    return ga


def main_menu():
    """Головне меню програми"""
    print("\n" + "=" * 50)
    print("ГЕНЕТИЧНИЙ АЛГОРИТМ ДЛЯ ЗМІЙКИ")
    print("=" * 50)
    print("\nОберіть режим:")
    print("  1. Тренування з візуалізацією (повільно, наочно)")
    print("  2. Швидке тренування без візуалізації")
    print("  3. Переглянути найкращу змійку")
    print("  4. Завантажити популяцію і продовжити тренування")
    print("  5. Тест системи (базові тести)")
    print("  0. Вихід")
    
    choice = input("\nВаш вибір: ").strip()
    
    if choice == "1":
        # Тренування з візуалізацією
        gens = input("Кількість поколінь (default=10): ").strip()
        gens = int(gens) if gens else 10
        
        ga = run_training_visualized(gens)
        
        # Запропонувати зберегти
        if input("\nЗберегти популяцію? (y/n): ").lower() == 'y':
            os.makedirs("data/populations", exist_ok=True)
            filename = f"data/populations/final_gen_{ga.generation}.csv"
            ga.save_population(filename)
        
        # Запропонувати переглянути
        if input("Переглянути найкращу змійку? (y/n): ").lower() == 'y':
            watch_best_snake(ga.best_genome)
    
    elif choice == "2":
        # Швидке тренування
        gens = input("Кількість поколінь (default=100): ").strip()
        gens = int(gens) if gens else 100
        
        save_csv = input("Зберігати статистику в CSV? (y/n, default=y): ").strip().lower()
        save_csv = save_csv != 'n'
        
        ga = run_training_headless(gens, save_stats=save_csv)
        
        # Автоматично зберегти популяцію
        os.makedirs("data/populations", exist_ok=True)
        filename = f"data/populations/final_gen_{ga.generation}.csv"
        ga.save_population(filename)
        
        # Запропонувати переглянути
        if input("\nПереглянути найкращу змійку? (y/n): ").lower() == 'y':
            watch_best_snake(ga.best_genome)
    
    elif choice == "3":
        # Переглянути збережену змійку
        ga = load_population_interactive()
        
        if ga is not None:
            # Використати першого з популяції як найкращого
            best_genome = ga.population[0]
            if ga.best_genome is not None:
                best_genome = ga.best_genome
            
            watch_best_snake(best_genome)
    
    elif choice == "4":
        # Завантажити і продовжити тренування
        ga = load_population_interactive()
        
        if ga is not None:
            mode = input("Візуалізація? (y/n): ").lower()
            gens = input("Скільки поколінь? (default=10): ").strip()
            gens = int(gens) if gens else 10
            
            if mode == 'y':
                ga = continue_training_visualized(ga, gens)
            else:
                ga = continue_training_headless(ga, gens)
            
            # Зберегти результат
            save_filename = f"data/populations/continued_gen_{ga.generation}.csv"
            ga.save_population(save_filename)
            print(f"✓ Популяцію збережено в {save_filename}")
            
            # Запропонувати переглянути
            if input("\nПереглянути найкращу змійку? (y/n): ").lower() == 'y':
                watch_best_snake(ga.best_genome)
    
    elif choice == "5":
        # Тести
        from test_basic import run_all_tests
        run_all_tests()
    
    elif choice == "0":
        print("\nДо побачення!")
        return False
    
    else:
        print("\n✗ Невірний вибір")
    
    return True


if __name__ == "__main__":
    # Створити необхідні папки
    os.makedirs("data/populations", exist_ok=True)
    os.makedirs("data/stats", exist_ok=True)
    
    # Головний цикл меню
    while True:
        if not main_menu():
            break
        
        input("\nНатисніть Enter для продовження...")