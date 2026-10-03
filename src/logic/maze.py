from mazegenerator import MazeGenerator

UP, RIGHT, DOWN, LEFT = 1, 2, 4, 8

def load_maze(width: int = 15, height: int = 15, seed: int = 0, perfect: bool = False):
    generator = MazeGenerator(size=(width, height), seed=seed, perfect=perfect)

    return {
        "maze": generator.maze,
        "width": width,
        "height": height
    }


def can_move(maze_grid, y, x, direction):
    return (not maze_grid[y][x] & direction)
