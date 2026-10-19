import sys

from src.config_loader import ConfigLoader, ConfigError
from src.logic.game_state import GameState
from UI.Game import Game


def main():
    """Reads the configuration file and starts the game."""
    try:
        if len(sys.argv) != 2:
            print("Error: Invalid number of arguments.", file=sys.stderr)
            print(f"Usage: uv run {sys.argv[0]} config.json", file=sys.stderr)
            sys.exit(1)

<<<<<<< HEAD
    game_state = GameState()
    config = load_config(sys.argv[1])
    maze = load_maze(
        config["level"][1]["width"], config["level"][1]["height"], config["seed"]
    )
    Game(game_state, config).run()
=======
        game_state = GameState()
        config = ConfigLoader().load_config(sys.argv[1])
        Game(game_state, config).run()

    except ConfigError as e:
        print(e)
        sys.exit(1)
>>>>>>> origin/main


if __name__ == "__main__":
    main()
