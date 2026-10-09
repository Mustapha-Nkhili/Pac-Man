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
    excluded = {(0, 0), (maze["width"] - 1, 0),
                (0, maze["height"] - 1),
                (maze["width"] - 1, maze["height"] - 1)}
    pacgums = game_state.place_pacgums(maze["width"], 
                                       maze["height"],
                                       config["pacgum"],
                                       excluded)
    print(pacgums)

    Game(game_state, config).run()


if __name__ == "__main__":
    main()