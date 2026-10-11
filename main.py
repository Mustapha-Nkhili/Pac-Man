import sys

from src.config_loader import load_config
from src.logic.game_state import GameState
from src.logic.maze import load_maze
from UI.Game import Game


def main():
    game_state = GameState()
    config = load_config(sys.argv[1])
    maze = load_maze(config["level"][1]["width"], config["level"][1]["height"],
                         config["seed"])
    Game(game_state, config).run()


if __name__ == "__main__":
    main()
