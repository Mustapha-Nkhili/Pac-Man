from typing import Any

from mazegenerator import MazeGenerator

UP, RIGHT, DOWN, LEFT = 1, 2, 4, 8


<<<<<<< HEAD
def load_maze(width: int = 15, height: int = 15, seed: int = 0, perfect: bool = False):
=======
def load_maze(
    width: int = 15, height: int = 15, seed: int = 0, perfect: bool = False
) -> dict[str, Any]:
    """Creates a new maze grid with a specific size and random seed.

    Args:
        width: The total number of columns in the grid.
        height: The total number of rows in the grid.
        seed: The random number seed used to generate the map.
        perfect: If True, the maze has no loops or open rooms.

    Returns:
        A dictionary containing the maze matrix data, width, and height.
    """
>>>>>>> origin/main
    generator = MazeGenerator(size=(width, height), seed=seed, perfect=perfect)

    return {"maze": generator.maze, "width": width, "height": height}


<<<<<<< HEAD
def can_move(maze_grid, y, x, direction):
=======
def can_move(
    maze_grid: list[list[int]], y: int, x: int, direction: int
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
>>>>>>> origin/main
    return not maze_grid[y][x] & direction
