from mazegenerator import MazeGenerator


def load_maze(width: int = 15, height: int = 15, seed: int = 0, perfect: bool = False):
    generator = MazeGenerator(size=(width, height), seed=seed, perfect=perfect)

    return {
        "maze": generator.maze,
        "width": width,
        "height": height
    }
