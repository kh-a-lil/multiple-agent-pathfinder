from src.data import Graph, Zone, Connection, ZoneType


class parse_class:
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
                self.map.start_hub = lines[0]
                new_zone.x = int(lines[1])
                new_zone.y = int(lines[2])
                if "[" in line and "[" in lines[3] and "]" in lines[3]:
                    attrs: list = lines[3].replace("[", "").replace("]", "").split()
                    for attr in attrs:
                        if attr.startswith("color"):
                            new_zone.color = attr.split("=", 1)[1]
                        if attr.startswith("max_drones"):
                            new_zone.max_drones = int(attr.split("=", 1)[1])
                            if new_zone.max_drones < self.map.nb_drones:
                                raise ValueError("start/end hub max drones < nb_drones")
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

                elif name.startswith("start_hub"):
                    new_zone.is_start = True
                    got_s_h = True
                    self.map.start_hub = new_zone.name

                self.map.add_zone(new_zone)

                # if name.startswith("end_hub"):
                #     print(new_zone.is_end)
                #     print(new_zone.name)
                #     print(new_zone.x)
                #     print(new_zone.y)
                #     print(new_zone.color)
                #     print(new_zone.max_drones)
                #     print(new_zone.zone_type)
                #     print(self.map.end_hub)

            elif line.startswith("hub"):
                name = line.split(":", 1)[0].strip()
                line = line.split(":", 1)[1].strip()
                new_zone: Zone = Zone()
                lines = line.split(maxsplit=3)
                new_zone.name = lines[0]
                self.map.start_hub = lines[0]
                new_zone.x = int(lines[1])
                new_zone.y = int(lines[2])
                if "[" in line and "[" in lines[3] and "]" in lines[3]:
                    attrs: list = lines[3].replace("[", "").replace("]", "").split()
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
                pass

            else:
                raise ValueError(f"unkowen argument at line {i}")
