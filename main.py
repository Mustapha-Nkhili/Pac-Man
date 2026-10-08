import sys

from src.config_loader import load_config
from UI.Game import Game


def main():
    Game(load_config(sys.argv[1])).run()


if __name__ == "__main__":
    main()