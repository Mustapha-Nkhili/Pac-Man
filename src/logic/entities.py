from .maze import DOWN, LEFT, RIGHT, UP, MazeLoader


class Entity:
    """Represents a basic unit moving within a maze grid.

    Attributes:
          x: The current horizontal grid coordinate.
          y: The current vertical grid coordinate.
          direction: The current heading integer representing UP, DOWN, LEFT,
              or RIGHT.
          maze_grid: A 2D array representation of the structural maze layout.
          maze_height: Total row count extracted from the maze grid.
          maze_width: Total column count extracted from the first row of the
              maze grid.
    """

    def __init__(
        self,
        x: int,
        y: int,
        direction: int,
        maze: MazeLoader,
        maze_grid: list[list[int]],
    ) -> None:
        """
        Initializes an Entity with spatial coordinates
        and structural constraints.
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.maze = maze
        self.maze_grid = maze_grid
        self.maze_height = len(maze_grid)
        self.maze_width = len(maze_grid[0])

    def move(self, direction: int) -> None:
        """Updates the entity's position if the chosen direction is unblocked.

        Args:
            direction: The desired integer heading to attempt navigating
                towards.
        """
        if self.maze.can_move(self.maze_grid, self.y, self.x, direction):
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
    """Represents the user-controlled entity in the maze.

    Attributes:
        score: Cumulative points acquired by the player.
        lives: Remaining attempt count before a game over condition triggers.
        old_x: The previous horizontal coordinate occupied by the player.
        old_y: The previous vertical coordinate occupied by the player.
        spawn_x: The initial baseline horizontal coordinate used for resets.
        spawn_y: The initial baseline vertical coordinate used for resets.
    """

    def __init__(
        self,
        x: int,
        y: int,
        lives: int,
        direction: int,
        maze: MazeLoader,
        maze_grid: list[list[int]],
    ) -> None:
        """Initializes a Player instance with game state parameters."""
        super().__init__(x, y, direction, maze, maze_grid)
        self.score = 0
        self.lives = lives
        self.old_x = x
        self.old_y = y
        self.spawn_x = x
        self.spawn_y = y

    def respawn(self) -> None:
        """Resets player position back to their baseline spawn point."""
        self.x, self.y = self.spawn_x, self.spawn_y
