class Edge:
    """Ребро графа - представляє відношення між вершинами"""

    def __init__(self, relation, target):
        self.relation = relation
        self.target = target  # цільова вершина

    def __str__(self):
        return f"--[{self.relation}]--> {self.target.name}"

    def __repr__(self):
        return self.__str__()