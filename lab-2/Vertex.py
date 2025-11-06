from Edge import Edge

class Vertex:
    """Вершина графа - представляє сутність у базі знань"""

    def __init__(self, name):
        self.name = name
        self.edges = []  # список ребер, що виходять з цієї вершини

    def add_edge(self, relation, target_vertex):
        """Додати ребро до вершини"""
        self.edges.append(Edge(relation, target_vertex))

    def get_edges_by_relation(self, relation):
        """Отримати всі ребра з певним типом відношення"""
        return [edge for edge in self.edges if edge.relation == relation]

    def has_direct_connection(self, target, relation=None):
        """Перевірити чи є пряме з'єднання з цільовою вершиною"""
        for edge in self.edges:
            if relation is None or edge.relation == relation:
                if edge.target.name == target:
                    return True, edge.relation
        return False, None

    def __str__(self):
        return f"Vertex({self.name})"

    def __repr__(self):
        return self.__str__()
