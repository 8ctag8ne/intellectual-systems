#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
База знань про аніме та мангу
Реалізує ієрархію класів з відношеннями is_a, part_of, has
"""


class KnowledgeBase:
    def __init__(self):
        # Зберігання відношень: {(об'єкт1, відношення, об'єкт2)}
        self.facts = set()
        # Зберігання класів та їх екземплярів
        self.classes = {}

    def add_fact(self, subject, relation, obj):
        """Додати факт до бази знань"""
        self.facts.add((subject, relation, obj))

    def add_class(self, class_name, instances=None):
        """Додати клас та його екземпляри"""
        if instances is None:
            instances = []
        self.classes[class_name] = instances

    def query_direct(self, subject, obj):
        """Перевірити пряме відношення між об'єктами"""
        for s, rel, o in self.facts:
            if s == subject and o == obj:
                return True, rel
        return False, None

    def query_transitive(self, subject, obj, visited=None):
        """
        Перевірити транзитивний зв'язок між об'єктами
        Використовує пошук в глибину (DFS)
        """
        if visited is None:
            visited = set()

        if subject in visited:
            return False, []

        visited.add(subject)

        # Перевірка прямого зв'язку
        direct, relation = self.query_direct(subject, obj)
        if direct:
            return True, [(subject, relation, obj)]

        # Пошук транзитивних зв'язків
        for s, rel, intermediate in self.facts:
            if s == subject:
                found, path = self.query_transitive(intermediate, obj, visited)
                if found:
                    return True, [(subject, rel, intermediate)] + path

        return False, []

    def get_all_relations(self, subject):
        """Отримати всі відношення для об'єкта"""
        relations = []
        for s, rel, o in self.facts:
            if s == subject:
                relations.append((rel, o))
        return relations

    def get_hierarchy(self, obj, relation="is_a", level=0):
        """Отримати ієрархію для об'єкта"""
        hierarchy = [(level, obj)]
        for s, rel, o in self.facts:
            if o == obj and rel == relation:
                hierarchy.extend(self.get_hierarchy(s, relation, level + 1))
        return hierarchy

    def print_hierarchy(self, root, relation="is_a"):
        """Красиво вивести ієрархію"""
        hierarchy = self.get_hierarchy(root, relation)
        hierarchy.sort(key=lambda x: x[0])

        print(f"\n{'=' * 60}")
        print(f"Ієрархія '{relation}' для: {root}")
        print('=' * 60)

        for level, item in hierarchy:
            indent = "  " * level
            if level == 0:
                print(f"{indent}📌 {item}")
            else:
                print(f"{indent}└─ {item}")

    def remove_fact(self, subject, relation, obj):
        """Видалити факт з бази знань"""
        fact = (subject, relation, obj)
        if fact in self.facts:
            self.facts.remove(fact)
            return True, f"✅ Факт видалено: {subject} --[{relation}]--> {obj}"
        return False, f"❌ Факт не знайдено: {subject} --[{relation}]--> {obj}"

    def add_fact_interactive(self, subject, relation, obj):
        """Додати факт інтерактивно з перевіркою"""
        if (subject, relation, obj) in self.facts:
            return False, f"⚠️ Факт вже існує: {subject} --[{relation}]--> {obj}"

        self.facts.add((subject, relation, obj))
        return True, f"✅ Факт додано: {subject} --[{relation}]--> {obj}"

    def list_all_entities(self):
        """Отримати список всіх унікальних сутностей"""
        entities = set()
        for s, _, o in self.facts:
            entities.add(s)
            entities.add(o)
        return sorted(entities)

    def list_all_relations(self):
        """Отримати список всіх типів відношень"""
        relations = set()
        for _, rel, _ in self.facts:
            relations.add(rel)
        return sorted(relations)

    def find_by_relation(self, relation):
        """Знайти всі факти з певним типом відношення"""
        results = []
        for s, rel, o in self.facts:
            if rel == relation:
                results.append((s, o))
        return results

    def export_facts(self, filename="kb_export.txt"):
        """Експортувати базу знань у файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for s, rel, o in sorted(self.facts):
                    f.write(f"{s},{rel},{o}\n")
            return True, f"✅ База експортована в {filename}"
        except Exception as e:
            return False, f"❌ Помилка експорту: {e}"

    def import_facts(self, filename="kb_export.txt"):
        """Імпортувати базу знань з файлу"""
        try:
            count = 0
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(',')
                        if len(parts) == 3:
                            self.facts.add((parts[0], parts[1], parts[2]))
                            count += 1
            return True, f"✅ Імпортовано {count} фактів з {filename}"
        except Exception as e:
            return False, f"❌ Помилка імпорту: {e}"


# ============================================================
# ПОВНА ЗАМІНА create_anime_knowledge_base()
# Предметна область: КЛАСИФІКАЦІЯ ЗБРОЇ
# 4 рівні ієрархії is_a + двосторонні зв'язки part_of/has
# ============================================================

def create_knowledge_base():
    """
    База знань: КЛАСИФІКАЦІЯ ЗБРОЇ
    4 рівні ієрархії is_a
    Двосторонні зв'язки: part_of ↔ has
    """
    kb = KnowledgeBase()

    # ============================================================
    # ІЄРАРХІЯ IS_A - РІВНО 4 РІВНІ
    # ============================================================

    # РІВЕНЬ 1: Найвищий - Зброя
    kb.add_fact("Weapon", "is_a", "Item")

    # РІВЕНЬ 2: Основні категорії за типом бою
    kb.add_fact("MeleeWeapon", "is_a", "Weapon")
    kb.add_fact("RangedWeapon", "is_a", "Weapon")
    kb.add_fact("ExplosiveWeapon", "is_a", "Weapon")

    # РІВЕНЬ 3: Підкатегорії
    # Холодна зброя
    kb.add_fact("Sword", "is_a", "MeleeWeapon")
    kb.add_fact("Axe", "is_a", "MeleeWeapon")
    kb.add_fact("Spear", "is_a", "MeleeWeapon")
    kb.add_fact("Dagger", "is_a", "MeleeWeapon")
    kb.add_fact("Mace", "is_a", "MeleeWeapon")
    kb.add_fact("Staff", "is_a", "MeleeWeapon")

    # Дистанційна зброя
    kb.add_fact("Bow", "is_a", "RangedWeapon")
    kb.add_fact("Crossbow", "is_a", "RangedWeapon")
    kb.add_fact("Firearm", "is_a", "RangedWeapon")
    kb.add_fact("Throwable", "is_a", "RangedWeapon")

    # Вибухівка
    kb.add_fact("Grenade", "is_a", "ExplosiveWeapon")
    kb.add_fact("Mine", "is_a", "ExplosiveWeapon")
    kb.add_fact("Bomb", "is_a", "ExplosiveWeapon")

    # РІВЕНЬ 4: Конкретні види
    # Мечі
    kb.add_fact("Longsword", "is_a", "Sword")
    kb.add_fact("Katana", "is_a", "Sword")
    kb.add_fact("Rapier", "is_a", "Sword")
    kb.add_fact("Scimitar", "is_a", "Sword")
    kb.add_fact("Claymore", "is_a", "Sword")
    kb.add_fact("Shortsword", "is_a", "Sword")

    # Сокири
    kb.add_fact("BattleAxe", "is_a", "Axe")
    kb.add_fact("Hatchet", "is_a", "Axe")
    kb.add_fact("Tomahawk", "is_a", "Axe")
    kb.add_fact("Halberd", "is_a", "Axe")

    # Списи
    kb.add_fact("Pike", "is_a", "Spear")
    kb.add_fact("Javelin", "is_a", "Spear")
    kb.add_fact("Lance", "is_a", "Spear")
    kb.add_fact("Trident", "is_a", "Spear")

    # Кинджали
    kb.add_fact("Stiletto", "is_a", "Dagger")
    kb.add_fact("Dirk", "is_a", "Dagger")
    kb.add_fact("Tanto", "is_a", "Dagger")

    # Луки
    kb.add_fact("Longbow", "is_a", "Bow")
    kb.add_fact("Shortbow", "is_a", "Bow")
    kb.add_fact("CompositeBow", "is_a", "Bow")
    kb.add_fact("Recurve", "is_a", "Bow")

    # Вогнепальна зброя
    kb.add_fact("Pistol", "is_a", "Firearm")
    kb.add_fact("Rifle", "is_a", "Firearm")
    kb.add_fact("Shotgun", "is_a", "Firearm")
    kb.add_fact("MachineGun", "is_a", "Firearm")

    # Метальна зброя
    kb.add_fact("Shuriken", "is_a", "Throwable")
    kb.add_fact("ThrowingKnife", "is_a", "Throwable")
    kb.add_fact("Boomerang", "is_a", "Throwable")
    kb.add_fact("Chakram", "is_a", "Throwable")

    # ============================================================
    # КОМПОНЕНТИ ЗБРОЇ (для зв'язків part_of/has)
    # ============================================================

    # Базові компоненти
    kb.add_fact("Component", "is_a", "Item")
    kb.add_fact("Blade", "is_a", "Component")
    kb.add_fact("Handle", "is_a", "Component")
    kb.add_fact("Guard", "is_a", "Component")
    kb.add_fact("Pommel", "is_a", "Component")
    kb.add_fact("String", "is_a", "Component")
    kb.add_fact("Trigger", "is_a", "Component")
    kb.add_fact("Barrel", "is_a", "Component")
    kb.add_fact("Sight", "is_a", "Component")
    kb.add_fact("Magazine", "is_a", "Component")

    # Типи лез
    kb.add_fact("StraightBlade", "is_a", "Blade")
    kb.add_fact("CurvedBlade", "is_a", "Blade")
    kb.add_fact("SerratedBlade", "is_a", "Blade")

    # Типи рукояток
    kb.add_fact("WoodenHandle", "is_a", "Handle")
    kb.add_fact("MetalHandle", "is_a", "Handle")
    kb.add_fact("LeatherHandle", "is_a", "Handle")

    # ============================================================
    # ДВОСТОРОННІ ЗВ'ЯЗКИ: МЕЧІ ТА ЇХ КОМПОНЕНТИ
    # ============================================================

    # Longsword компоненти
    kb.add_fact("StraightBlade", "part_of", "Longsword")
    kb.add_fact("Longsword", "has", "StraightBlade")

    kb.add_fact("MetalHandle", "part_of", "Longsword")
    kb.add_fact("Longsword", "has", "MetalHandle")

    kb.add_fact("Guard", "part_of", "Longsword")
    kb.add_fact("Longsword", "has", "Guard")

    kb.add_fact("Pommel", "part_of", "Longsword")
    kb.add_fact("Longsword", "has", "Pommel")

    # Katana компоненти
    kb.add_fact("CurvedBlade", "part_of", "Katana")
    kb.add_fact("Katana", "has", "CurvedBlade")

    kb.add_fact("WoodenHandle", "part_of", "Katana")
    kb.add_fact("Katana", "has", "WoodenHandle")

    kb.add_fact("Guard", "part_of", "Katana")
    kb.add_fact("Katana", "has", "Guard")

    # Rapier компоненти
    kb.add_fact("StraightBlade", "part_of", "Rapier")
    kb.add_fact("Rapier", "has", "StraightBlade")

    kb.add_fact("MetalHandle", "part_of", "Rapier")
    kb.add_fact("Rapier", "has", "MetalHandle")

    kb.add_fact("Guard", "part_of", "Rapier")
    kb.add_fact("Rapier", "has", "Guard")

    # Scimitar компоненти
    kb.add_fact("CurvedBlade", "part_of", "Scimitar")
    kb.add_fact("Scimitar", "has", "CurvedBlade")

    kb.add_fact("MetalHandle", "part_of", "Scimitar")
    kb.add_fact("Scimitar", "has", "MetalHandle")

    # Dagger компоненти
    kb.add_fact("StraightBlade", "part_of", "Stiletto")
    kb.add_fact("Stiletto", "has", "StraightBlade")

    kb.add_fact("MetalHandle", "part_of", "Stiletto")
    kb.add_fact("Stiletto", "has", "MetalHandle")

    # ============================================================
    # ДВОСТОРОННІ ЗВ'ЯЗКИ: ЛУКИ ТА ЇХ КОМПОНЕНТИ
    # ============================================================

    # Longbow
    kb.add_fact("String", "part_of", "Longbow")
    kb.add_fact("Longbow", "has", "String")

    kb.add_fact("WoodenHandle", "part_of", "Longbow")
    kb.add_fact("Longbow", "has", "WoodenHandle")

    # Crossbow
    kb.add_fact("String", "part_of", "Crossbow")
    kb.add_fact("Crossbow", "has", "String")

    kb.add_fact("Trigger", "part_of", "Crossbow")
    kb.add_fact("Crossbow", "has", "Trigger")

    kb.add_fact("WoodenHandle", "part_of", "Crossbow")
    kb.add_fact("Crossbow", "has", "WoodenHandle")

    # ============================================================
    # ДВОСТОРОННІ ЗВ'ЯЗКИ: ВОГНЕПАЛЬНА ЗБРОЯ
    # ============================================================

    # Pistol
    kb.add_fact("Barrel", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "Barrel")

    kb.add_fact("Trigger", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "Trigger")

    kb.add_fact("MetalHandle", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "MetalHandle")

    kb.add_fact("Magazine", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "Magazine")

    # Rifle
    kb.add_fact("Barrel", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Barrel")

    kb.add_fact("Trigger", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Trigger")

    kb.add_fact("WoodenHandle", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "WoodenHandle")

    kb.add_fact("Sight", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Sight")

    kb.add_fact("Magazine", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Magazine")

    # Shotgun
    kb.add_fact("Barrel", "part_of", "Shotgun")
    kb.add_fact("Shotgun", "has", "Barrel")

    kb.add_fact("Trigger", "part_of", "Shotgun")
    kb.add_fact("Shotgun", "has", "Trigger")

    kb.add_fact("WoodenHandle", "part_of", "Shotgun")
    kb.add_fact("Shotgun", "has", "WoodenHandle")

    # ============================================================
    # МАТЕРІАЛИ
    # ============================================================

    kb.add_fact("Material", "is_a", "Item")
    kb.add_fact("Metal", "is_a", "Material")
    kb.add_fact("Wood", "is_a", "Material")
    kb.add_fact("Leather", "is_a", "Material")
    kb.add_fact("Plastic", "is_a", "Material")

    # Типи металів
    kb.add_fact("Steel", "is_a", "Metal")
    kb.add_fact("Iron", "is_a", "Metal")
    kb.add_fact("Bronze", "is_a", "Metal")
    kb.add_fact("Silver", "is_a", "Metal")

    # Типи дерева
    kb.add_fact("Oak", "is_a", "Wood")
    kb.add_fact("Ash", "is_a", "Wood")
    kb.add_fact("Yew", "is_a", "Wood")

    # ============================================================
    # ДВОСТОРОННІ ЗВ'ЯЗКИ: КОМПОНЕНТИ ТА МАТЕРІАЛИ
    # ============================================================

    # StraightBlade зроблено зі сталі
    kb.add_fact("Steel", "part_of", "StraightBlade")
    kb.add_fact("StraightBlade", "has", "Steel")

    # CurvedBlade зі сталі
    kb.add_fact("Steel", "part_of", "CurvedBlade")
    kb.add_fact("CurvedBlade", "has", "Steel")

    # MetalHandle з заліза
    kb.add_fact("Iron", "part_of", "MetalHandle")
    kb.add_fact("MetalHandle", "has", "Iron")

    # WoodenHandle з дуба
    kb.add_fact("Oak", "part_of", "WoodenHandle")
    kb.add_fact("WoodenHandle", "has", "Oak")

    # LeatherHandle зі шкіри
    kb.add_fact("Leather", "part_of", "LeatherHandle")
    kb.add_fact("LeatherHandle", "has", "Leather")

    # Barrel зі сталі
    kb.add_fact("Steel", "part_of", "Barrel")
    kb.add_fact("Barrel", "has", "Steel")

    # String (тятива)
    kb.add_fact("Leather", "part_of", "String")
    kb.add_fact("String", "has", "Leather")

    # ============================================================
    # ХАРАКТЕРИСТИКИ ЗБРОЇ
    # ============================================================

    kb.add_fact("Property", "is_a", "Item")
    kb.add_fact("Weight", "is_a", "Property")
    kb.add_fact("Length", "is_a", "Property")
    kb.add_fact("Damage", "is_a", "Property")
    kb.add_fact("Range", "is_a", "Property")
    kb.add_fact("Speed", "is_a", "Property")

    # Значення характеристик
    kb.add_fact("Heavy", "is_a", "Weight")
    kb.add_fact("Light", "is_a", "Weight")
    kb.add_fact("Medium", "is_a", "Weight")

    kb.add_fact("Long", "is_a", "Length")
    kb.add_fact("Short", "is_a", "Length")

    kb.add_fact("HighDamage", "is_a", "Damage")
    kb.add_fact("MediumDamage", "is_a", "Damage")
    kb.add_fact("LowDamage", "is_a", "Damage")

    kb.add_fact("LongRange", "is_a", "Range")
    kb.add_fact("ShortRange", "is_a", "Range")

    kb.add_fact("Fast", "is_a", "Speed")
    kb.add_fact("Slow", "is_a", "Speed")

    # ============================================================
    # ДВОСТОРОННІ ЗВ'ЯЗКИ: ЗБРОЯ ТА ХАРАКТЕРИСТИКИ
    # ============================================================

    # Longsword
    kb.add_fact("Longsword", "has", "Heavy")
    kb.add_fact("Longsword", "has", "Long")
    kb.add_fact("Longsword", "has", "HighDamage")
    kb.add_fact("Longsword", "has", "Slow")

    # Katana
    kb.add_fact("Katana", "has", "Medium")
    kb.add_fact("Katana", "has", "Long")
    kb.add_fact("Katana", "has", "HighDamage")
    kb.add_fact("Katana", "has", "Fast")

    # Rapier
    kb.add_fact("Rapier", "has", "Light")
    kb.add_fact("Rapier", "has", "Long")
    kb.add_fact("Rapier", "has", "MediumDamage")
    kb.add_fact("Rapier", "has", "Fast")

    # Stiletto
    kb.add_fact("Stiletto", "has", "Light")
    kb.add_fact("Stiletto", "has", "Short")
    kb.add_fact("Stiletto", "has", "MediumDamage")
    kb.add_fact("Stiletto", "has", "Fast")

    # BattleAxe
    kb.add_fact("BattleAxe", "has", "Heavy")
    kb.add_fact("BattleAxe", "has", "Long")
    kb.add_fact("BattleAxe", "has", "HighDamage")
    kb.add_fact("BattleAxe", "has", "Slow")

    # Longbow
    kb.add_fact("Longbow", "has", "Medium")
    kb.add_fact("Longbow", "has", "Long")
    kb.add_fact("Longbow", "has", "MediumDamage")
    kb.add_fact("Longbow", "has", "LongRange")

    # Pistol
    kb.add_fact("Pistol", "has", "Light")
    kb.add_fact("Pistol", "has", "Short")
    kb.add_fact("Pistol", "has", "MediumDamage")
    kb.add_fact("Pistol", "has", "ShortRange")
    kb.add_fact("Pistol", "has", "Fast")

    # Rifle
    kb.add_fact("Rifle", "has", "Medium")
    kb.add_fact("Rifle", "has", "Long")
    kb.add_fact("Rifle", "has", "HighDamage")
    kb.add_fact("Rifle", "has", "LongRange")

    # ============================================================
    # ІСТОРИЧНІ ПЕРІОДИ (для контексту)
    # ============================================================

    kb.add_fact("Period", "is_a", "Item")
    kb.add_fact("Medieval", "is_a", "Period")
    kb.add_fact("Renaissance", "is_a", "Period")
    kb.add_fact("Feudal", "is_a", "Period")
    kb.add_fact("Modern", "is_a", "Period")

    # Зброя має історичний період
    kb.add_fact("Longsword", "has", "Medieval")
    kb.add_fact("Claymore", "has", "Medieval")
    kb.add_fact("BattleAxe", "has", "Medieval")

    kb.add_fact("Rapier", "has", "Renaissance")

    kb.add_fact("Katana", "has", "Feudal")
    kb.add_fact("Tanto", "has", "Feudal")

    kb.add_fact("Pistol", "has", "Modern")
    kb.add_fact("Rifle", "has", "Modern")
    kb.add_fact("Shotgun", "has", "Modern")

    # ============================================================
    # СТИЛІ БОЮ
    # ============================================================

    kb.add_fact("CombatStyle", "is_a", "Item")
    kb.add_fact("Dueling", "is_a", "CombatStyle")
    kb.add_fact("HeavyStrike", "is_a", "CombatStyle")
    kb.add_fact("QuickAttack", "is_a", "CombatStyle")
    kb.add_fact("Archery", "is_a", "CombatStyle")
    kb.add_fact("Tactical", "is_a", "CombatStyle")

    # Зброя використовується для певних стилів
    kb.add_fact("Rapier", "has", "Dueling")
    kb.add_fact("Longsword", "has", "HeavyStrike")
    kb.add_fact("Katana", "has", "QuickAttack")
    kb.add_fact("Stiletto", "has", "QuickAttack")
    kb.add_fact("Longbow", "has", "Archery")
    kb.add_fact("Rifle", "has", "Tactical")

    # ============================================================
    # ПЕРЕХРЕСНІ ЗВ'ЯЗКИ (щоб різні види зброї були пов'язані)
    # ============================================================

    # Зброя з однаковими компонентами
    # Guard пов'язує мечі
    kb.add_fact("Guard", "part_of", "Sword")
    kb.add_fact("Sword", "has", "Guard")

    # Trigger пов'язує вогнепальну зброю та арбалет
    kb.add_fact("Trigger", "part_of", "Firearm")
    kb.add_fact("Firearm", "has", "Trigger")

    # String пов'язує луки
    kb.add_fact("String", "part_of", "Bow")
    kb.add_fact("Bow", "has", "String")

    # Steel - спільний матеріал для багатьох клинків
    kb.add_fact("Steel", "part_of", "Blade")
    kb.add_fact("Blade", "has", "Steel")

    return kb


def interactive_query(kb):
    """Розширений інтерактивний режим запитів для класифікації зброї"""
    print("\n" + "=" * 60)
    print("🔫 БАЗА ЗНАНЬ: КЛАСИФІКАЦІЯ ЗБРОЇ 🔫")
    print("=" * 60)
    print("\nДоступні команди:")
    print("  1. query <об'єкт1> <об'єкт2> - перевірити зв'язок")
    print("  2. relations <об'єкт> - показати всі зв'язки об'єкта")
    print("  3. hierarchy <об'єкт> [відношення] - показати ієрархію")
    print("  4. add <суб'єкт> <відношення> <об'єкт> - додати факт")
    print("  5. remove <суб'єкт> <відношення> <об'єкт> - видалити факт")
    print("  6. list entities - показати всі сутності")
    print("  7. list relations - показати всі типи відношень")
    print("  8. find <відношення> - знайти всі факти з цим відношенням")
    print("  9. export [файл] - експортувати базу в файл")
    print(" 10. import [файл] - імпортувати базу з файлу")
    print(" 11. examples - показати приклади запитів")
    print(" 12. stats - показати статистику бази")
    print(" 13. exit - вихід")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n💬 Запит: ").strip()

            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0].lower()

            if command == "exit":
                print("\n👋 До побачення!")
                break

            elif command == "query" and len(parts) >= 3:
                obj1, obj2 = parts[1], parts[2]
                found, path = kb.query_transitive(obj1, obj2)

                if found:
                    print(f"\n✅ ТАК! '{obj1}' пов'язаний з '{obj2}'")
                    print(f"\n🔗 Шлях зв'язку:")
                    for i, (s, rel, o) in enumerate(path, 1):
                        print(f"   {i}. {s} --[{rel}]--> {o}")
                else:
                    print(f"\n❌ НІ. '{obj1}' НЕ пов'язаний з '{obj2}'")

            elif command == "relations" and len(parts) >= 2:
                obj = parts[1]
                relations = kb.get_all_relations(obj)

                if relations:
                    print(f"\n📋 Відношення для '{obj}':")
                    for rel, target in relations:
                        print(f"   • {obj} --[{rel}]--> {target}")
                else:
                    print(f"\n❌ Не знайдено відношень для '{obj}'")

            elif command == "hierarchy" and len(parts) >= 2:
                obj = parts[1]
                relation = parts[2] if len(parts) >= 3 else "is_a"
                kb.print_hierarchy(obj, relation)

            elif command == "add" and len(parts) >= 4:
                subject, relation, obj = parts[1], parts[2], parts[3]
                success, message = kb.add_fact_interactive(subject, relation, obj)
                print(f"\n{message}")

            elif command == "remove" and len(parts) >= 4:
                subject, relation, obj = parts[1], parts[2], parts[3]
                success, message = kb.remove_fact(subject, relation, obj)
                print(f"\n{message}")

            elif command == "list" and len(parts) >= 2:
                subcommand = parts[1].lower()

                if subcommand == "entities":
                    entities = kb.list_all_entities()
                    print(f"\n📦 Всі сутності в базі ({len(entities)}):")
                    print("=" * 60)

                    # Групуємо по 4 колонки для компактності
                    for i in range(0, len(entities), 4):
                        row = entities[i:i + 4]
                        print("  ".join(f"{ent:20}" for ent in row))

                elif subcommand == "relations":
                    relations = kb.list_all_relations()
                    print(f"\n🔗 Типи відношень ({len(relations)}):")
                    for rel in relations:
                        count = len(kb.find_by_relation(rel))
                        print(f"   • {rel}: {count} фактів")
                else:
                    print("\n❌ Невідома підкоманда. Використовуйте: list entities або list relations")

            elif command == "find" and len(parts) >= 2:
                relation = parts[1]
                results = kb.find_by_relation(relation)

                if results:
                    print(f"\n🔍 Знайдено {len(results)} фактів з відношенням '{relation}':")
                    for s, o in results:
                        print(f"   • {s} --[{relation}]--> {o}")
                else:
                    print(f"\n❌ Не знайдено фактів з відношенням '{relation}'")

            elif command == "export":
                filename = parts[1] if len(parts) >= 2 else "kb_export.txt"
                success, message = kb.export_facts(filename)
                print(f"\n{message}")

            elif command == "import":
                filename = parts[1] if len(parts) >= 2 else "kb_export.txt"
                success, message = kb.import_facts(filename)
                print(f"\n{message}")

            elif command == "examples":
                print("\n" + "=" * 60)
                print("📚 ПРИКЛАДИ ЗАПИТІВ ДЛЯ КЛАСИФІКАЦІЇ ЗБРОЇ")
                print("=" * 60)
                print("\n🔍 Базові запити:")
                print("  query Longsword Weapon")
                print("  query Pistol Firearm")
                print("  query Steel Metal")
                print("\n🔧 Запити компонентів:")
                print("  query StraightBlade Longsword")
                print("  query Trigger Pistol")
                print("  query Barrel Rifle")
                print("\n➕ Додавання фактів:")
                print("  add NewSword is_a Sword")
                print("  add Katana has Sharpness")
                print("  add Blade part_of NewSword")
                print("\n➖ Видалення фактів:")
                print("  remove Katana has Sharpness")
                print("\n📋 Перегляд даних:")
                print("  relations Longsword")
                print("  list entities")
                print("  list relations")
                print("  find has")
                print("  find part_of")
                print("\n🌳 Ієрархії:")
                print("  hierarchy Weapon")
                print("  hierarchy Sword")
                print("  hierarchy Component")
                print("\n💾 Експорт/Імпорт:")
                print("  export weapon_kb.txt")
                print("  import weapon_kb.txt")

            elif command == "stats":
                print("\n" + "=" * 60)
                print("📊 СТАТИСТИКА БАЗИ ЗНАНЬ ПРО ЗБРОЮ")
                print("=" * 60)
                print(f"Всього фактів: {len(kb.facts)}")
                print(f"Всього унікальних сутностей: {len(kb.list_all_entities())}")

                relations_count = {}
                for _, rel, _ in kb.facts:
                    relations_count[rel] = relations_count.get(rel, 0) + 1

                print(f"\n🔗 Розподіл відношень:")
                for rel, count in sorted(relations_count.items(), key=lambda x: x[1], reverse=True):
                    bar = "█" * (count // 5)
                    print(f"  {rel:15} | {bar} {count}")

                # Статистика для зброї
                weapon_count = len([s for s, rel, o in kb.facts if
                                    rel == "is_a" and o in ["Weapon", "MeleeWeapon", "RangedWeapon",
                                                            "ExplosiveWeapon"]])
                component_count = len([s for s, rel, o in kb.facts if
                                       rel == "is_a" and o in ["Component", "Blade", "Handle", "Guard"]])
                material_count = len([s for s, rel, o in kb.facts if
                                      rel == "is_a" and o in ["Material", "Metal", "Wood", "Leather"]])

                print(f"\n🔫 Типи зброї: ~{weapon_count}")
                print(f"🔧 Компоненти: ~{component_count}")
                print(f"🏗️ Матеріали: ~{material_count}")

                # Популярні види зброї
                sword_count = len([s for s, rel, o in kb.facts if rel == "is_a" and o == "Sword"])
                firearm_count = len([s for s, rel, o in kb.facts if rel == "is_a" and o == "Firearm"])
                bow_count = len([s for s, rel, o in kb.facts if rel == "is_a" and o == "Bow"])

                print(f"\n🗡️ Мечів: {sword_count} видів")
                print(f"🔫 Вогнепальної зброї: {firearm_count} видів")
                print(f"🏹 Лук: {bow_count} видів")

            else:
                print("\n❌ Невідома команда. Введіть 'examples' для прикладів")

        except KeyboardInterrupt:
            print("\n\n👋 До побачення!")
            break
        except Exception as e:
            print(f"\n❌ Помилка: {e}")

if __name__ == "__main__":
    # Створити розширену базу знань
    kb = create_knowledge_base()

    # Інтерактивний режим
    interactive_query(kb)