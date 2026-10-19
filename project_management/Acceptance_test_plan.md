# Acceptance Test Plan(Features Tested, Bugs Found and Fixed)

- **Test Category:** State Presistence and Transition Logic
    - **Feature Tested:** Cheat mode (lvel skip) triggering the game-ove state.
    - **Bug found:** Triggering the skip via keyboard events executed a return statement prematurely, destrying the local execution stack before the custom UI messages could be passed to the next screen, the engine defaulted to fallback text.
    - **Fixe Implemented:** Injected the specific game ove string directly into the shared self.config dictionary in memory before the loop transition, bridging the gap between decoupled UI classes.

- **Test Category:**  Highscore Data integrity
    - **Feature Tested:** Reading and sorting external JSON saves.
    - **Bug Found:** Injecting nested arrays into the file caused the sorted lambda function to throw a TypeERROR crasing the engine
    - **Fix implemented:** Rerouted all raw file data through the custom data validation method parior to sorting and appending, ensuring malicious data types are silently discarded.

- **Test Category:** Physics and Input Initialization
    - **Feature Tested** Initial player movement on map sawn.
    - **Bug Found:** The Player entity initiated movement without the user input on the first frame tick because the dafault state variable conatined an active direction vector. 
    - **Fix Implemented:**Abstracted the initial movement state to a neutral/idle vector, impementing a logical guard in the move_player method to prevent coordinate translation until explicit use input is dected.

- **Test Category:** Player spawn point
    - **Feature Tested:** initial player spawn point on the middle of the map
    - **Bug Found:** The player get jailed inside a fully closed cell when used just a simple calculation of the middle of the map
    - **Fix Implemented:** Using BFS to find the closest available cell for the player to spawn on 