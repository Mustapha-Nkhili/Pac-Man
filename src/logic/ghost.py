from collections import deque
from enum import Enum, auto
import random

from .entities import Entity
from .maze import DOWN, LEFT, RIGHT, UP, can_move


class GhostStates(Enum):
    """Holds the different states a ghost can be in."""

    CHASE = auto()
    SCARED = auto()
    EATEN = auto()


class GhostCorners(Enum):
    """Holds the four corner targets of the maze map."""

    TOPLEFT = auto()
    TOPRIGHT = auto()
    BOTTOMLEFT = auto()
    BOTTOMRIGHT = auto()


OPPOSITE = {UP: DOWN, RIGHT: LEFT, DOWN: UP, LEFT: RIGHT}
SHY_DISTANCE = 8


class Ghost(Entity):
    """Represents a ghost enemy that moves through the maze grid.

    A ghost can chase the player, run away from the player, or respawn
    to its corner when eaten.

    Attributes:
        maze_height: The number of rows in the maze grid.
        maze_width: The number of columns in the maze grid.
        corner: The home corner assigned to this specific ghost.
        state: The current behavior mode of the ghost.
        scared_until: The game time when the ghost stops being scared.
        scared_duration: How long a ghost stays scared in milliseconds.
        recent_cells: A history tracking the last 6 steps taken.
    """

    def __init__(
        self, direction: int, maze_grid: list[list[int]], corner: GhostCorners
    ) -> None:
        """Initializes a Ghost object"""
        self.maze_height = len(maze_grid)
        self.maze_width = len(maze_grid[0])
        self.corner = corner
        x, y = self._get_corner()
        super().__init__(x, y, direction, maze_grid)
        self.state = GhostStates.CHASE
        self.scared_until = 0
        self.scared_duration = 7000
        self.recent_cells: deque[tuple[int, int]] = deque(maxlen=6)
        self._is_retreating = False

    def move(self, direction: int) -> None:
        """Moves the ghost and saves its position to the recent steps list.

        Args:
            direction: The integer code for the direction to move.
        """
        previous = (self.x, self.y)
        super().move(direction)
        if previous != (self.x, self.y):
            self.recent_cells.append((self.x, self.y))

    def _get_corner(self) -> tuple[int, int]:
        """Finds the (x, y) coordinates of the ghost's home corner.

        Returns:
            A tuple containing the horizontal and vertical coordinates.
        """
        corner = self.corner

        if corner == GhostCorners.TOPLEFT:
            return (0, 0)
        elif corner == GhostCorners.TOPRIGHT:
            return (self.maze_width - 1, 0)
        elif corner == GhostCorners.BOTTOMLEFT:
            return (0, self.maze_height - 1)
        elif corner == GhostCorners.BOTTOMRIGHT:
            return (self.maze_width - 1, self.maze_height - 1)
        else:
            return (0, 0)

    def _get_unvisited_neighbors(
        self,
        x: int,
        y: int,
        came_from: dict[tuple[int, int], tuple[tuple[int, int], int] | None],
    ) -> list[tuple[int, int, int]]:
        """Finds neighbor cells that have not been checked by the pathfinder.

        Args:
            x: The horizontal grid position to check from.
            y: The vertical grid position to check from.
            came_from: A dictionary tracking the history of checked cells.

        Returns:
            A list of tuples, each containing (next_x, next_y, direction).
        """
        neighbors = []

        if y - 1 >= 0 and (x, y - 1) not in came_from:
            neighbors.append((x, y - 1, UP))
        if x + 1 < self.maze_width and (x + 1, y) not in came_from:
            neighbors.append((x + 1, y, RIGHT))
        if y + 1 < self.maze_height and (x, y + 1) not in came_from:
            neighbors.append((x, y + 1, DOWN))
        if x - 1 >= 0 and (x - 1, y) not in came_from:
            neighbors.append((x - 1, y, LEFT))

        return neighbors

    def _find_shortest_path(self, player_x: int, player_y: int) -> int | None:
        """Finds the fastest direction to reach a target position.

        Args:
            player_x: The target horizontal position.
            player_y: The target vertical position.

        Returns:
            The direction code for the first step, or None if no path exists.
        """
        queue: deque[tuple[int, int]] = deque([(self.x, self.y)])
        came_from: dict[
            tuple[int, int], tuple[tuple[int, int], int] | None
        ] = {}
        came_from[(self.x, self.y)] = None

        while queue:
            x, y = queue.popleft()

            if (x, y) == (player_x, player_y):
                current = (player_x, player_y)
                direction = None

                while came_from[current] is not None:
                    entry = came_from[current]
                    if entry is not None:
                        prev_cell, prev_direction = entry
                        if prev_cell == (self.x, self.y):
                            direction = prev_direction
                        current = prev_cell

                return direction

            neighbors = self._get_unvisited_neighbors(x, y, came_from)
            for neighbor in neighbors:
                next_x, next_y, direction = neighbor

                if can_move(self.maze_grid, y, x, direction):
                    came_from[(next_x, next_y)] = ((x, y), direction)
                    queue.append((next_x, next_y))

        return None

    def _get_neighbors(self) -> list[tuple[int, int, int]]:
        """Finds all open paths directly next to the ghost's current position.

        Returns:
            A list of tuples, each containing (next_x, next_y, direction).
        """
        x = self.x
        y = self.y
        neighbors = []
        directions = [
            (x, y - 1, UP),
            (x + 1, y, RIGHT),
            (x, y + 1, DOWN),
            (x - 1, y, LEFT),
        ]

        for nx, ny, direction in directions:
            if 0 <= nx < self.maze_width and 0 <= ny < self.maze_height:
                if can_move(self.maze_grid, y, x, direction):
                    neighbors.append((nx, ny, direction))

        return neighbors

    def _escape_player_direction(
        self, player_x: int, player_y: int
    ) -> int | None:
        """Chooses a direction that moves the ghost furthest from the player.

        Args:
            player_x: The player's horizontal position.
            player_y: The player's vertical position.

        Returns:
            The safest escape direction code, or None if trapped.
        """
        neighbors = self._get_neighbors()
        if not neighbors:
            return None

        reverse = OPPOSITE.get(self.direction)
        forward_neighbors = [n for n in neighbors if n[2] != reverse]

        choices = forward_neighbors if forward_neighbors else neighbors
        no_recent_neighbors = [
            n for n in choices if (n[0], n[1]) not in self.recent_cells
        ]

        neighbors = no_recent_neighbors if no_recent_neighbors else choices

        best_direction = None
        best_distance = -1
        for nx, ny, direction in neighbors:
            distance = abs(nx - player_x) + abs(ny - player_y)
            if distance > best_distance:
                best_distance = distance
                best_direction = direction

        return best_direction

    def _get_random_direction(self) -> int | None:
        """Chooses a random valid direction, avoiding turning straight back.

        Returns:
            A random direction code, or None if there are no open paths.
        """
        neighbors = self._get_neighbors()

        if not neighbors:
            return None

        forward = [
            n for n in neighbors if n[2] != OPPOSITE.get(self.direction)
        ]
        return random.choice(forward or neighbors)[2]

    def _get_shy_direction(self, player_x: int, player_y: int) -> int | None:
        """Chases the player, but runs back home if the player gets too close.

        Args:
            player_x: The player's horizontal position.
            player_y: The player's vertical position.

        Returns:
            The chosen direction code, or None if blocked.
        """
        distance = abs(self.x - player_x) + abs(self.y - player_y)

        if self._is_retreating:
            if distance > (SHY_DISTANCE + 2):
                self._is_retreating = False
        else:
            if distance <= SHY_DISTANCE:
                self._is_retreating = True

        if not self._is_retreating:
            return self._find_shortest_path(player_x, player_y)

        corner_x, corner_y = self._get_corner()
        from_corner = abs(self.x - corner_x) + abs(self.y - corner_y)
        if from_corner <= 4:
            return self._get_random_direction()

        return self._find_shortest_path(corner_x, corner_y)

    def take_turn(self, player_x: int, player_y: int) -> None:
        """Decides the ghost's next movement choice based on
            its type and state.

        Args:
            player_x: The current horizontal position of the player target.
            player_y: The current vertical position of the player target.
        """
        if self.state == GhostStates.CHASE:
            if self.corner == GhostCorners.TOPLEFT:
                direction = self._find_shortest_path(player_x, player_y)

            elif self.corner == GhostCorners.TOPRIGHT:
                direction = self._get_random_direction()

            elif self.corner == GhostCorners.BOTTOMRIGHT:
                direction = self._get_random_direction()

            elif self.corner == GhostCorners.BOTTOMLEFT:
                direction = self._get_shy_direction(player_x, player_y)

        elif self.state == GhostStates.SCARED:
            direction = self._escape_player_direction(player_x, player_y)
        elif self.state == GhostStates.EATEN:
            x, y = self._get_corner()
            direction = self._find_shortest_path(x, y)
        else:
            direction = None
        if direction is not None:
            self.move(direction)

        if (
            self.state == GhostStates.EATEN
            and (self.x, self.y) == self._get_corner()
        ):
            self.state = GhostStates.CHASE
