import sys

from src.config_loader import ConfigLoader, ConfigError
from src.logic.maze import MazeLoader
from src.logic.game_state import GameState
from src.UI.Game import Game


def main() -> None:
    """Reads the configuration file and starts the game."""
    try:
        if len(sys.argv) != 2:
            print("Error: Invalid number of arguments.", file=sys.stderr)
            print(f"Usage: uv run {sys.argv[0]} config.json", file=sys.stderr)
            sys.exit(1)

        maze = MazeLoader()
        game_state = GameState()
        config = ConfigLoader().load_config(sys.argv[1])
        Game(game_state, config, maze).run()

    except (ConfigError, RuntimeError) as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Error: Keyboard interrupt detected")
        sys.exit(1)


if __name__ == "__main__":
    main()
