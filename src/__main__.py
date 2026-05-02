import sys
from sys import exit, stderr
from src.parsing import ParseClass
from src.space_time_pathfinder import PathFinder


def main():
    if len(sys.argv) != 2:
        print('usage: uv python3 -m src <input map>\nor\
              \nmake run MAP="<input map>"')
        exit(0)
    try:
        with open(sys.argv[1], "r") as f:
            parser: ParseClass = ParseClass(f)
    except Exception as e:
        print(f"fly-in: an error reading input map: {e}", file=stderr)
        exit(1)

    solver = PathFinder(parser.map)
    solver.djikstra()

    # with open(sys.argv[1], "r") as f:
    #     parser: ParseClass = ParseClass(f)

    # for s in parser.map.connections.values():
    #     print(s.zone1)
    #     print(s.zone2)
    #     print(s.max_link_capacity, "\n\n\n")


if __name__ == "__main__":
    main()
