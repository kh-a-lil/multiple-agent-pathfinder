import sys
from sys import exit


def main():
    if len(sys.argv) != 2:
        print("usage: uv python3 -m src <input map>")
        exit(0)

    print("Hello from fly-in!")


if __name__ == "__main__":
    main()
