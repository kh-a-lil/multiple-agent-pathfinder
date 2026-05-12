import sys
from sys import exit, stderr
from src.parsing import ParseClass
from src.space_time_pathfinder import PathFinder
from pathlib import Path


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
    output: list = []
    i = 0
    done: bool = False
    while not done:
        done = True
        turn = []
        for index, rout in solver.routs.items():
            for name, t in rout:
                if t == i:
                    done = False
                    turn.append(f"{index}-{name}")
        #print(turn)
        i += 1
        output.append(" ".join(turn))
        if done:
            break
    #for i in output:
    #    print(i)
    #print(solver.routs)



    #path: Path = Path(args.output)
    #path.parent.mkdir(parents=True, exist_ok=True)
    #try:
    #    with path.open("w") as f:

    #except Exception as e:
    #    print(f"CMM: error writing output file: {e}", file=stderr)

    #for key, val in solver.routs.items():
    #    print(key, ": \n", val, "\n\n\n")

    # with open(sys.argv[1], "r") as f:
    #     parser: ParseClass = ParseClass(f)


    #for s in parser.map.zones.values():
    #    print(s.name)
    #    print("\n\n\n")

if __name__ == "__main__":
    main()
