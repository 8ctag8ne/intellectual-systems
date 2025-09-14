import os
from src.constants import *


class MapLoader:
    def __init__(self):
        self.maps_dir = "./resources/maps"
        # Створюємо папки якщо не існують
        os.makedirs(self.maps_dir, exist_ok=True)
        os.makedirs("./resources/sprites", exist_ok=True)

        # Створюємо базову карту якщо вона не існує
        self.create_default_map()

    def create_default_map(self):
        """Створює базову карту якщо вона не існує"""
        map_path = os.path.join(self.maps_dir, "map1.txt")
        if not os.path.exists(map_path):
            default_map = [
                "########################",
                "#..........##..........#",
                "#.##.#####.##.#####.##.#",
                "#.......................#",
                "#.##.#.#######.#.##.#",
                "#....#....##....#....#",
                "####.####.##.####.####",
                "   #.#..........#.#   ",
                "####.#.##  ##.#.####",
                "#......##  ##......#",
                "####.#.########.#.####",
                "   #.#....P.....#.#   ",
                "####.####.##.####.####",
                "#....#....##....#....#",
                "#.##.#.#######.#.##.#",
                "#..G........G.......G.#",
                "#.##.#####.##.#####.##.#",
                "#..........##..........#",
                "########################"
            ]

            with open(map_path, 'w') as f:
                f.write('\n'.join(default_map))

    def load_map(self, filename):
        """Завантажує карту з файлу та повертає структуровані дані"""
        map_path = os.path.join(self.maps_dir, filename)

        if not os.path.exists(map_path):
            raise FileNotFoundError(f"Карта {filename} не знайдена!")

        walls = set()
        dots = set()
        ghost_starts = []
        pacman_start = None

        with open(map_path, 'r') as f:
            lines = f.readlines()

        for y, line in enumerate(lines):
            line = line.rstrip('\n')
            for x, char in enumerate(line):
                if char == WALL:
                    walls.add((x, y))
                elif char == DOT:
                    dots.add((x, y))
                elif char == PACMAN_START:
                    pacman_start = (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
                elif char == GHOST_START:
                    ghost_starts.append((x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
                # EMPTY та BIG_DOT поки не обробляємо

        if pacman_start is None:
            raise ValueError(f"В карті {filename} не знайдено стартової позиції Пакмена (P)!")

        if len(ghost_starts) == 0:
            raise ValueError(f"В карті {filename} не знайдено стартових позицій привидів (G)!")

        return {
            'walls': walls,
            'dots': dots,
            'pacman_start': pacman_start,
            'ghost_starts': ghost_starts
        }

    def get_available_maps(self):
        """Повертає список доступних карт"""
        maps = []
        for filename in os.listdir(self.maps_dir):
            if filename.endswith('.txt'):
                maps.append(filename)
        return maps