# Pac-Man




# Highscore
the highscore iterface triggeres when ever the player is in lose or win condition enabling the player to save their score if it ranks within the top 10, if the player submit an empry field the system safely defaults to the name `PLAYER`
- Input Sanitization: The UI only accepts alphanumeric characters to prevent Json parsign errors

- Data intergrity: Before rendering, the file passes throufh a recursive validation filter that explicitly checks data types and strips out corrupted enteries or malicious injections like nested lists or negative scores

- Memory Protection: the sytem check the file size at the os level before alocating ram, preventing the engine from crashing if a massive malicious edited file is loaded, capping the saved list to 10 enteries ensures the file footprint remains small  