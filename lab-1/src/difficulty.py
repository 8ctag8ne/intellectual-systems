# difficulty.py - Оновлена система складності з покращеними правилами
from src.ghost_ai import *
from src.enhanced_ghost_ai import *

class DifficultyLevel:
    """Клас що описує рівень складності з правилами"""

    def __init__(self, name, description, rule_sets):
        self.name = name
        self.description = description
        self.rule_sets = rule_sets

class DifficultyManager:
    """Менеджер рівнів складності з покращеними правилами"""

    def __init__(self):
        self.current_level = 0
        self.levels = self._create_difficulty_levels()

    def _create_difficulty_levels(self):
        """Створює 4 рівні складності з покращеними правилами"""
        return [
            # Рівень 1: Новачок - мінімальна видимість, простий рух
            DifficultyLevel(
                name="Beginner",
                description="Short sight, no memory, simple patrol",
                rule_sets=[
                    # Привид 1: Коротка видимість + блукання
                    [
                        EnhancedVisionRule(sight_radius=2, sound_radius=1, memory_duration=0.5, priority=2.0),
                        IntelligentWanderRule(priority=1.2),
                        AvoidOtherGhostsRule(min_distance=3, priority=1.0)
                    ],
                    # Привид 2: Базове патрулювання
                    [
                        SmartPatrolRule(patrol_points=[(5, 5), (18, 5), (18, 15), (5, 15)], priority=1.5),
                        IntelligentWanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=3, priority=1.0)
                    ],
                    # Привид 3: Тільки розумне блукання
                    [
                        IntelligentWanderRule(priority=1.5),
                        AvoidOtherGhostsRule(min_distance=2, priority=0.8)
                    ],
                    # Привид 4: Випадковий рух
                    [
                        WanderRule(priority=1.0),
                    ]
                ]
            ),

            # Рівень 2: Середній - покращена видимість, коротка пам'ять
            DifficultyLevel(
                name="Intermediate",
                description="Medium sight, short memory, sound detection",
                rule_sets=[
                    # Привид 1: Активний переслідувач
                    [
                        EnhancedVisionRule(sight_radius=4, sound_radius=2, memory_duration=1.5, priority=3.0),
                        IntelligentWanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=2, priority=1.2)
                    ],
                    # Привид 2: Патрульний з детекцією
                    [
                        SmartPatrolRule(patrol_points=[(3, 3), (20, 3), (20, 16), (3, 16)], priority=2.0),
                        EnhancedVisionRule(sight_radius=3, sound_radius=2, memory_duration=1.0, priority=2.5),
                        IntelligentWanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=2, priority=1.2)
                    ],
                    # Привид 3: Змішана стратегія
                    [
                        EnhancedVisionRule(sight_radius=3, sound_radius=1, memory_duration=1.0, priority=2.0),
                        IntelligentWanderRule(priority=1.2),
                        AvoidOtherGhostsRule(min_distance=2, priority=1.0)
                    ],
                    # Привид 4: Покращене блукання
                    [
                        IntelligentWanderRule(priority=1.2),
                        EnhancedVisionRule(sight_radius=2, sound_radius=1, memory_duration=0.5, priority=1.5),
                        AvoidOtherGhostsRule(min_distance=3, priority=0.8)
                    ]
                ]
            ),

            # Рівень 3: Складний - добра видимість, пам'ять, координація
            DifficultyLevel(
                name="Advanced",
                description="Good sight, memory, basic coordination, prediction",
                rule_sets=[
                    # Привид 1: Головний переслідувач з передбаченням
                    [
                        EnhancedVisionRule(sight_radius=6, sound_radius=3, memory_duration=3.0, priority=3.5),
                        PredictPacmanRule(prediction_steps=2, priority=2.5),
                        IntelligentWanderRule(priority=1.0),
                        SeekPacmanRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=1, priority=0.75)
                    ],
                    # Привид 2: Фланговий спеціаліст
                    [
                        EnhancedVisionRule(sight_radius=5, sound_radius=2, memory_duration=2.5, priority=3.0),
                        FlankPacmanRule(priority=2.8),
                        SmartPatrolRule(patrol_points=[(2, 2), (21, 2), (21, 17), (2, 17)], priority=1.5),
                        IntelligentWanderRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=1, priority=0.6)
                    ],
                    # Привид 3: Блокувальник
                    [
                        EnhancedVisionRule(sight_radius=5, sound_radius=2, memory_duration=2.0, priority=2.8),
                        BlockEscapeRoute(priority=2.5),
                        IntelligentWanderRule(priority=1.0),
                        SeekPacmanRule(priority=1.0),
                        AvoidOtherGhostsRule(min_distance=1, priority=0.5)
                    ],
                    # Привид 4: Підтримка
                    [
                        EnhancedVisionRule(sight_radius=4, sound_radius=2, memory_duration=2.0, priority=2.5),
                        PredictPacmanRule(prediction_steps=1, priority=2.0),
                        SmartPatrolRule(patrol_points=[(12, 6), (12, 12)], priority=1.8),
                        SeekPacmanRule(priority=1.0),
                        IntelligentWanderRule(priority=1.0)
                    ]
                ]
            ),

            # Рівень 4: Експерт - відмінна видимість, довга пам'ять, повна координація
            DifficultyLevel(
                name="Expert",
                description="Excellent sight, long memory, full coordination, advanced tactics",
                rule_sets=[
                    # Привид 1: Альфа-переслідувач
                    [
                        EnhancedVisionRule(sight_radius=8, sound_radius=4, memory_duration=5.0, priority=4.0),
                        PredictPacmanRule(prediction_steps=3, priority=3.5),
                        FlankPacmanRule(priority=3.0),
                        BlockEscapeRoute(priority=2.5),
                        SeekPacmanRule(priority=2.0),
                        IntelligentWanderRule(priority=1.0)
                    ],
                    # Привид 2: Тактичний фланкер
                    [
                        EnhancedVisionRule(sight_radius=7, sound_radius=4, memory_duration=4.5, priority=3.8),
                        FlankPacmanRule(priority=3.5),
                        BlockEscapeRoute(priority=3.2),
                        PredictPacmanRule(prediction_steps=2, priority=2.8),
                        SeekPacmanRule(priority=2.0),
                        IntelligentWanderRule(priority=1.0)
                    ],
                    # Привид 3: Стратегічний блокувальник
                    [
                        EnhancedVisionRule(sight_radius=7, sound_radius=3, memory_duration=4.0, priority=3.5),
                        BlockEscapeRoute(priority=3.8),
                        PredictPacmanRule(prediction_steps=4, priority=3.0),
                        FlankPacmanRule(priority=2.5),
                        SeekPacmanRule(priority=2.0),
                        IntelligentWanderRule(priority=1.0)
                    ],
                    # Привид 4: Універсальний підтримувач
                    [
                        EnhancedVisionRule(sight_radius=6, sound_radius=3, memory_duration=3.5, priority=3.2),
                        PredictPacmanRule(prediction_steps=3, priority=3.0),
                        FlankPacmanRule(priority=2.8),
                        BlockEscapeRoute(priority=2.5),
                        SmartPatrolRule(patrol_points=[(12, 6), (12, 12), (6, 9), (18, 9)], priority=2.0),
                        SeekPacmanRule(priority=2.0),
                        IntelligentWanderRule(priority=1.0)
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
                basic_rules = [IntelligentWanderRule(priority=1.0)]
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
            'EnhancedVisionRule': 'Limited sight & memory',
            'PredictPacmanRule': 'Movement prediction',
            'FlankPacmanRule': 'Flanking maneuvers',
            'AvoidOtherGhostsRule': 'Ghost separation',
            'SmartPatrolRule': 'Adaptive patrol',
            'BlockEscapeRoute': 'Exit blocking',
            'IntelligentWanderRule': 'Smart exploration',
            'WanderRule': 'Random movement'
        }

        for rule_name in rule_names:
            if rule_name in rule_descriptions:
                descriptions.append(rule_descriptions[rule_name])

        return ', '.join(descriptions)