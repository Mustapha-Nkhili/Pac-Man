import random

from .entities import Player, Ghost, GhostStates, GhostCorners

ALL_Walls = 15


class GameState:
    def _get_corners(self, width: int, height: int) -> set[tuple[int, int]]:
        return {(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)}

    def place_pacgums(
        self, width: int, height: int, maze: list[list[int]], count: int
    ) -> set[tuple[int, int]]:
        rng = random.Random()

        center_cell = (width // 2, height // 2)
        excluded = self._get_corners(width, height) | {center_cell}
        cells_without_42 = [
            (x, y)
            for x in range(width)
            for y in range(height)
            if maze[y][x] < ALL_Walls
        ]
        available = [cell for cell in cells_without_42 if cell not in excluded]

        count = min(count, len(available))
        return set(rng.sample(available, count))

    def place_super_pacgums(self, width: int, height: int) -> set[tuple[int, int]]:
        return self._get_corners(width, height)

    def check_collisions(
        self, player: Player, ghosts: list[Ghost], points_per_ghost: int
    ) -> None:
        for ghost in ghosts:
            if (player.x, player.y) != (ghost.x, ghost.y):
                continue

            if ghost.state == GhostStates.SCARED:
                player.score += points_per_ghost
                ghost.state = GhostStates.EATEN
            elif ghost.state == GhostStates.CHASE:
                player.lives -= 1
                player.respawn()

    def check_pacgums_collisions(
        self, player: Player, pacgums: set[tuple[int, int]], points_per_pacgum: int
    ):
        if (player.x, player.y) in pacgums:
            pacgums.remove((player.x, player.y))
            player.score += points_per_pacgum

    def check_superpacgums_collisions(
        self,
        player: Player,
        super_pacgums: set[tuple[int, int]],
        ghosts: list[Ghost],
        now: int,
        points_per_super_pacgum: int,
    ) -> None:
        if (player.x, player.y) in super_pacgums:
            super_pacgums.remove((player.x, player.y))
            player.score += points_per_super_pacgum
            for ghost in ghosts:
                if ghost.state == GhostStates.EATEN:
                    continue
                ghost.state = GhostStates.SCARED
                ghost.scared_until = now + ghost.scared_duration
