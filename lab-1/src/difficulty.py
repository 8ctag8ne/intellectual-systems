# difficulty.py - Оновлена система складності з правилами
from src.ghost_ai import *


class DifficultyLevel:
    """Клас що описує рівень складності з правилами"""

    def __init__(self, name, description, rule_sets):
        self.name = name
        self.description = description
        self.rule_sets = rule_sets  # Список наборів правил для кожного привида


class DifficultyManager:
    """Менеджер рівнів складності з правилами"""

    def __init__(self):
        self.current_level = 0
        self.levels = self._create_difficulty_levels()

    def _create_difficulty_levels(self):
        """Створює 4 рівні складності з різними наборами правил"""
        return [
            # Рівень 1: Новачок - тільки базові правила
            DifficultyLevel(
                name="Beginner",
                description="Simple wandering, limited vision",
                rule_sets=[
                    # Привид 1: Тільки блукання
                    [
                        WanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=3, priority=0.8)
                    ],
                    # Привид 2: Блукання + базове патрулювання
                    [
                        WanderRule(priority=1.0),
                        PatrolRule(patrol_points=[(5, 5), (18, 5), (18, 15), (5, 15)], priority=1.2),
                        AvoidOtherGhostsRule(min_distance=3, priority=0.8)
                    ],
                    # Привид 3: Випадковий рух
                    [
                        WanderRule(priority=1.0),
                    ],
                    # Привид 4: Випадковий рух
                    [
                        WanderRule(priority=1.0),
                    ]
                ]
            ),

            # Рівень 2: Середній - додаємо обмежене переслідування
            DifficultyLevel(
                name="Intermediate",
                description="Limited chasing, basic cooperation",
                rule_sets=[
                    # Привид 1: Переслідувач з обмеженою видимістю
                    [
                        SeekPacmanRule(view_distance=6, priority=3.0),
                        WanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=2, priority=1.5)
                    ],
                    # Привид 2: Патрульний
                    [
                        PatrolRule(patrol_points=[(3, 3), (20, 3), (20, 16), (3, 16)], priority=2.0),
                        SeekPacmanRule(view_distance=4, priority=2.5),
                        WanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=2, priority=1.5)
                    ],
                    # Привид 3: Блукання з рідкісним переслідуванням
                    [
                        WanderRule(priority=1.2),
                        SeekPacmanRule(view_distance=3, priority=2.0),
                        AvoidOtherGhostsRule(min_distance=2, priority=1.0)
                    ],
                    # Привид 4: Тільки блукання
                    [
                        WanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=3, priority=0.8)
                    ]
                ]
            ),

            # Рівень 3: Складний - стратегічна поведінка
            DifficultyLevel(
                name="Advanced",
                description="Strategic positioning, flanking, prediction",
                rule_sets=[
                    # Привид 1: Активний переслідувач з передбаченням
                    [
                        SeekPacmanRule(view_distance=8, priority=3.0),
                        PredictPacmanRule(prediction_steps=3, priority=2.5),
                        FlankPacmanRule(priority=2.0),
                        WanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=1, priority=1.5)
                    ],
                    # Привид 2: Фланговий маневр
                    [
                        FlankPacmanRule(priority=3.0),
                        SeekPacmanRule(view_distance=6, priority=2.5),
                        PatrolRule(patrol_points=[(2, 2), (21, 2), (21, 17), (2, 17)], priority=1.5),
                        WanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=1, priority=1.2)
                    ],
                    # Привид 3: Блокувальник втеч
                    [
                        BlockEscapeRoute(priority=2.8),
                        SeekPacmanRule(view_distance=6, priority=2.0),
                        WanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=1, priority=1.0)
                    ],
                    # Привид 4: Смішана стратегія
                    [
                        SeekPacmanRule(view_distance=7, priority=2.5),
                        PredictPacmanRule(prediction_steps=2, priority=2.0),
                        PatrolRule(patrol_points=[(12, 6), (12, 12)], priority=1.8),
                        WanderRule(priority=1.0)
                    ]
                ]
            ),

            # Рівень 4: Експерт - повна координація
            DifficultyLevel(
                name="Expert",
                description="Full coordination, advanced tactics, unlimited vision",
                rule_sets=[
                    # Привид 1: Головний переслідувач
                    [
                        SeekPacmanRule(view_distance=float('inf'), priority=4.0),
                        PredictPacmanRule(prediction_steps=4, priority=3.5),
                        FlankPacmanRule(priority=3.0),
                        BlockEscapeRoute(priority=2.5),
                        WanderRule(priority=1.0)
                    ],
                    # Привид 2: Фланговий спеціаліст
                    [
                        FlankPacmanRule(priority=4.0),
                        BlockEscapeRoute(priority=3.5),
                        SeekPacmanRule(view_distance=float('inf'), priority=3.0),
                        PredictPacmanRule(prediction_steps=3, priority=2.5),
                        WanderRule(priority=1.0)
                    ],
                    # Привид 3: Блокувальник
                    [
                        BlockEscapeRoute(priority=4.0),
                        PredictPacmanRule(prediction_steps=5, priority=3.0),
                        SeekPacmanRule(view_distance=float('inf'), priority=2.5),
                        FlankPacmanRule(priority=2.0),
                        WanderRule(priority=1.0)
                    ],
                    # Привид 4: Універсальний
                    [
                        SeekPacmanRule(view_distance=float('inf'), priority=3.5),
                        FlankPacmanRule(priority=3.5),
                        BlockEscapeRoute(priority=3.0),
                        PredictPacmanRule(prediction_steps=3, priority=2.8),
                        WanderRule(priority=1.0)
                    ]
                ]
            )
        ]

    def get_current_level(self):
        """Повертає поточний рівень складності"""
        return self.levels[self.current_level]

    def next_level(self):
        """Переходить до наступного рівня"""
        if self.current_level < len(self.levels) - 1:
            self.current_level += 1
            return True
        return False

    def prev_level(self):
        """Переходить до попереднього рівня"""
        if self.current_level > 0:
            self.current_level -= 1
            return True
        return False

    def set_level(self, level_index):
        """Встановлює конкретний рівень"""
        if 0 <= level_index < len(self.levels):
            self.current_level = level_index
            return True
        return False

    def get_level_count(self):
        """Повертає кількість рівнів"""
        return len(self.levels)

    def get_level_names(self):
        """Повертає список назв рівнів"""
        return [level.name for level in self.levels]

    def create_ghost_ais(self, ghosts, game):
        """Створює ШІ для привидів відповідно до поточного рівня"""
        current_level = self.get_current_level()
        ghost_ais = []

        for i, ghost in enumerate(ghosts):
            if i < len(current_level.rule_sets):
                rules = []
                # Створюємо копії правил для кожного привида
                for rule_class_or_instance in current_level.rule_sets[i]:
                    if isinstance(rule_class_or_instance, GhostRule):
                        # Якщо це вже екземпляр правила, створюємо копію
                        rule_type = type(rule_class_or_instance)
                        # Копіюємо базові параметри
                        new_rule = rule_type.__new__(rule_type)
                        new_rule.__dict__.update(rule_class_or_instance.__dict__)
                        rules.append(new_rule)
                    else:
                        # Якщо це клас правила, створюємо новий екземпляр
                        rules.append(rule_class_or_instance)

                # Створюємо ШІ з правилами
                ghost_ai = RuleBasedGhostAI(ghost, game, rules)
                ghost_ais.append(ghost_ai)
            else:
                # Якщо привидів більше ніж конфігурацій, використовуємо базовий ШІ
                basic_rules = [WanderRule(priority=1.0)]
                ghost_ai = RuleBasedGhostAI(ghost, game, basic_rules)
                ghost_ais.append(ghost_ai)

        return ghost_ais

    def get_active_rules_description(self):
        """Повертає опис активних правил для поточного рівня"""
        current_level = self.get_current_level()
        descriptions = []

        rule_names = set()
        for rule_set in current_level.rule_sets:
            for rule in rule_set:
                rule_name = rule.__class__.__name__
                if rule_name not in rule_names:
                    rule_names.add(rule_name)

        rule_descriptions = {
            'SeekPacmanRule': 'Direct pursuit',
            'PredictPacmanRule': 'Movement prediction',
            'FlankPacmanRule': 'Flanking maneuvers',
            'AvoidOtherGhostsRule': 'Ghost separation',
            'PatrolRule': 'Territory patrol',
            'BlockEscapeRoute': 'Exit blocking',
            'WanderRule': 'Random movement'
        }

        for rule_name in rule_names:
            if rule_name in rule_descriptions:
                descriptions.append(rule_descriptions[rule_name])

        return ', '.join(descriptions)