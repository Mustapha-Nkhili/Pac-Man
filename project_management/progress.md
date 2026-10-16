# Actual Progress vs. Timeline

## 1. Workflow actually used

- One branch per feature (`feat/config-loader`, `feat/ghost`, `feat/ghost-states`,
  `feat/player`, `feat/game-state`, `feat/ghosts-behavior`, `feat/final-improvements`, ...).
- Merged into `main` through pull requests (#1, #4, #5, #6, #7) or direct merges
  of `main` into the feature branch to resync.
- Tooling: `uv` for dependencies, flake8/mypy for linting, the assigned
  `mazegenerator` wheel vendored in a `vendor/` folder and used as-is.

## 2. Planned vs. actual, by milestone

| Milestone (plan)                  | Evidence in Git                                                                                                                                                                                                                        | Planned end | Actual | Status      | Notes                                                                                               |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------ | ----------- | --------------------------------------------------------------------------------------------------- |
| **M0 Setup**                      | `first commit`, `docs: add README.md`, `chore: add .gitignore`, `chore: setup uv`, `chore: add .venv folder in .gitignore`                                                                                                             | 09-21       | 09-21  | Done        | Repo, `.gitignore`, `uv` set up first, as planned                                                   |
| **M2 Maze integration**           | `chore: add mazegenerator wheel in vendor folder`, `chore(deps): update mazegenerator wheel file name`, `feat(maze): add load_maze helper`, later `the maze load properly now, no matter the size`                                     | 09-25       | 09-24  | Done        | Package used as-is; loader adapts to it. A later fix made loading size-independent                  |
| **M1 Config**                     | PR #1 `feat/config-loader`: comment stripping, value validation and fallback, missing keys, level array, flake8 fixes, `is_valid_int` rejecting booleans; later `fix: fallback to defaults if configuration file is not a JSON object` | 09-25       | 09-25  | Done        | Delivered after the maze loader (order swapped vs. plan); one robustness fix added afterwards       |
| **M3 Core engine**                | `feat: integrate config and maze loading into main`, `working game, still needing some fixes`, `refactor: rename entry point to pac-man.py and migrate to Game runner class`                                                           | 09-25       | 09-25  | Done        | First playable loop shortly after config + maze; later restructured into a `Game` runner class      |
| **M4 Gameplay: ghosts**           | PR #4 `feat/ghost` + `feat/ghost-states`: `Entity`/`Ghost` classes, BFS pathfinding, `GhostStates` enum, scared timer, EATEN state and reset                                                                                           | 10-06       | 10-16  | Done        | Planned as one block; split into two branches in practice                                           |
| **M4 Gameplay: player and items** | PR #5 `feat/player` (Player class); PR #6 `feat/game-state` (pacgum and super-pacgum collisions, randomized pacgum spawn excluding corners, ghost corner spawn, player collision and respawn)                                          | 10-06       | 10-06  | Done        | Pacgum placement rules (corners excluded, 42 cells and center excluded) refined during the work     |
| **M5 Progression (win/lose)**     | `feat/player` second round: winning and losing conditions merged (`fe589a1`)                                                                                                                                                           | 10-10       | 10-06  | Done        | Win/lose done. 10+ levels, level timer and timeout rule, pause/resume                               |
| **M6 UI**                         | `menu UI pacman collisoin handled`, `ui-changes`: pacman sprite and animation; fixes for flickering, ghost colors, pacman rendering                                                                                                    | 10-12       | 10-12  | Done        | Menu, sprites and animation exist. pause menu, game over and victory screens, instructions screen   |
| **M7 Highscores**                 | `feat/player`: score board, highscore entry, `highscore.json` parsing and error handling, parsing improvements                                                                                                                         | 10-16       | 10-16  | Done        | Several iterations on file-parsing robustness                                                       |
| **Ghost AI refinement**           | PR #7 `feat/ghosts-behavior`: Ghost logic moved to its own module, anti-backtracking while scared, random chase per corner, "shy" chase, random behavior for bottom-right ghost                                                        | no date     | 10-16  | Done        | Added after the plan: the subject leaves chase behavior open, so each ghost got a distinct behavior |
| **M10 Docs and QA**               | `docs: add README.md`, `docs: add project timeline`, docs in `config-loader`                                                                                                                                                           | 10-18       |        | In progress | README required sections, remaining project management docs and acceptance tests still to complete  |

## 3. Deviations and what we learned

1. **Order of work changed.** Config loading and maze integration were delivered in a
   different order than planned, but both landed before the game loop, so the
   critical path was respected.
2. **Ghosts took longer than planned.** They were split into `feat/ghost` and
   `feat/ghost-states`, then revisited in `feat/ghosts-behavior` for distinct
   behaviors.
3. **Highscore robustness needed several passes** (missing file, invalid format,
   name and score validation).
4. **Timeline written late.** Formalised after several features were merged.
