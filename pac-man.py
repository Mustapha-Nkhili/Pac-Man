import sys

from src.config_loader import load_config
from src.logic.maze import load_maze

def main():
    if len(sys.argv) != 2:
        print("Error: Invalid number of arguments.", file=sys.stderr)
        print(f"Usage: python {sys.argv[0]} config.json", file=sys.stderr)
        sys.exit(1)

    config = load_config(sys.argv[1])
    maze = load_maze(config["level"][0]["width"],
                     config["level"][0]["height"],
                     config["seed"])
    print(maze)


if __name__ == "__main__":
    main()
