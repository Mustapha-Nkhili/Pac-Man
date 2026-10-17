import sys

from src.config_loader import load_config
from src.logic.game_state import GameState
from UI.Game import Game


def main():
    if len(sys.argv) != 2:
        print("Error: Invalid number of arguments.", file=sys.stderr)
        print(f"Usage: uv run {sys.argv[0]} config.json", file=sys.stderr)
        sys.exit(1)

    game_state = GameState()
    config = load_config(sys.argv[1])
    Game(game_state, config).run()


if __name__ == "__main__":
    main()
