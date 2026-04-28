from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


@dataclass
class Zone:
    name: str = None
    x: int = None
    y: int = None
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: int = 1
    color: Optional[str] = None

    is_start: bool = False
    is_end: bool = False


@dataclass
class Connection:
    zone1: str = None
    zone2: str = None
    max_link_capacity: int = 1


@dataclass
class Graph:
    nb_drones: int = 0
    start_hub: Optional[str] = None
    end_hub: Optional[str] = None

    # Stores all zones. Key: zone name, Value: Zone object
    zones: dict[str, Zone] = field(default_factory=dict)

    # Stores all connections.
    # Key: frozenset of the two zone names. Value: Connection object
    connections: dict[frozenset[str], Connection] = field(default_factory=dict)

    # Adjacency list for Dijkstra: quickly find neighbors of a zone
    # Key: zone name, Value: list of neighbor zone names
    adj_list: dict[str, list[str]] = field(default_factory=dict)

    def add_zone(self, zone: Zone) -> None:
        """Adds a zone and initializes its adjacency list."""
        self.zones[zone.name] = zone
        if zone.name not in self.adj_list:
            self.adj_list[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        """Adds a connection and updates the adjacency list."""
        edge_key = frozenset([conn.zone1, conn.zone2])

        # The PDF says: "The same connection must not appear more than once"
        if edge_key in self.connections:
            raise ValueError(
                f"Duplicate connection detected: {conn.zone1}-{conn.zone2}"
            )

        self.connections[edge_key] = conn

        # It's a bidirectional graph, so add neighbors to both sides
        self.adj_list[conn.zone1].append(conn.zone2)
        self.adj_list[conn.zone2].append(conn.zone1)
