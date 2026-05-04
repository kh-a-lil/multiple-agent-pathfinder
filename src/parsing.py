from src.data import Graph, Zone, Connection, ZoneType


class ParseClass:
    def __init__(self, input):
        self.map: Graph = Graph()
        got_nb_d: bool = False
        got_s_h: bool = False
        got_e_h: bool = False

        for i, line in enumerate(input, 1):
            line: str = line.split("#", 1)[0].strip()
            if not line:
                continue

            if line.startswith("nb_drones"):
                if got_nb_d:
                    raise ValueError(f"multiple definitions of nb_drones at line {i}")
                self.map.nb_drones = int(line.split(":", 1)[1].strip())
                got_nb_d = True

            elif line.startswith("start_hub") or line.startswith("end_hub"):
                if line.startswith("start_hub") and got_s_h:
                    raise ValueError(f"multiple definitions of start_hub at line {i}")

                if line.startswith("end_hub") and got_e_h:
                    raise ValueError(f"multiple definitions of end_hub at line {i}")

                name = line.split(":", 1)[0].strip()
                line = line.split(":", 1)[1].strip()
                new_zone: Zone = Zone()
                lines = line.split(maxsplit=3)
                new_zone.name = lines[0]
                new_zone.x = int(lines[1])
                new_zone.y = int(lines[2])
                if "[" in line and "[" in lines[3] and "]" in lines[3]:
                    s_attrs: str = lines[3].replace("[", "").replace("]", "")
                    attrs: list = s_attrs.split()
                    for attr in attrs:
                        if attr.startswith("color"):
                            new_zone.color = attr.split("=", 1)[1]
                        if attr.startswith("max_drones"):
                            new_zone.max_drones = int(attr.split("=", 1)[1])
                            if new_zone.max_drones < self.map.nb_drones:
                                new_zone.max_drones = self.map.nb_drones
                        if attr.startswith("zone"):
                            zone_attr = attr.split("=", 1)[1]
                            if zone_attr == "normal":
                                new_zone.zone_type = ZoneType.NORMAL
                            elif zone_attr == "blocked":
                                new_zone.zone_type = ZoneType.BLOCKED
                                raise ValueError("start/end hub can't be blocked")
                            elif zone_attr == "restricted":
                                new_zone.zone_type = ZoneType.RESTRICTED
                                raise ValueError("start/end hub can't be restricted")
                            elif zone_attr == "priority":
                                new_zone.zone_type = ZoneType.PRIORITY
                            else:
                                raise ValueError(f"unkowen zone type at line {i}")

                if name.startswith("end_hub"):
                    new_zone.is_end = True
                    got_e_h = True
                    self.map.end_hub = new_zone.name

                if name.startswith("start_hub"):
                    new_zone.is_start = True
                    got_s_h = True
                    self.map.start_hub = new_zone.name

                self.map.add_zone(new_zone)

            elif line.startswith("hub"):
                name = line.split(":", 1)[0].strip()
                line = line.split(":", 1)[1].strip()
                new_zone: Zone = Zone()
                lines = line.split(maxsplit=3)
                new_zone.name = lines[0]
                new_zone.x = int(lines[1])
                new_zone.y = int(lines[2])
                if len(lines) > 3 and "[" in lines[3] and "]" in lines[3]:
                    s_attrs: str = lines[3].replace("[", "").replace("]", "")
                    attrs = s_attrs.split()
                    for attr in attrs:
                        if attr.startswith("color"):
                            new_zone.color = attr.split("=", 1)[1]
                        if attr.startswith("max_drones"):
                            new_zone.max_drones = int(attr.split("=", 1)[1])
                        if attr.startswith("zone"):
                            zone_attr = attr.split("=", 1)[1]
                            if zone_attr == "normal":
                                new_zone.zone_type = ZoneType.NORMAL
                            elif zone_attr == "blocked":
                                new_zone.zone_type = ZoneType.BLOCKED
                            elif zone_attr == "restricted":
                                new_zone.zone_type = ZoneType.RESTRICTED
                            elif zone_attr == "priority":
                                new_zone.zone_type = ZoneType.PRIORITY
                            else:
                                raise ValueError(f"unkowen zone type at line {i}")
                self.map.add_zone(new_zone)

            elif line.startswith("connection"):
                name = line.split(":", 1)[0].strip()
                line = line.split(":", 1)[1].strip()
                new_con: Connection = Connection()
                links = line.split(maxsplit=1)[0]
                if sum([1 for c in links if c == "-"]) != 1:
                    raise ValueError(f"wrong syntax at line {i}")
                new_con.zone1 = links.split("-", 1)[0].strip()
                new_con.zone2 = links.split("-", 1)[1].strip()
                if "[" in line:
                    if "]" not in line:
                        raise ValueError(f"wrong syntax at line {i}")
                    # c_a = connection attribute
                    c_a = line.split("[", 1)[1].replace("]", "").split("=")[1]
                    c_a = c_a.strip()
                    c_n = line.split("[", 1)[1].replace("]", "").split("=")[0]
                    c_n = c_n.strip()
                    if c_n == "max_link_capacity":
                        new_con.max_link_capacity = int(c_a)
                    else:
                        raise ValueError("unkowen connection attribute")
                try:
                    self.map.add_connection(new_con)
                except KeyError:
                    raise ValueError("a connection connecting none existant zone")

            else:
                raise ValueError(f"unkowen argument at line {i}")
