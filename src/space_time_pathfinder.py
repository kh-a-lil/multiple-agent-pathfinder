from src.data import *


class PathFinder:
    def __init__(self, map: Graph):
        self.graph: Graph = map
        self.node_reservations: dict[tuple[str, int], int] = {}
        self.edge_reservations: dict[tuple[frozenset[str], int], int] = {}

    def djikstra(self):
        pass

    def looper(self):
        self.routs = []
        for drone in range(1, self.graph.nb_drones + 1):
            rout = self.djikstra()
            self.routs.append(rout)
            self.update_reservations(rout)
