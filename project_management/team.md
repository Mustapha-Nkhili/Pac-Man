# Team Organization

## 1. Team

| Member   | Login    | Role          |
| -------- | -------- | ------------- |
| Member A | mn-khili | Game logic    |
| Member B | maissam  | Visualisation |

## 2. Who did what

The work was split along one clear boundary: **game logic vs. visualisation**.

### Member A: game logic and core systems

- `Entity` base class and the `Ghost` and `Player` classes
- Ghost behavior: BFS pathfinding, ghost states (chase, scared, eaten), scared and eaten timers, per-ghost chase behaviors (random by corner, "shy" chase)
- Collisions: player with pacgums, player with super-pacgums, player with ghosts, with respawn logic
- Pacgum and super-pacgum placement
- Configuration parsing (comments, validation, defaults, fallbacks)
- Maze loading through the assigned A-Maze-ing package

### Member B: visualisation

- Everything displayed on screen: menus, maze drawing, sprites and animations (for example the Pac-Man sprite and its animation), ghost colors
- pause menu, game over and victory screens, instructions screen, highscore display, cheat mode, game progression

### Shared

- README, project management documents

## 3. How the work was organized

- **One branch per feature**, merged into `main`, mostly through pull requests .
- Branches mirror the split above: for example `feat/config-loader`, `feat/ghost`, `feat/ghost-states`, `feat/player`, `feat/game-state` and `feat/ghosts-behavior` for the logic, and `ui-changes` for the visualisation.
- A `Game` runner class connects both sides: the logic exposes the game state (positions, states, score, lives), and the visualisation reads it to draw it. Because the interface is the game state, both members could work in parallel without editing the same files.

## 4. How decisions were made

- **Split by responsibility.** The main decision was taken at the start: separate the project into game logic and visualisation. Each member owns one side and takes the decisions inside it, then explains them to the other.
- **Shared decisions.** Technical choices that affect both sides (what the game state exposes, config keys) were discussed together before coding.
- **Open design points.** The points left to the team by the subject (chase behavior, timeout rule, number and size of levels) were decided together, see `analysis.md` for the outcomes.
- **Avoiding disagreement.** Because each member has a clear responsibility, most conflicts and errors were avoided by design: we rarely edited the same files and could work in parallel on separate branches. The shared game state is the only interface, so a disagreement was limited to what that interface contains.

## 5. How issues were handled

| Issue                                                      | How it was handled                                                                                  |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Ghosts loop while scared                                   | Added tracking of recent cells to prevent backtracking                                              |
| Config file not a JSON object, boolean accepted as integer | Fixed with validation and fallbacks                                                                 |
| Maze loading depending on size                             | Loader rewritten to work for any size                                                               |
| Code growing hard to read                                  | Refactors: entities split, Ghost logic moved to its own module, entry point and `Game` runner class |


## 6. Communication and tools

- Git and GitHub: branches, pull requests
