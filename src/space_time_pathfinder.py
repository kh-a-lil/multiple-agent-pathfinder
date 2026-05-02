from src.data import *
import heapq


class PathFinder:
    def __init__(self, map: Graph):
        self.graph: Graph = map
        self.node_reservations: dict[tuple[str, int], int] = {}
        self.edge_reservations: dict[tuple[frozenset[str], int], int] = {}

    def djikstra(self):
        queue: list[(int,Zone)] = []
        visited: list[Zone, int] = []
        heapq.heappush(queue, (0,self.graph.zones[self.graph.start_hub], None))

        while queue:
            curr_turn , curr_zone, came_from = heapq.heappop(queue)
            if curr_zone == self.graph.zones[self.graph.end_hub]:
                return queue
            if (curr_zone, curr_turn) in visited:
                continue
            visited.append((curr_zone, curr_turn))

            next_turn = curr_turn + 1
            if self.node_reservations[(curr_zone, next_turn)] < curr_zone.max_drones:
                if (curr_zone, next_turn) in visited:
                    continue
                heapq.heappush(queue, (next_turn, curr_zone))
            for neighbor in self.graph.adj_list[curr_zone.name]:
                if neighbor.zone_type == ZoneType.NORMAL or neighbor.zone_type == ZoneType.PRIORITY:
                    if (neighbor, next_turn) in visited:
                        continue
                    if self.node_reservations[(neighbor, next_turn)] < neighbor.max_drones:
                        if self.edge_reservations[((curr_zone, neighbor), curr_turn)] < 
                        heapq.heappush(queue, (next_turn, neighbor))
                if neighbor.zone_type == ZoneType.RESTRICTED:
                    pass




    def update_reservations(self):
        pass

    def looper(self):
        self.routs = []
        for _ in range(1, self.graph.nb_drones + 1):
            rout = self.djikstra()
            self.routs.append(rout)
            self.update_reservations(rout)


# Initialize an empty Priority Queue.
# Push the Start node: (Turn 0, "Start_Zone")

# WHILE the Queue is not empty:
#    Pop the item with the lowest Turn number: (Current_Turn, Current_Node)

#    IF Current_Node is the "End_Zone":
#        WE FOUND THE BEST PATH!
#        Save this path, update the Timetable, and move to the next drone!

#    IF (Current_Node, Current_Turn) is in Visited:
#        Skip it. (We already found a faster way here)
#    Mark (Current_Node, Current_Turn) as Visited.

#    # --- ACTION 1: WAIT ---
#    Next_Turn = Current_Turn + 1
#    Check Timetable: Is 'Current_Node' completely full at 'Next_Turn'?
#    If NO:
#        Push (Next_Turn, Current_Node) to Queue

#    # --- ACTION 2: MOVE ---
#    FOR EACH Neighbor of Current_Node:

#        IF Neighbor is "normal" zone:
#            Next_Turn = Current_Turn + 1
#            Check Timetable: Is Neighbor full at Next_Turn?
#            Check Timetable: Is the Edge connecting them full at Current_Turn?
#            If NO to both:
#                Push (Next_Turn, Neighbor) to Queue

#        IF Neighbor is "restricted" zone (Costs 2 turns):
#            Next_Turn = Current_Turn + 2
#            Check Timetable: Is Neighbor full at Next_Turn?
#            Check Timetable: Is the Edge full at Current_Turn AND Current_Turn + 1?
#            If NO to all:
#                Push (Next_Turn, Neighbor) to Queue
