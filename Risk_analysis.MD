# Risk Analysis and Possible Mitigation

**What it is:** A formal identification of technical, architectural, and operational threats that could have derailed the engine, alongside the engineering countermeasures used to neutralize them.

- ### Risk: Render Pipeline CPU/Hard Drive Throttling
    - **Threat:** Requesting the operating system to perform hard-drive I/O and matrix scalling math for entity assets (like ghosts) inside a 60 fps rendring loop, this risks severe frame-rate drops and CPU bottlenecking.
    - **Mitigation:** Shifte all pygame.image.load() and pygame.transform.scale() operations to the class initialization phase, Assets are resterized and stored in a presistent RAM dictionary, reducing rednfering overhead to simple memory lookups and blit operations.
- ### Risk: Memory Exhaustion via Malicious File I/O
    - **Threat:** An attacker or corrupted system modifies the highscore.json file to be gigabytes in size or injects deeply nested data structres, triggering an OS-level Out of memory or infinit recursion crashes when json.load() attempts to allocate it.
    - **Mitigation:** implemented a two layer defensive pipeline, first an os level os.path.getsise() check aborts the load if the file exceeds a strict kb threshold, Second a resursive memory filter sanitizes the JSON structure, guaranteeing only flat, properly typed dictionaries enter the game's instance memory.
- ### Risk: Procedural Generation Deadlocks
    - **Threat:** Modifying configuartion parameters alters the procedural bitmask generation of the maze, creatng the risk of the player spawning inside a closed wall cell and sof-locking the game.
    - **Mitigation:** Removed hardcoded spawm coordinates, implemented dynamic spawn resolution by inspecting the grid's bitmask at runtime to locate a guaranteed open pathway before placing the player entity.