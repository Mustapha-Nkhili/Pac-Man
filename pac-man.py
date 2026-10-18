import sys

from src.config_loader import ConfigLoader, ConfigError
from src.logic.game_state import GameState
from UI.Game import Game


def main():
    try:
        if len(sys.argv) != 2:
            print("Error: Invalid number of arguments.", file=sys.stderr)
            print(f"Usage: uv run {sys.argv[0]} config.json", file=sys.stderr)
            sys.exit(1)

        game_state = GameState()
        config = ConfigLoader().load_config(sys.argv[1])
        Game(game_state, config).run()

    except ConfigError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
