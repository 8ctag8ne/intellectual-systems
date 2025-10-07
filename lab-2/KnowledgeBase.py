#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
База знань про аніме та мангу
Реалізує ієрархію класів з відношеннями is_a, part_of, has
"""
from Vertex import *

class OptimizedKnowledgeBase:
    """Оптимізована база знань на основі графа"""

    def __init__(self):
        self.vertices = {}  # словник вершин: name -> Vertex
        self.relation_types = set()

    def get_or_create_vertex(self, name):
        """Отримати вершину за ім'ям або створити нову"""
        if name not in self.vertices:
            self.vertices[name] = Vertex(name)
        return self.vertices[name]

    def add_fact(self, subject, relation, obj):
        """Додати факт до бази знань"""
        subject_vertex = self.get_or_create_vertex(subject)
        obj_vertex = self.get_or_create_vertex(obj)

        subject_vertex.add_edge(relation, obj_vertex)
        self.relation_types.add(relation)

        return True, f"✅ Додано: {subject} --[{relation}]--> {obj}"

    def query_direct(self, subject, obj, relation=None):
        """Перевірити пряме відношення між об'єктами"""
        if subject not in self.vertices or obj not in self.vertices:
            return False, None

        subject_vertex = self.vertices[subject]
        return subject_vertex.has_direct_connection(obj, relation)

    def query_transitive(self, subject, obj, relation_filter=None, visited=None):
        """
        Перевірити транзитивний зв'язок між об'єктами
        Використовує BFS для ефективного пошуку
        """
        if subject not in self.vertices or obj not in self.vertices:
            return False, []

        if visited is None:
            visited = set()

        # BFS для знаходження шляху
        queue = [(self.vertices[subject], [])]  # (current_vertex, path)
        visited.add(subject)

        while queue:
            current_vertex, path = queue.pop(0)

            # Перевіряємо всі ребра з поточної вершини
            for edge in current_vertex.edges:
                # Застосовуємо фільтр відношення, якщо вказано
                if relation_filter and edge.relation != relation_filter:
                    continue

                # Перевіряємо чи знайшли ціль
                if edge.target.name == obj:
                    full_path = path + [(current_vertex.name, edge.relation, edge.target.name)]
                    return True, full_path

                # Додаємо сусідні вершини в чергу
                if edge.target.name not in visited:
                    visited.add(edge.target.name)
                    new_path = path + [(current_vertex.name, edge.relation, edge.target.name)]
                    queue.append((edge.target, new_path))

        return False, []

    def get_all_relations(self, subject):
        """Отримати всі відношення для об'єкта"""
        if subject not in self.vertices:
            return []

        relations = []
        for edge in self.vertices[subject].edges:
            relations.append((edge.relation, edge.target.name))
        return relations

    def get_hierarchy(self, root_name, relation="is_a"):
        """Отримати ієрархію для об'єкта за допомогою BFS"""
        if root_name not in self.vertices:
            return []

        hierarchy = []
        queue = [(self.vertices[root_name], 0)]  # (vertex, level)
        visited = set([root_name])

        while queue:
            current_vertex, level = queue.pop(0)
            hierarchy.append((level, current_vertex.name))

            # Знаходимо всіх нащадків за вказаним відношенням
            for edge in current_vertex.edges:
                if edge.relation == relation and edge.target.name not in visited:
                    visited.add(edge.target.name)
                    queue.append((edge.target, level + 1))

        return hierarchy

    def print_hierarchy(self, root, relation="is_a"):
        """Красиво вивести ієрархію"""
        hierarchy = self.get_hierarchy(root, relation)

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
        if subject not in self.vertices:
            return False, f"❌ Вершина не знайдена: {subject}"

        subject_vertex = self.vertices[subject]

        # Шукаємо та видаляємо ребро
        for i, edge in enumerate(subject_vertex.edges):
            if edge.relation == relation and edge.target.name == obj:
                del subject_vertex.edges[i]
                return True, f"✅ Факт видалено: {subject} --[{relation}]--> {obj}"

        return False, f"❌ Факт не знайдено: {subject} --[{relation}]--> {obj}"

    def list_all_entities(self):
        """Отримати список всіх унікальних сутностей"""
        return sorted(self.vertices.keys())

    def list_all_relations(self):
        """Отримати список всіх типів відношень"""
        return sorted(self.relation_types)

    def find_by_relation(self, relation):
        """Знайти всі факти з певним типом відношення"""
        results = []
        for vertex_name, vertex in self.vertices.items():
            for edge in vertex.edges:
                if edge.relation == relation:
                    results.append((vertex_name, edge.target.name))
        return results

    def export_facts(self, filename="kb_export.txt"):
        """Експортувати базу знань у файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for vertex_name, vertex in sorted(self.vertices.items()):
                    for edge in vertex.edges:
                        f.write(f"{vertex_name},{edge.relation},{edge.target.name}\n")
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
                            self.add_fact(parts[0], parts[1], parts[2])
                            count += 1
            return True, f"✅ Імпортовано {count} фактів з {filename}"
        except Exception as e:
            return False, f"❌ Помилка імпорту: {e}"

    def get_statistics(self):
        """Отримати статистику бази знань"""
        total_vertices = len(self.vertices)
        total_edges = sum(len(vertex.edges) for vertex in self.vertices.values())

        relation_stats = {}
        for vertex in self.vertices.values():
            for edge in vertex.edges:
                relation_stats[edge.relation] = relation_stats.get(edge.relation, 0) + 1

        return {
            'vertices': total_vertices,
            'edges': total_edges,
            'relations': relation_stats
        }


def create_optimized_weapon_kb():
    """
    Створення оптимізованої бази знань про зброю
    Використовує ту саму логіку, але з новою структурою даних
    """
    kb = OptimizedKnowledgeBase()
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
    kb.add_fact("Grenade", "is_a", "Throwable")
    kb.add_fact("Bomb", "is_a", "Throwable")

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
    kb.add_fact("Copper", "is_a", "Metal")
    kb.add_fact("Aluminum", "is_a", "Metal")

    # Вибухові матеріали - ДЕТАЛЬНА ІЄРАРХІЯ
    kb.add_fact("ExplosiveMaterial", "is_a", "Material")
    kb.add_fact("HighExplosive", "is_a", "ExplosiveMaterial")
    kb.add_fact("LowExplosive", "is_a", "ExplosiveMaterial")
    kb.add_fact("PrimaryExplosive", "is_a", "ExplosiveMaterial")
    kb.add_fact("SecondaryExplosive", "is_a", "ExplosiveMaterial")

    # Конкретні вибухові речовини
    kb.add_fact("TNT", "is_a", "HighExplosive")
    kb.add_fact("TNT", "is_a", "SecondaryExplosive")
    kb.add_fact("RDX", "is_a", "HighExplosive")  # Hexogen
    kb.add_fact("RDX", "is_a", "SecondaryExplosive")
    kb.add_fact("PETN", "is_a", "HighExplosive")
    kb.add_fact("CompositionC4", "is_a", "HighExplosive")
    kb.add_fact("Dynamite", "is_a", "HighExplosive")
    kb.add_fact("Gunpowder", "is_a", "LowExplosive")
    kb.add_fact("Nitroglycerin", "is_a", "PrimaryExplosive")
    kb.add_fact("LeadAzide", "is_a", "PrimaryExplosive")

    # Хімічні елементи
    kb.add_fact("ChemicalElement", "is_a", "Material")
    kb.add_fact("Carbon", "is_a", "ChemicalElement")
    kb.add_fact("Nitrogen", "is_a", "ChemicalElement")
    kb.add_fact("Oxygen", "is_a", "ChemicalElement")
    kb.add_fact("Hydrogen", "is_a", "ChemicalElement")

    # Типи дерева
    kb.add_fact("Oak", "is_a", "Wood")
    kb.add_fact("Ash", "is_a", "Wood")
    kb.add_fact("Yew", "is_a", "Wood")

    # TNT складається з хімічних елементів
    kb.add_fact("Nitrogen", "part_of", "TNT")
    kb.add_fact("TNT", "has", "Nitrogen")
    kb.add_fact("Oxygen", "part_of", "TNT")
    kb.add_fact("TNT", "has", "Oxygen")
    kb.add_fact("Hydrogen", "part_of", "TNT")
    kb.add_fact("TNT", "has", "Hydrogen")

    # RDX (Hexogen) також має схожий склад
    kb.add_fact("Nitrogen", "part_of", "RDX")
    kb.add_fact("RDX", "has", "Nitrogen")
    kb.add_fact("Oxygen", "part_of", "RDX")
    kb.add_fact("RDX", "has", "Oxygen")
    kb.add_fact("Hydrogen", "part_of", "RDX")
    kb.add_fact("RDX", "has", "Hydrogen")

    # Порох також має ці елементи
    kb.add_fact("Nitrogen", "part_of", "Gunpowder")
    kb.add_fact("Gunpowder", "has", "Nitrogen")
    kb.add_fact("Oxygen", "part_of", "Gunpowder")
    kb.add_fact("Gunpowder", "has", "Oxygen")

    # Сталь складається з заліза та вуглецю
    kb.add_fact("Iron", "part_of", "Steel")
    kb.add_fact("Steel", "has", "Iron")
    kb.add_fact("Carbon", "part_of", "Steel")
    kb.add_fact("Steel", "has", "Carbon")

    # Граната містить TNT
    kb.add_fact("TNT", "part_of", "Grenade")
    kb.add_fact("Grenade", "has", "TNT")

    # Бомба містить RDX (Composition C4)
    kb.add_fact("RDX", "part_of", "Bomb")
    kb.add_fact("Bomb", "has", "RDX")
    kb.add_fact("CompositionC4", "part_of", "Bomb")
    kb.add_fact("Bomb", "has", "CompositionC4")

    # Гвинтівка містить сталь та порох
    kb.add_fact("Steel", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Steel")

    kb.add_fact("Casing", "part_of", "Grenade")
    kb.add_fact("Grenade", "has", "Casing")
    kb.add_fact("Casing", "part_of", "Bomb")
    kb.add_fact("Bomb", "has", "Casing")

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

    # Спільні властивості через матеріали
    kb.add_fact("ExplosiveMaterial", "has", "ExplosiveProperty")
    kb.add_fact("TNT", "has", "HighExplosive")
    kb.add_fact("Hexogen", "has", "VeryHighExplosive")
    kb.add_fact("Gunpowder", "has", "LowExplosive")

    # Властивості зброї, що походять від матеріалів
    kb.add_fact("Grenade", "has", "ExplosiveDamage")  # бо має TNT
    kb.add_fact("Bomb", "has", "ExplosiveDamage")  # бо має Hexogen
    kb.add_fact("Firearm", "has", "KineticDamage")  # бо має Gunpowder


    # Детонатор може використовуватись у різних вибухових пристроях
    kb.add_fact("Detonator", "part_of", "Bomb")
    kb.add_fact("Bomb", "has", "Detonator")
    kb.add_fact("Detonator", "part_of", "Mine")
    kb.add_fact("Mine", "has", "Detonator")

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


def optimized_interactive_query(kb):
    """Інтерактивний режим для оптимізованої бази знань"""
    print("\n" + "=" * 60)
    print("⚡ ОПТИМІЗОВАНА БАЗА ЗНАНЬ: КЛАСИФІКАЦІЯ ЗБРОЇ ⚡")
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
    print("  9. stats - показати статистику")
    print(" 10. exit - вихід")
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
                    print(f"\n🔗 Шлях зв'язку ({len(path)} кроків):")
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
                success, message = kb.add_fact(subject, relation, obj)
                print(f"\n{message}")

            elif command == "remove" and len(parts) >= 4:
                subject, relation, obj = parts[1], parts[2], parts[3]
                success, message = kb.remove_fact(subject, relation, obj)
                print(f"\n{message}")

            elif command == "list" and len(parts) >= 2:
                subcommand = parts[1].lower()
                if subcommand == "entities":
                    entities = kb.list_all_entities()
                    print(f"\n📦 Всі сутності ({len(entities)}):")
                    for i in range(0, len(entities), 4):
                        row = entities[i:i + 4]
                        print("  ".join(f"{ent:20}" for ent in row))
                elif subcommand == "relations":
                    relations = kb.list_all_relations()
                    print(f"\n🔗 Типи відношень ({len(relations)}):")
                    for rel in relations:
                        count = len(kb.find_by_relation(rel))
                        print(f"   • {rel}: {count} фактів")

            elif command == "find" and len(parts) >= 2:
                relation = parts[1]
                results = kb.find_by_relation(relation)
                if results:
                    print(f"\n🔍 Знайдено {len(results)} фактів з відношенням '{relation}':")
                    for s, o in results:
                        print(f"   • {s} --[{relation}]--> {o}")
                else:
                    print(f"\n❌ Не знайдено фактів з відношенням '{relation}'")

            elif command == "stats":
                stats = kb.get_statistics()
                print(f"\n📊 СТАТИСТИКА БАЗИ:")
                print(f"   Вершин: {stats['vertices']}")
                print(f"   Ребер: {stats['edges']}")
                print(f"   Щільність графа: {stats['edges'] / stats['vertices']:.2f} ребер/вершину")
                print(f"\n📈 Розподіл відношень:")
                for rel, count in sorted(stats['relations'].items(), key=lambda x: x[1], reverse=True):
                    bar = "█" * min(count // 3, 20)  # Нормалізуємо для відображення
                    print(f"   {rel:15} | {bar} {count}")

            else:
                print("\n❌ Невідома команда. Спробуйте: query, relations, hierarchy, add, remove, list, find, stats")

        except KeyboardInterrupt:
            print("\n\n👋 До побачення!")
            break
        except Exception as e:
            print(f"\n❌ Помилка: {e}")


if __name__ == "__main__":
    # Створюємо оптимізовану базу знань
    kb = create_optimized_weapon_kb()

    # Запускаємо інтерактивний режим
    optimized_interactive_query(kb)