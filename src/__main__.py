import sys
from sys import exit, stderr
from src.parsing import ParseClass
from src.space_time_pathfinder import PathFinder


def main() -> None:
    """Run the fly-in simulation from a map configuration file.

    The function parses the input map, computes drone routes, and
    prints the movements for each simulation turn.

    Raises:
        SystemExit: If the input arguments are invalid or the map
            cannot be parsed.
    """
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
    output: list = []
    i = 1
    done: bool = False
    while not done:
        done = True
        turn = []
        for index, rout in solver.routs.items():
            p_name: str = solver.graph.start_hub
            for name, t in rout:
                if t == i:
                    done = False
                    if name != p_name:
                        p_name = name
                        turn.append(f"D{index}-{name}")
        i += 1
        if done:
            break
        output.append(" ".join(turn))
    for i in output:
        print(i)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"fly-in: an error happend: {e}", file=stderr)
        exit(1)
