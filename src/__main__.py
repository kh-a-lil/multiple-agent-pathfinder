import sys
from sys import exit, stderr
from src.parsing import parse_class


def main():
    if len(sys.argv) != 2:
        print("usage: uv python3 -m src <input map>")
        exit(0)
    try:
        with open(sys.argv[1], "r") as f:
            parser: parse_class = parse_class(f)
    except Exception as e:
        print(f"fly-in: an error reading input map: {e}", file=stderr)
        exit(1)
    for s in parser.map.zones.values():
        print(s.name)

    # with open(sys.argv[1], "r") as f:
    #         parser: parse_class = parse_class(f)

if __name__ == "__main__":
    main()
