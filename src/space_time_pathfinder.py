from src.data import *
import heapq
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

class PathFinder:
    def __init__(self, map: Graph):
        self.graph: Graph = map
        self.node_reservations: dict[tuple[str, int], int] = {}
        self.edge_reservations: dict[tuple[frozenset[str, str], int], int] = {}
        self.looper()

    def construct_path(self, memory: dict[tuple[str, int], tuple[str, int]]):
        path = []
        node = list(memory.keys())[-1]
        while node[0]:
            path.append(node)
            node = memory[node]
        path.reverse()
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
                con: Connection = self.graph.connections.get(frozenset((came_from, curr_zone.name)), 0)
                if con and con.zone1 == came_from:
                    memory[(came_from + "-" + curr_zone.name, curr_turn - 1)] = (came_from, curr_turn - 2)
                    memory[(curr_zone.name, curr_turn)] = (came_from + "-" + curr_zone.name, curr_turn - 1)
                else:
                    memory[(curr_zone.name + "-" + came_from, curr_turn - 1)] = (came_from, curr_turn - 2)
                    memory[(curr_zone.name, curr_turn)] = (curr_zone.name + "-" + came_from, curr_turn - 1)
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
                    next_turn = curr_turn + 1 if neighbor.zone_type == ZoneType.NORMAL else curr_turn + 1.1
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
                        ) and (
                            self.edge_reservations.get(
                                (frozenset([curr_zone.name, neighbor.name]), curr_turn + 1), 0
                            )
                            < self.graph.connections[
                                frozenset([curr_zone.name, neighbor.name])
                            ].max_link_capacity
                        ):
                            heapq.heappush(queue, (next_turn, neighbor, curr_zone.name))

    def visualize(self):
        pos = {z.name: (z.x, -z.y) for z in self.graph.zones.values()}
        for edge in self.graph.connections.keys():
            n1, n2 = tuple(edge)
            pos[f"{n1}-{n2}"] = pos[f"{n2}-{n1}"] = ((pos[n1][0]+pos[n2][0])/2, (pos[n1][1]+pos[n2][1])/2)
        max_turn = max((t for p in self.routs.values() for _, t in p), default=0)
        current_turn = 0
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.canvas.manager.set_window_title('Fly-In Simulation')
        fig.patch.set_facecolor("#1e1e2e")
        def draw():
            ax.clear()
            ax.set_facecolor("#1e1e2e")
            ax.axis("equal")
            ax.axis("off")
            ax.set_title(f"Turn {current_turn} / {max_turn}\n(ENTER: Next | BACKSPACE: Prev)", color="white", pad=10)
            for edge in self.graph.connections.keys():
                n1, n2 = tuple(edge)
                ax.plot([pos[n1][0], pos[n2][0]], [pos[n1][1], pos[n2][1]], color="#585b70", lw=2, zorder=1)
            for z in self.graph.zones.values():
                c = getattr(z, 'color', None)
                c = c if mcolors.is_color_like(c) else '#89b4fa'
                ax.scatter(pos[z.name][0], pos[z.name][1], s=600, color=c, edgecolors="white", zorder=2)
                ax.text(pos[z.name][0], pos[z.name][1] - 0.3, z.name, color="#a6adc8", ha="center", fontsize=9)
            groups = {}
            for d_id, path in self.routs.items():
                loc = next((l for l, t in reversed(path) if t <= current_turn), path[0][0])
                groups.setdefault(loc, []).append(d_id)
            for loc, drones in groups.items():
                x, y = pos[loc]
                ax.scatter(x, y, s=300, color="#f38ba8", zorder=3)
                lbl = f"D{drones[0]}" + (f"+{len(drones)-1}" if len(drones) > 1 else "")
                ax.text(x, y, lbl, color="black", ha="center", va="center", fontweight="bold", fontsize=8, zorder=4)
            fig.canvas.draw()
        def on_key(event):
            nonlocal current_turn
            if event.key == 'enter' and current_turn < max_turn:
                current_turn += 1
                draw()
            elif event.key == 'backspace' and current_turn > 0:
                current_turn -= 1
                draw()
        fig.canvas.mpl_connect('key_press_event', on_key)
        draw()
        plt.show()

    def update_reservations(self, rout):
            for i in range(len(rout)):
                loc, t = rout[i]
                self.node_reservations[(loc, t)] = self.node_reservations.get((loc, t), 0) + 1
                if i < len(rout) - 1:
                    next_loc, next_t = rout[i+1]
                    if loc != next_loc:
                        # normal
                        if "-" not in loc and "-" not in next_loc:
                            edge = frozenset([loc, next_loc])
                            self.edge_reservations[(edge, t)] = self.edge_reservations.get((edge, t), 0) + 1
                        # restricted
                        elif "-" not in loc and "-" in next_loc:
                            edge = frozenset(next_loc.split("-"))
                            self.edge_reservations[(edge, t)] = self.edge_reservations.get((edge, t), 0) + 1
                            self.edge_reservations[(edge, t + 1)] = self.edge_reservations.get((edge, t), 0) + 1

    def looper(self):
        self.routs = {}
        for i in range(1, self.graph.nb_drones + 1):
            rout = self.djikstra()
            self.routs[i] = rout
            self.update_reservations(rout)
        self.visualize()
