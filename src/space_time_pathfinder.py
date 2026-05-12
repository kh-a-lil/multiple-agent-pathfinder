from src.data import *
import heapq


class PathFinder:
    def __init__(self, map: Graph):
        self.graph: Graph = map
        self.node_reservations: dict[tuple[str, int], int] = {}
        self.edge_reservations: dict[tuple[frozenset[str], int], int] = {}
        self.tea = 0
        self.looper()

    def construct_path(self, memory: dict[tuple[str, int], tuple[str, int]]):
        m_len = len(memory) - 1
        path = []
        dest = list(memory.keys())[-1]
        while m_len >= 0:
            if list(memory.keys())[m_len] == dest:
                path.append(dest)
                dest = list(memory.values())[m_len]
            m_len -= 1
        path.reverse()
        self.tea += 1
        return path

    def djikstra(self):
        queue: list[(int, Zone, str)] = []
        visited: set[str, int] = set()
        memory: dict[tuple[str, int], tuple[str, int]] = {}
        heapq.heappush(queue, (0, self.graph.zones[self.graph.start_hub], None))
        while queue:
            curr_turn, curr_zone, came_from = heapq.heappop(queue)
            if came_from == curr_zone.name:
                memory[(curr_zone.name, curr_turn)] = (came_from, curr_turn - 1)
            elif curr_zone.zone_type == "restricted":
                memory[(came_from + "-" + curr_zone.name, curr_turn - 1)] = (came_from, curr_turn - 2)
                memory[(curr_zone.name, curr_turn)] = (came_from + "-" + curr_zone.name, curr_turn - 1)
            else:
                memory[(curr_zone.name, curr_turn)] = (came_from, curr_turn - 1)
            if curr_zone == self.graph.zones[self.graph.end_hub]:
                return self.construct_path(memory)
            if (curr_zone.name, curr_turn) in visited:
                continue
            visited.add((curr_zone.name, curr_turn))
            next_turn: int = curr_turn + 1
            if (
                self.node_reservations.get((curr_zone.name, next_turn), 0)
                < curr_zone.max_drones
            ):
                if (curr_zone.name, next_turn) in visited:
                    continue
                heapq.heappush(queue, (next_turn, curr_zone, curr_zone.name))
            for n in self.graph.adj_list[curr_zone.name]:
                neighbor = self.graph.zones[n]
                if (
                    neighbor.zone_type == ZoneType.NORMAL
                    or neighbor.zone_type == ZoneType.PRIORITY
                ):
                    next_turn = curr_turn + 1
                    if (neighbor.name, next_turn) in visited:
                        continue
                    if (
                        self.node_reservations.get((neighbor.name, next_turn), 0)
                        < neighbor.max_drones
                    ):
                        if (
                            self.edge_reservations.get(
                                (frozenset([curr_zone.name, neighbor.name]), curr_turn), 0
                            )
                            < self.graph.connections[
                                frozenset([curr_zone.name, neighbor.name])
                            ].max_link_capacity
                        ):
                            heapq.heappush(queue, (next_turn, neighbor, curr_zone.name))
                if neighbor.zone_type == ZoneType.RESTRICTED:
                    next_turn = curr_turn + 2
                    if (neighbor.name, next_turn) in visited:
                        continue
                    if (
                        self.node_reservations.get((neighbor.name, next_turn), 0)
                        < neighbor.max_drones
                    ):
                        if (
                            self.edge_reservations.get(
                                (frozenset([curr_zone.name, neighbor.name]), curr_turn), 0
                            )
                            < self.graph.connections[
                                frozenset([curr_zone.name, neighbor.name])
                            ].max_link_capacity
                            and self.edge_reservations.get(
                                (frozenset([curr_zone.name, neighbor.name]), curr_turn + 1), 0
                            )
                            < self.graph.connections[
                                frozenset([curr_zone.name, neighbor.name])
                            ].max_link_capacity
                        ):
                            heapq.heappush(queue, (next_turn, neighbor, curr_zone.name))

    def update_reservations(self, rout):
        for item in rout:
            if self.node_reservations.get(item, 0):
                self.node_reservations[item] += 1
            else:
                self.node_reservations[item] = 1


    def looper(self):
        self.routs = {}
        for i in range(1, self.graph.nb_drones + 1):
            rout = self.djikstra()
            self.routs[i] = rout
            self.update_reservations(rout)
        print(self.routs)
