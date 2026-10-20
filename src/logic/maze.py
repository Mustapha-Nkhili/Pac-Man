from mazegenerator import MazeGenerator

UP, RIGHT, DOWN, LEFT = 1, 2, 4, 8


class MazeLoader:
    def load_maze(
        self,
        width: int = 15,
        height: int = 15,
        seed: int = 0,
        perfect: bool = False,
    ) -> list[list[int]]:
        """Creates a new maze grid with a specific size and random seed.

        Args:
            width: The total number of columns in the grid.
            height: The total number of rows in the grid.
            seed: The random number seed used to generate the map.
            perfect: If True, the maze has no loops or open rooms.

        Returns:
            A list containing the maze data.
        """
        try:
            generator = MazeGenerator(
                size=(width, height), seed=seed, perfect=perfect
            )
        except RecursionError:
            raise RuntimeError(
                f"Error: maze {width}x{height} is too large to generate"
            )

        maze: list[list[int]] = generator.maze
        return maze

    def can_move(
        self, maze_grid: list[list[int]], y: int, x: int, direction: int
    ) -> bool:
        """Checks if a specific path direction is open and has no wall.

        Uses a bitwise comparison to see if the chosen direction bit is set
        as a wall inside the map coordinate slot.

        Args:
            maze_grid: The full grid map matrix data to read from.
            y: The vertical row index of the position to test.
            x: The horizontal column index of the position to test.
            direction: The direction bit integer (UP, RIGHT, DOWN, or LEFT).

        Returns:
            True if the entity can move into that space, False if blocked.
        """
        return not maze_grid[y][x] & direction
