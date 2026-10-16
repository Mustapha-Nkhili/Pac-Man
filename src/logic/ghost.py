from collections import deque
from enum import Enum, auto
import random

from .entities import Entity
from .maze import DOWN, LEFT, RIGHT, UP, can_move


class GhostStates(Enum):
    CHASE = auto()
    SCARED = auto()
    EATEN = auto()

class GhostCorners(Enum):
    TOPLEFT = auto()
    TOPRIGHT = auto()
    BOTTOMLEFT = auto()
    BOTTOMRIGHT = auto()


OPPOSITE = {UP: DOWN, RIGHT: LEFT, DOWN: UP, LEFT: RIGHT}
SHY_DISTANCE = 8


class Ghost(Entity):
    def __init__(self, direction: int,
                 maze_grid: list[list[int]],
                 corner: GhostCorners) -> None:
        self.maze_height = len(maze_grid)
        self.maze_width = len(maze_grid[0])
        self.corner = corner
        x, y = self._get_corner()
        super().__init__(x, y, direction, maze_grid)
        self.state = GhostStates.CHASE
        self.scared_until = 0
        self.scared_duration = 7000
        self.recent_cells = deque(maxlen=6)
        self._is_retreating = False


    def move(self, direction: int) -> None:
        previous = (self.x, self.y)
        super().move(direction)
        if previous != (self.x, self.y):
            self.recent_cells.append((self.x, self.y))

    def _get_corner(self) -> tuple[int, int]:
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

    def _get_unvisited_neighbors(self, x: int, y: int, came_from: dict[tuple, tuple]) -> list[tuple[int, int, int]]:
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
        queue: deque[tuple[int, int]] = deque([(self.x, self.y)])
        came_from = {}
        came_from[(self.x, self.y)] = None

        while queue:
            x, y = queue.popleft()
 
            if (x, y) == (player_x, player_y):
                current = (player_x, player_y)
                direction = None

                while came_from[current] is not None:
                    prev_cell, prev_direction = came_from[current]
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

    def _get_neighbors(self) -> list[tuple[int, int, int]]:
        x = self.x
        y = self.y
        neighbors = []
        directions = [
            (x, y - 1, UP),
            (x + 1, y, RIGHT),
            (x, y + 1, DOWN),
            (x - 1, y, LEFT)
        ]

        for nx, ny, direction in directions:
            if 0 <= nx < self.maze_width and 0 <= ny < self.maze_height:
                if can_move(self.maze_grid, y, x, direction):
                    neighbors.append((nx, ny, direction))

        return neighbors


    def _escape_player_direction(self, player_x, player_y) -> int | None:
        neighbors = self._get_neighbors()
        if not neighbors:
            return None

        reverse = OPPOSITE.get(self.direction)
        forward_neighbors = [n for n in neighbors if n[2] != reverse]

        choices = forward_neighbors if forward_neighbors else neighbors
        no_recent_neighbors = [n for n in choices if (n[0], n[1]) not in self.recent_cells]

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
        neighbors = self._get_neighbors()

        if not neighbors:
            return None

        forward = [n for n in neighbors if n[2] != OPPOSITE.get(self.direction)]
        return random.choice(forward or neighbors)[2]


    def _get_shy_direction(self, player_x: int, player_y: int) -> int | None:
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

        if self.state == GhostStates.EATEN and (self.x, self.y) == self._get_corner():
            self.state = GhostStates.CHASE
