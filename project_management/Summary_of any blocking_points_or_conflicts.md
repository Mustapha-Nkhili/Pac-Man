# Summary of Blocking Points or Conflicts

## Blocking Point: Variable Scope and Garbage collection Disconnects
- **Issue:** A major hurdle during data validation was passing sanitized data from local utitlity functions into the permanent graphics rendering loop, vecayse pythons grbage collector instantly destroys local variables upong method completion, early iteration of the scoreboard rendered completely blank despite successful file parsing.

- **Resolution:** Mapped local output variables explicitly to presistent class instance variables locking the data into the object's state space so the rendering loop could read it on subsequent frames.

## Conflict: Managing Global state without Global Variables
- **Issue:** As the engine grew, multiple decoupled screens (Gameplay, Main menu, Highscore UI) needed access to shared data passing all the needed data individually through `__init__` parameters became unmaintainable.

- **Resolution:** Standarized a centralized config dictionary that act as signle source of truth in memory, by passing this single reference to all ui classes, distinct components could read and mutate game states asynchronously without violating object-oriented design principles

## Conflict: Workload Imbalance and Resource Dilution

- **Issue:** A critical project-managment conflict arose when collaborator divided their attention across multiple concurrent projects, this lack of dedicated focus created availability bottlenecks, progress on the engine stalled because dependent modules had to wait fot the collaborator's unfinished logic.

- **Resolution:** Shifted the development strategy to defensively decouple our worflows, By establishing stric data contracts early, defining the exact dictionary structure the UI would expect, I was able to continue building the frontend and security pipelines using dummy data, i also took direct ownership of the project critical path the core game loop and memory management ensuring the engine's baseline progressed independently of asynchronous peer schedules.
