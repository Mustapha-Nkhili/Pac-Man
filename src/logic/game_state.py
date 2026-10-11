import random

from .entities import Player, Ghost, GhostStates


class GameState:
    def _get_corners(self, width: int, height: int) -> set[tuple[int, int]]:
        return {(0, 0), (width - 1, 0),
                (0, height - 1),
                (width - 1, height - 1)}


    def place_pacgums(self, width: int, height: int, maze: list[list[int]], count: int) -> set[tuple[int, int]]:
        rng = random.Random()

        center_cell = (width // 2, height // 2)
        excluded = self._get_corners(width, height) | {center_cell}
        cells_without_42 = [(x, y) for x in range(width) for y in range(height) if maze[y][x] < 15]
        available = [cell for cell in cells_without_42 if cell not in excluded]

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


    def check_pacgums_collisions(self,
                                 player: Player,
                                 pacgums: set[tuple[int, int]],
                                 points_per_pacgum: int):
        if (player.x, player.y) in pacgums:
            pacgums.remove((player.x, player.y))
            player.score += points_per_pacgum
