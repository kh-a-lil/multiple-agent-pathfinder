from src.data import *
import heapq
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.animation import FuncAnimation, PillowWriter


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
                    next_turn = curr_turn + 1 # if neighbor.zone_type == ZoneType.NORMAL else curr_turn + 1
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

    def visualize_tmp(self, filename="simulation.mp4"):
        print(f"Generating smooth visualization: {filename}...")

        # --- 1. BUILD POSITIONS ---
        pos = {}
        for zone in self.graph.zones.values():
            pos[zone.name] = (zone.x, -zone.y)

        for edge_set in self.graph.connections.keys():
            n1, n2 = list(edge_set)
            x_mid = (pos[n1][0] + pos[n2][0]) / 2
            y_mid = (pos[n1][1] + pos[n2][1]) / 2
            pos[f"{n1}-{n2}"] = (x_mid, y_mid)
            pos[f"{n2}-{n1}"] = (x_mid, y_mid)

        # --- 2. BUILD CONTINUOUS TIMELINES PER DRONE ---
        max_turn = max(max(t for loc, t in path) for path in self.routs.values()) if self.routs else 0
        drone_timelines = {}

        for d_id, path in self.routs.items():
            path_dict = {t: loc for loc, t in path}
            full_timeline = []
            last_loc = path[0][0]

            # Fill every single turn so the drone always has a known location
            for t in range(max_turn + 1):
                if t in path_dict:
                    last_loc = path_dict[t]
                full_timeline.append(last_loc)

            drone_timelines[d_id] = full_timeline

        # --- 3. THEME & COLORS ---
        BG = "#0B1220"
        EDGE = "#94A3B8"
        DEFAULT_NODE = "#6366F1"
        TEXT = "#F8FAFC"
        DRONE_COLOR = "#22D3EE" # Cyan for the actual drones

        THEME_COLORS = {
            "red": "#991B1B", "green": "#065F46", "blue": "#1E40AF",
            "yellow": "#B45309", "orange": "#C2410C", "purple": "#5B21B6",
            "gray": "#334155", "grey": "#334155", "white": "#94A3B8",
            "black": "#000000", "pink": "#9D174D", "cyan": "#155E75",
        }

        def get_node_color(color_name):
            if not color_name: return DEFAULT_NODE
            c_lower = color_name.lower()
            if c_lower in THEME_COLORS: return THEME_COLORS[c_lower]
            try: return mcolors.to_hex(color_name)
            except ValueError: return DEFAULT_NODE

        # --- 4. DYNAMIC SCALING SETUP ---
        num_zones = len(self.graph.zones)
        is_massive = num_zones > 20
        fig_width = 20 if is_massive else 10
        fig, ax = plt.subplots(figsize=(fig_width, 6), dpi=150)

        xs = [coord[0] for coord in pos.values()]
        ys = [coord[1] for coord in pos.values()]
        x_margin = (max(xs) - min(xs)) * 0.1 or 1
        y_margin = (max(ys) - min(ys)) * 0.2 or 1

        node_size = 150 if is_massive else 600
        label_font = 6 if is_massive else 10

        # ANIMATION SETTINGS
        FRAMES_PER_TURN = 15 # Generates 15 intermediate frames between Turn 1 and Turn 2
        total_frames = max_turn * FRAMES_PER_TURN + 1

        def get_drone_pos(d_id, T):
            """Linear Interpolation (Lerp) to find exact X,Y at fractional time T"""
            t1 = int(T)
            t2 = min(t1 + 1, max_turn)
            progress = T - t1

            loc1 = drone_timelines[d_id][t1]
            loc2 = drone_timelines[d_id][t2]

            x1, y1 = pos[loc1]
            x2, y2 = pos[loc2]

            # Calculate smooth intermediate position
            curr_x = x1 + (x2 - x1) * progress
            curr_y = y1 + (y2 - y1) * progress
            return round(curr_x, 3), round(curr_y, 3)

        def draw(frame_idx):
            ax.clear()
            ax.set_facecolor(BG)
            fig.patch.set_facecolor(BG)

            T = frame_idx / FRAMES_PER_TURN
            current_turn = int(T)

            # Draw Edges
            drawn_edges = set()
            for node, neighbors in self.graph.adj_list.items():
                for neighbor in neighbors:
                    edge = frozenset([node, neighbor])
                    if edge in drawn_edges: continue
                    drawn_edges.add(edge)
                    x1, y1 = pos[node]
                    x2, y2 = pos[neighbor]
                    ax.plot([x1, x2], [y1, y2], color=EDGE, linewidth=2, alpha=0.4, solid_capstyle="round", zorder=1)

            # Draw Empty Nodes (Just structure, no drone counts inside)
            for loc, (x, y) in pos.items():
                if "-" in loc: continue # Don't draw invisible midpoints
                zone_obj = self.graph.zones[loc]
                n_color = get_node_color(getattr(zone_obj, 'color', None))
                ax.scatter(x, y, s=node_size, color=n_color, edgecolors="#A5B4FC", linewidths=1.5, zorder=2)
                ax.text(x, y - (y_margin * 0.15), loc, color="#94A3B8", ha="center", va="top", fontsize=label_font, rotation=25 if is_massive else 0, zorder=3)

            # Calculate ALL Drone Positions and Group Them
            pos_groups = {}
            for d_id in drone_timelines.keys():
                curr_pos = get_drone_pos(d_id, T)
                if curr_pos not in pos_groups:
                    pos_groups[curr_pos] = []
                pos_groups[curr_pos].append(d_id)

            # Draw Drones & Tags
            for (x, y), drones in pos_groups.items():
                main_drone = drones[0]
                extra = len(drones) - 1

                # Format: [D-1] + 2
                tag = f"[D-{main_drone}]"
                if extra > 0:
                    tag += f" + {extra}"

                # Draw the actual drone as a bright cyan dot
                ax.scatter(x, y, s=node_size * 0.4, color=DRONE_COLOR, zorder=4)

                # Draw the label above the drone with a sleek dark background box
                ax.text(x, y + (y_margin * 0.08), tag, color=TEXT, ha="center", va="bottom",
                        fontsize=7 if is_massive else 10, fontweight="bold",
                        bbox=dict(facecolor='#0F172A', alpha=0.8, edgecolor=DRONE_COLOR, boxstyle='round,pad=0.3', linewidth=1),
                        zorder=5)

            ax.set_title(f"Simulation Turn {current_turn}", color=TEXT, fontsize=20, pad=20, fontweight="bold")
            ax.set_xlim(min(xs) - x_margin, max(xs) + x_margin)
            ax.set_ylim(min(ys) - y_margin, max(ys) + y_margin)
            if not is_massive: ax.set_aspect("equal")
            ax.axis("off")
            plt.tight_layout(pad=2)

        # Smooth animation settings (20 fps)
        writer = FFMpegWriter(
    fps=20,
    metadata={"artist": "Matplotlib"},
    bitrate=1800
)
        anim = FuncAnimation(fig, draw, frames=total_frames, interval=50)
        anim.save(
    filename,
    writer=writer,
    savefig_kwargs={"facecolor": BG}
)
        print(f"Visualization saved to {filename} successfully!")

    def update_reservations(self, rout):
        if rout:
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
        #self.visualize_tmp()
