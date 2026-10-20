import random

from .entities import Player
from .ghost import Ghost, GhostStates

ALL_Walls = 15


class GameState:
    """
    Manages the generation, rules, and collision logic of the maze game.

    This class places items on the map, checks when objects touch,
    and updates game scores and lives.
    """

    def _get_corners(self, width: int, height: int) -> set[tuple[int, int]]:
        """Finds the coordinates of the four corners of the map.

        Args:
            width: The total number of columns in the grid.
            height: The total number of rows in the grid.

        Returns:
            A set of grid coordinates for the four corners.
        """
        return {
            (0, 0),
            (width - 1, 0),
            (0, height - 1),
            (width - 1, height - 1),
        }

    def place_pacgums(
        self,
        width: int,
        height: int,
        maze: list[list[int]],
        count: int,
        center_cell: tuple[int, int],
    ) -> set[tuple[int, int]]:
        """Puts normal pacgums on random empty spaces of the map.

        Pacgums will not appear on the corners or in the center.

        Args:
            width: The total columns of the map.
            height: The total rows of the map.
            maze: The grid showing where walls are.
            count: How many pacgums to create.

        Returns:
            A set of grid coordinates where pacgums are placed.
        """
        rng = random.Random()

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

    def place_super_pacgums(
        self, width: int, height: int
    ) -> set[tuple[int, int]]:
        """Puts large super pacgums on the corners of the map.

        Args:
            width: The total columns of the map.
            height: The total rows of the map.

        Returns:
            A set of grid coordinates for the four corners.
        """
        return self._get_corners(width, height)

    def check_collisions(
        self, player: Player, ghosts: list[Ghost], points_per_ghost: int
    ) -> None:
        """Checks if the player is touching any ghosts.

        If the ghost is scared, the player eats it and gets points.
        If the ghost is chasing, the player loses a life and respawns.

        Args:
            player: The player object.
            ghosts: A list of all ghosts in the game.
            points_per_ghost: Score given for eating a scared ghost.
        """
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
        self,
        player: Player,
        pacgums: set[tuple[int, int]],
        points_per_pacgum: int,
    ) -> None:
        """Checks if the player collects a normal pacgum.

        If touched, the pacgum is removed and the player gets points.

        Args:
            player: The player class.
            pacgums: A set of remaining pacgum positions.
            points_per_pacgum: Score given for collecting one pacgum.
        """
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
        """Checks if the player collects a super pacgum.

        If touched, the item is removed, the player gets points, and all
        living ghosts become scared for a short time.

        Args:
            player: The player object.
            super_pacgums: A set of remaining super pacgum positions.
            ghosts: A list of all ghosts in the game.
            now: The current game time value.
            points_per_super_pacgum: Score given for collecting the item.
        """
        if (player.x, player.y) in super_pacgums:
            super_pacgums.remove((player.x, player.y))
            player.score += points_per_super_pacgum
            for ghost in ghosts:
                if ghost.state == GhostStates.EATEN:
                    continue
                ghost.state = GhostStates.SCARED
                ghost.scared_until = now + ghost.scared_duration
