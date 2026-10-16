# Project Analysis and Choices

## 1. Goal

Deliver a complete, playable Pac-Man in Python (3.10+), written with object-oriented programming, configurable through a JSON-with-comments file, using an externally assigned maze generator, with persistent highscores, a cheat mode for reviewers, and a build published on a public platform (Itch.io). Code quality rules: flake8, mypy, type hints, docstrings, no crash, no traceback.

## 2. Requirements breakdown

| Area        | Requirement (subject)                                            | Decision                                                                                                                                                                         |
| ----------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Launch      | `python3 pac-man.py config.json`, exactly one argument           | Entry point named `pac-man.py`, arguments checked first, clear error message, clean exit                                                                                         |
| Config      | JSON with `#` comments, defaults, clamping, unknown keys ignored | Dedicated `config_loader` module, every key validated with a fallback, any non-object JSON falls back to defaults                                                                |
| Maze        | Assigned A-Maze-ing package, used as-is, `PERFECT=False`         | Wheel vendored in `vendor/`, installed through `uv`, a `load_maze` helper adapts to its interface; errors caught                                                                 |
| Entities    | Player, 4 ghosts, pacgums, super-pacgums                         | Shared base `Entity` class, `Ghost` and `Player` subclasses                                                                                                                      |
| Ghost AI    | Chase when not edible, flee when edible, respawn when eaten      | BFS pathfinding on the maze grid; `GhostStates` enum (chase, scared, eaten); timers for state transitions                                                                        |
| Scoring     | X / Y / Z points, never decreases                                | Points read from the config                                                                                                                                                      |
| Highscores  | Top 10, validated names, robust to file errors                   | Stored in a JSON file; parsing hardened over several iterations                                                                                                                  |
| Progression | 10+ levels, timer, lives and score kept, pause                   | A `Game` runner class owns the game state and level flow                                                                                                                         |
| UI          | Menu, pause, game over, victory                                  | Done                                                                                                                                                                             |
| Cheat mode  | Must genuinely help the reviewer                                 | All five cheats suggested by the subject are implemented: invincibility, level skip, ghost freeze, extra lives and increased speed, so a reviewer can test every feature quickly |


## 3. Technical choices

### 3.1 Language, tooling, quality

- Python 3.10+, `uv` for dependency management
- flake8 and mypy 
- Type hints and docstrings on functions and classes.

### 3.2 Graphics library

We use **pygame**. The subject allows "MLX or similar", and pygame fits that. Why:

- Keyboard input (arrow keys / WASD), drawing and sprite animation are built in.
- Easy to install as a regular Python dependency through `uv`. 
- compatible with common packaging tools.

### 3.3 Architecture

- `Entity` base class: position and movement shared by all moving objects.
- `Ghost` and `Player`.
- `Game` runner class: main loop, collisions, scoring, levels, state changes.
- Separate modules for config loading, maze loading, highscores and UI.

### 3.4 Ghost behavior

The subject leaves the chase behavior open. Instead of four identical chasers:

- Shared movement uses BFS pathfinding toward the target.
- Different behaviors were given to different ghosts: direct chase, a "shy" chase, and random movement chosen per corner.
- While scared, ghosts flee and avoid backtracking by tracking recently visited cells.
- When eaten they return to their corner, then re-enter play after a delay.

Why: it reproduces the spirit of the original game (each ghost has a personality) and keeps the game fair and varied.

### 3.5 Maze handling

- Level 1 uses the fixed seed from the config, later levels use random mazes.
- The loader works for any maze size.
- Pacgums are placed in corridors with some cells excluded: the four corners (super-pacgums and ghost homes), the center cell (player spawn) and the 42 cells.
- The generator is never modified, failures are handled in the loader.

### 3.6 Highscores

JSON file named by `highscore_filename` in the config. human readable, easy to validate, simple to keep top 10. Robustness (missing file, invalid format, bad names or scores)

### 3.7 Timeout rule

The subject lets us decide what happens when the level timer reaches zero. When the level timer reaches zero, the game ends (game over screen, then name entry for the highscore, then back to the main menu). Why: it gives the timer real consequences, so the player must keep moving and clear the maze, and it reuses the existing game over flow without adding a new state.

## 4. Alternatives considered

| Topic                 | Option A               | Option B                     | Chosen   | Why                                      |
| --------------------- | ---------------------- | ---------------------------- | -------- | ---------------------------------------- |
| Ghost AI              | Identical direct chase | Distinct behaviors per ghost | B        | More interesting, closer to the original |
| Highscore storage     | Plain text             | JSON                         | JSON     | Structured, easy to validate             |
| Dependency management | pip + requirements     | `uv`                         | `uv`     | Fast, reproducible                       |
| Maze generator        | Write our own          | Use the assigned package     | Assigned | Required by the subject                  |

