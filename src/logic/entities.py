from .maze import can_move, UP, DOWN, LEFT, RIGHT

class Entity:
    def  __init__(self, x: int, y: int, direction: int, maze_grid: list[list[int]]) -> None:
        self.x = x
        self.y = y
        self.direction = direction
        self.maze_grid = maze_grid

    def move(self, direction: int) -> None:
        if can_move(self.maze_grid, self.x, self.y, direction):
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
