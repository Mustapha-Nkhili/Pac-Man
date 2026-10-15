from .maze import DOWN, LEFT, RIGHT, UP, can_move


class Entity:
    def __init__(
        self, x: int, y: int, direction: int, maze_grid: list[list[int]]
    ) -> None:
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


class Player(Entity):
    def __init__(
        self, x: int, y: int, lives: int, direction: int, maze_grid: list[list[int]]
    ) -> None:
        super().__init__(x, y, direction, maze_grid)
        self.score = 0
        self.lives = lives
        self.old_x = x
        self.old_y = y
        self.spawn_x = x
        self.spawn_y = y

    def respawn(self) -> None:
        self.x, self.y = self.spawn_x, self.spawn_y
        self.old_x, self.old_y = self.spawn_x, self.spawn_y
