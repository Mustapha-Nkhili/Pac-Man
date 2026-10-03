from collections import deque

from .maze import DOWN, LEFT, RIGHT, UP, can_move


class Entity:
    def __init__(self, x: int, y: int, direction: int, maze_grid: list[list[int]]) -> None:
        self.x = x
        self.y = y
        self.direction = direction
        self.maze_grid = maze_grid
        self.maze_height = len(maze_grid)
        self.maze_width = len(maze_grid[0])

    def move(self, direction: int) -> None:
        if can_move(self.maze_grid, self.y, self.x, direction):
            self.direction = direction
            if direction == UP:
                self.y -= 1
            elif direction == DOWN:
                self.y += 1
            elif direction == LEFT:
                self.x -= 1
            elif direction == RIGHT:
                self.x += 1


class Ghost(Entity):
    def __init__(self, x: int,
                 y: int,
                 direction: int,
                 state: str,
                 maze_grid: list[list[int]]) -> None:
        super().__init__(x, y, direction, maze_grid)
        self.state = state


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

