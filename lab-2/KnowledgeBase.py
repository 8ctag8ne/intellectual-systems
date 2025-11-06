#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
База знань про аніме та мангу
Реалізує ієрархію класів з відношеннями is_a, part_of, has
"""
import collections

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

    def query_transitive(self, subject, obj, relation_filter=None):
        """
        Перевірити транзитивний зв'язок між об'єктами
        Використовує BFS з відновленням шляху в кінці
        """
        if subject not in self.vertices or obj not in self.vertices:
            return False, []

        # BFS з відстеженням попередників
        queue = collections.deque([subject])
        visited = {subject}
        predecessor = {}  # vertex -> (previous_vertex, relation)

        while queue:
            current_name = queue.popleft()
            current_vertex = self.vertices[current_name]

            # Перевіряємо всі ребра з поточної вершини
            for edge in current_vertex.edges:
                # Застосовуємо фільтр відношення, якщо вказано
                if relation_filter and edge.relation != relation_filter:
                    continue

                neighbor_name = edge.target.name

                # Перевіряємо чи знайшли ціль
                if neighbor_name == obj:
                    # Відновлюємо шлях від цілі до початку
                    path = []
                    # Додаємо останній крок
                    path.append((current_name, edge.relation, neighbor_name))
                    # Відновлюємо решту шляху
                    node = current_name
                    while node in predecessor:
                        prev_node, rel = predecessor[node]
                        path.append((prev_node, rel, node))
                        node = prev_node
                    # Реверсуємо шлях (бо будували від кінця до початку)
                    path.reverse()
                    return True, path

                # Додаємо сусідні вершини в чергу
                if neighbor_name not in visited:
                    visited.add(neighbor_name)
                    predecessor[neighbor_name] = (current_name, edge.relation)
                    queue.append(neighbor_name)

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

    # Дистанційна зброя
    kb.add_fact("Bow", "is_a", "RangedWeapon")
    kb.add_fact("Firearm", "is_a", "RangedWeapon")
    kb.add_fact("Throwable", "is_a", "RangedWeapon")

    # Вибухівка
    kb.add_fact("Grenade", "is_a", "ExplosiveWeapon")
    kb.add_fact("Bomb", "is_a", "ExplosiveWeapon")

    # ВАЖЛИВО: Граната також метальна зброя (множинне успадкування)
    kb.add_fact("Grenade", "is_a", "Throwable")

    # РІВЕНЬ 4: Конкретні види
    # Мечі
    kb.add_fact("Longsword", "is_a", "Sword")
    kb.add_fact("Katana", "is_a", "Sword")
    kb.add_fact("Rapier", "is_a", "Sword")
    kb.add_fact("Shortsword", "is_a", "Sword")

    # Сокири
    kb.add_fact("BattleAxe", "is_a", "Axe")
    kb.add_fact("Hatchet", "is_a", "Axe")

    # Списи
    kb.add_fact("Pike", "is_a", "Spear")
    kb.add_fact("Javelin", "is_a", "Spear")

    # Кинджали
    kb.add_fact("Stiletto", "is_a", "Dagger")
    kb.add_fact("Tanto", "is_a", "Dagger")

    # Луки
    kb.add_fact("Longbow", "is_a", "Bow")
    kb.add_fact("Shortbow", "is_a", "Bow")

    # Вогнепальна зброя
    kb.add_fact("Pistol", "is_a", "Firearm")
    kb.add_fact("Rifle", "is_a", "Firearm")

    # Метальна зброя
    kb.add_fact("Shuriken", "is_a", "Throwable")
    kb.add_fact("ThrowingKnife", "is_a", "Throwable")

    # ============================================================
    # КОМПОНЕНТИ ЗБРОЇ
    # ============================================================

    kb.add_fact("Component", "is_a", "Item")
    kb.add_fact("Blade", "is_a", "Component")
    kb.add_fact("Handle", "is_a", "Component")
    kb.add_fact("Guard", "is_a", "Component")
    kb.add_fact("Pommel", "is_a", "Component")
    kb.add_fact("String", "is_a", "Component")
    kb.add_fact("Trigger", "is_a", "Component")
    kb.add_fact("Barrel", "is_a", "Component")
    kb.add_fact("Magazine", "is_a", "Component")

    # ============================================================
    # МАТЕРІАЛИ
    # ============================================================

    kb.add_fact("Material", "is_a", "Item")
    kb.add_fact("Metal", "is_a", "Material")
    kb.add_fact("Wood", "is_a", "Material")
    kb.add_fact("ExplosiveMaterial", "is_a", "Material")

    # Типи металів
    kb.add_fact("Steel", "is_a", "Metal")
    kb.add_fact("Iron", "is_a", "Metal")

    # Типи дерева
    kb.add_fact("Oak", "is_a", "Wood")
    kb.add_fact("Yew", "is_a", "Wood")

    # Вибухові речовини
    kb.add_fact("TNT", "is_a", "ExplosiveMaterial")
    kb.add_fact("Gunpowder", "is_a", "ExplosiveMaterial")

    # Хімічні елементи
    kb.add_fact("ChemicalElement", "is_a", "Material")
    kb.add_fact("Carbon", "is_a", "ChemicalElement")
    kb.add_fact("Nitrogen", "is_a", "ChemicalElement")

    # ============================================================
    # ЗВ'ЯЗКИ: ВСІМ МЕЧАМ СПІЛЬНИЙ Guard
    # ============================================================

    # Guard є частиною всіх мечів (через категорію)
    kb.add_fact("Guard", "part_of", "Sword")
    kb.add_fact("Sword", "has", "Guard")

    # Усі мечі мають леза
    kb.add_fact("Blade", "part_of", "Sword")
    kb.add_fact("Sword", "has", "Blade")

    # Усі мечі мають рукоятки
    kb.add_fact("Handle", "part_of", "Sword")
    kb.add_fact("Sword", "has", "Handle")

    # Довгі мечі мають Pommel
    kb.add_fact("Pommel", "part_of", "Longsword")
    kb.add_fact("Longsword", "has", "Pommel")

    kb.add_fact("Pommel", "part_of", "Rapier")
    kb.add_fact("Rapier", "has", "Pommel")

    # ============================================================
    # ЗВ'ЯЗКИ: ВСІМ ЛУКАМ СПІЛЬНИЙ String
    # ============================================================

    kb.add_fact("String", "part_of", "Bow")
    kb.add_fact("Bow", "has", "String")

    kb.add_fact("Handle", "part_of", "Bow")
    kb.add_fact("Bow", "has", "Handle")

    # ============================================================
    # ЗВ'ЯЗКИ: ВСІЙ ВОГНЕПАЛЬНІЙ ЗБРОЇ СПІЛЬНІ Barrel, Trigger, Magazine
    # ============================================================

    kb.add_fact("Barrel", "part_of", "Firearm")
    kb.add_fact("Firearm", "has", "Barrel")

    kb.add_fact("Trigger", "part_of", "Firearm")
    kb.add_fact("Firearm", "has", "Trigger")

    kb.add_fact("Magazine", "part_of", "Firearm")
    kb.add_fact("Firearm", "has", "Magazine")

    kb.add_fact("Handle", "part_of", "Firearm")
    kb.add_fact("Firearm", "has", "Handle")

    # ============================================================
    # ЗВ'ЯЗКИ: ВСІМ КИНДЖАЛАМ СПІЛЬНЕ Blade
    # ============================================================

    kb.add_fact("Blade", "part_of", "Dagger")
    kb.add_fact("Dagger", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Dagger")
    kb.add_fact("Dagger", "has", "Handle")

    # ============================================================
    # ЗВ'ЯЗКИ: СОКИРАМ СПІЛЬНЕ Blade і Handle
    # ============================================================

    kb.add_fact("Blade", "part_of", "Axe")
    kb.add_fact("Axe", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Axe")
    kb.add_fact("Axe", "has", "Handle")

    # ============================================================
    # ЗВ'ЯЗКИ: СПИСАМ СПІЛЬНЕ Handle
    # ============================================================

    kb.add_fact("Blade", "part_of", "Spear")
    kb.add_fact("Spear", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Spear")
    kb.add_fact("Spear", "has", "Handle")

    # ============================================================
    # ЗВ'ЯЗКИ: МАТЕРІАЛИ В КОМПОНЕНТАХ (єднає всі види зброї)
    # ============================================================

    # Blade зроблено зі Steel
    kb.add_fact("Steel", "part_of", "Blade")
    kb.add_fact("Blade", "has", "Steel")

    # Handle може бути з дерева або металу
    kb.add_fact("Oak", "part_of", "Handle")
    kb.add_fact("Handle", "has", "Oak")

    # kb.add_fact("Iron", "part_of", "Handle")
    # kb.add_fact("Handle", "has", "Iron")

    # Guard із металу
    kb.add_fact("Steel", "part_of", "Guard")
    kb.add_fact("Guard", "has", "Steel")

    # Pommel із металу
    kb.add_fact("Iron", "part_of", "Pommel")
    kb.add_fact("Pommel", "has", "Iron")

    # Barrel зі Steel
    kb.add_fact("Steel", "part_of", "Barrel")
    kb.add_fact("Barrel", "has", "Steel")

    # String з дерева Yew
    kb.add_fact("Yew", "part_of", "String")
    kb.add_fact("String", "has", "Yew")

    # ============================================================
    # ЗВ'ЯЗКИ: СТАЛЬ СКЛАДАЄТЬСЯ З ЗАЛІЗА ТА ВУГЛЕЦЮ
    # ============================================================

    kb.add_fact("Iron", "part_of", "Steel")
    kb.add_fact("Steel", "has", "Iron")

    kb.add_fact("Carbon", "part_of", "Steel")
    kb.add_fact("Steel", "has", "Carbon")

    # ============================================================
    # ЗВ'ЯЗКИ: ВИБУХІВКА
    # ============================================================

    # Граната містить TNT
    kb.add_fact("TNT", "part_of", "Grenade")
    kb.add_fact("Grenade", "has", "TNT")

    # Бомба містить TNT
    kb.add_fact("TNT", "part_of", "Bomb")
    kb.add_fact("Bomb", "has", "TNT")

    # TNT складається з хімічних елементів
    kb.add_fact("Nitrogen", "part_of", "TNT")
    kb.add_fact("TNT", "has", "Nitrogen")

    kb.add_fact("Carbon", "part_of", "TNT")
    kb.add_fact("TNT", "has", "Carbon")

    # Вогнепальна зброя використовує Gunpowder
    kb.add_fact("Gunpowder", "part_of", "Firearm")
    kb.add_fact("Firearm", "has", "Gunpowder")

    # Gunpowder містить Nitrogen
    kb.add_fact("Nitrogen", "part_of", "Gunpowder")
    kb.add_fact("Gunpowder", "has", "Nitrogen")

    kb.add_fact("Carbon", "part_of", "Gunpowder")
    kb.add_fact("Gunpowder", "has", "Carbon")

    # ============================================================
    # ДОДАТКОВІ ПРАВИЛА ДЛЯ ПОВ'ЯЗУВАННЯ СУТНОСТЕЙ
    # ============================================================

    # ============================================================
    # 1. ПОВ'ЯЗУВАННЯ МЕЧІВ МІЖ СОБОЮ
    # ============================================================

    # Конкретні мечі успадковують компоненти від Sword
    # Longsword має всі компоненти Sword
    kb.add_fact("Guard", "part_of", "Longsword")
    kb.add_fact("Longsword", "has", "Guard")

    kb.add_fact("Blade", "part_of", "Longsword")
    kb.add_fact("Longsword", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Longsword")
    kb.add_fact("Longsword", "has", "Handle")

    # Shortsword має всі компоненти Sword
    kb.add_fact("Guard", "part_of", "Shortsword")
    kb.add_fact("Shortsword", "has", "Guard")

    kb.add_fact("Blade", "part_of", "Shortsword")
    kb.add_fact("Shortsword", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Shortsword")
    kb.add_fact("Shortsword", "has", "Handle")

    # Katana має всі компоненти Sword
    kb.add_fact("Guard", "part_of", "Katana")
    kb.add_fact("Katana", "has", "Guard")

    kb.add_fact("Blade", "part_of", "Katana")
    kb.add_fact("Katana", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Katana")
    kb.add_fact("Katana", "has", "Handle")

    # Rapier має всі компоненти Sword
    kb.add_fact("Guard", "part_of", "Rapier")
    kb.add_fact("Rapier", "has", "Guard")

    kb.add_fact("Blade", "part_of", "Rapier")
    kb.add_fact("Rapier", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Rapier")
    kb.add_fact("Rapier", "has", "Handle")

    # ============================================================
    # 2. ПОВ'ЯЗУВАННЯ СОКИР З МЕЧАМИ ТА ІНШОЮ ЗБРОЄЮ
    # ============================================================

    # Конкретні сокири успадковують компоненти від Axe
    kb.add_fact("Blade", "part_of", "BattleAxe")
    kb.add_fact("BattleAxe", "has", "Blade")

    kb.add_fact("Handle", "part_of", "BattleAxe")
    kb.add_fact("BattleAxe", "has", "Handle")

    kb.add_fact("Blade", "part_of", "Hatchet")
    kb.add_fact("Hatchet", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Hatchet")
    kb.add_fact("Hatchet", "has", "Handle")

    # ============================================================
    # 3. ПОВ'ЯЗУВАННЯ КИНДЖАЛІВ
    # ============================================================

    kb.add_fact("Blade", "part_of", "Stiletto")
    kb.add_fact("Stiletto", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Stiletto")
    kb.add_fact("Stiletto", "has", "Handle")

    kb.add_fact("Blade", "part_of", "Tanto")
    kb.add_fact("Tanto", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Tanto")
    kb.add_fact("Tanto", "has", "Handle")

    # ============================================================
    # 4. ПОВ'ЯЗУВАННЯ СПИСІВ
    # ============================================================

    kb.add_fact("Blade", "part_of", "Pike")
    kb.add_fact("Pike", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Pike")
    kb.add_fact("Pike", "has", "Handle")

    kb.add_fact("Blade", "part_of", "Javelin")
    kb.add_fact("Javelin", "has", "Blade")

    kb.add_fact("Handle", "part_of", "Javelin")
    kb.add_fact("Javelin", "has", "Handle")

    # ============================================================
    # 5. ПОВ'ЯЗУВАННЯ ЛУКІВ
    # ============================================================

    kb.add_fact("String", "part_of", "Longbow")
    kb.add_fact("Longbow", "has", "String")

    kb.add_fact("Handle", "part_of", "Longbow")
    kb.add_fact("Longbow", "has", "Handle")

    kb.add_fact("String", "part_of", "Shortbow")
    kb.add_fact("Shortbow", "has", "String")

    kb.add_fact("Handle", "part_of", "Shortbow")
    kb.add_fact("Shortbow", "has", "Handle")

    # ============================================================
    # 6. ПОВ'ЯЗУВАННЯ ВОГНЕПАЛЬНОЇ ЗБРОЇ
    # ============================================================

    # Pistol має всі компоненти Firearm
    kb.add_fact("Barrel", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "Barrel")

    kb.add_fact("Trigger", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "Trigger")

    kb.add_fact("Magazine", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "Magazine")

    kb.add_fact("Handle", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "Handle")

    kb.add_fact("Gunpowder", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "Gunpowder")

    # Rifle має всі компоненти Firearm
    kb.add_fact("Barrel", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Barrel")

    kb.add_fact("Trigger", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Trigger")

    kb.add_fact("Magazine", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Magazine")

    kb.add_fact("Handle", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Handle")

    kb.add_fact("Gunpowder", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Gunpowder")

    # ============================================================
    # 7. ДОДАТКОВІ ЗВ'ЯЗКИ МАТЕРІАЛІВ З КОНКРЕТНОЮ ЗБРОЄЮ
    # ============================================================

    # Katana з дерев'яною рукояткою Oak
    kb.add_fact("Oak", "part_of", "Katana")
    kb.add_fact("Katana", "has", "Oak")

    # Rifle з дерев'яною рукояткою Oak
    kb.add_fact("Oak", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Oak")

    # Longbow з дерева Yew
    kb.add_fact("Yew", "part_of", "Longbow")
    kb.add_fact("Longbow", "has", "Yew")

    # BattleAxe зі сталі
    kb.add_fact("Steel", "part_of", "BattleAxe")
    kb.add_fact("BattleAxe", "has", "Steel")

    # Longsword зі сталі
    kb.add_fact("Steel", "part_of", "Longsword")
    kb.add_fact("Longsword", "has", "Steel")

    # Katana зі сталі
    kb.add_fact("Steel", "part_of", "Katana")
    kb.add_fact("Katana", "has", "Steel")

    # Pistol зі сталі
    kb.add_fact("Steel", "part_of", "Pistol")
    kb.add_fact("Pistol", "has", "Steel")

    # Rifle зі сталі
    kb.add_fact("Steel", "part_of", "Rifle")
    kb.add_fact("Rifle", "has", "Steel")

    # ============================================================
    # 8. ПОВ'ЯЗУВАННЯ МЕТАЛЬНОЇ ЗБРОЇ
    # ============================================================

    kb.add_fact("Blade", "part_of", "ThrowingKnife")
    kb.add_fact("ThrowingKnife", "has", "Blade")

    kb.add_fact("Handle", "part_of", "ThrowingKnife")
    kb.add_fact("ThrowingKnife", "has", "Handle")

    kb.add_fact("Steel", "part_of", "Shuriken")
    kb.add_fact("Shuriken", "has", "Steel")

    # ============================================================
    # 9. ДОДАТКОВІ ЗВ'ЯЗКИ ДЛЯ IRON ТА OAK
    # ============================================================

    # Iron також у різних компонентах
    kb.add_fact("Iron", "part_of", "Blade")
    kb.add_fact("Blade", "has", "Iron")

    kb.add_fact("Iron", "part_of", "Barrel")
    kb.add_fact("Barrel", "has", "Iron")

    # Oak у багатьох рукоятках
    kb.add_fact("Oak", "part_of", "Longbow")
    kb.add_fact("Longbow", "has", "Oak")

    kb.add_fact("Oak", "part_of", "BattleAxe")
    kb.add_fact("BattleAxe", "has", "Oak")

    kb.add_fact("Oak", "part_of", "Pike")
    kb.add_fact("Pike", "has", "Oak")

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