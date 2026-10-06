import random

from .entities import Player, Ghost, GhostStates


class GameState:
    def place_pacgums(self, width: int, height: int, count: int,
                      excluded: set[tuple[int, int]]) -> set[tuple[int, int]]:
        rng = random.Random()

        all_cells = [(x, y) for x in range(width) for y in range(height)]
        available = [cell for cell in all_cells if cell not in excluded]

        count = min(count, len(available))
        return set(rng.sample(available, count))

    def check_collisions(self, player: Player, ghosts: list[Ghost], points_per_ghost: int) -> None:
        for ghost in ghosts:
            if (player.x, player.y) != (ghost.x, ghost.y):
                continue

            if ghost.state == GhostStates.SCARED:
                player.score += points_per_ghost
                ghost.state = GhostStates.EATEN
            elif ghost.state == GhostStates.CHASE:
                player.lives -= 1
                player.respawn()
