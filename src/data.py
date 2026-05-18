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
    def __lt__(self, other):
        if self.zone_type == ZoneType.PRIORITY:
            return False
        return True
    name: str = ""
    x: int = 0
    y: int = 0
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: int | float = 1
    color: Optional[str] = None

    is_start: bool = False
    is_end: bool = False


@dataclass
class Connection:
    zone1: str = ""
    zone2: str = ""
    max_link_capacity: int = 1


@dataclass
class Graph:
    nb_drones: int = 0
    start_hub: str = ""
    end_hub: str = ""

    zones: dict[str, Zone] = field(default_factory=dict)

    connections: dict[frozenset[str], Connection] = field(default_factory=dict)

    adj_list: dict[str, list[str]] = field(default_factory=dict)

    def add_zone(self, zone: Zone) -> None:
        """Adds a zone and initializes its adjacency list."""
        self.zones[zone.name] = zone
        if zone.name not in self.adj_list:
            self.adj_list[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        """Adds a connection and updates the adjacency list."""
        edge_key = frozenset([conn.zone1, conn.zone2])

        if edge_key in self.connections:
            raise ValueError(
                f"Duplicate connection detected: {conn.zone1}-{conn.zone2}"
            )

        self.connections[edge_key] = conn

        self.adj_list[conn.zone1].append(conn.zone2)
        self.adj_list[conn.zone2].append(conn.zone1)
