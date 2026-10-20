import json
import os
from itertools import cycle
from json import JSONDecodeError

import pygame

from src.resources import resource_path
from src.logic.entities import Player
from src.logic.game_state import GameState
from src.logic.ghost import Ghost, GhostCorners, GhostStates
from src.logic.maze import DOWN, LEFT, RIGHT, UP, load_maze

CELL_SIZE = 20
BACKGROUND = (28, 28, 31)
PLAYER_DELAY = 150
FAST_PLAYER_DELAY = 50
FRAME_PER_IMAGE = 8
GHOST_DELAY = 600


class Gameplay:
    """Main gameplay screens: maze, player, ghosts, pacgums and hud.

    Loads each level, moves the player and ghosts, resolves collisions
    and pacgums eating runs the countdown timer and
    draws everything, upadte return the name of the next screen when the
    game next the game ends, otherwise None.

    Atrributes: KEYS: Maps arrow key and WASD to maze direction constants,
    DIRE: Maps maze direction codes to the rotation in
    degrees applied to the Pac-man sprite (which faces right by default).
    """

    KEYS = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
        pygame.K_w: UP,
        pygame.K_s: DOWN,
        pygame.K_a: LEFT,
        pygame.K_d: RIGHT,
    }
    DIRE = {
        1: 90,
        2: 0,
        8: 180,
        4: -90,
    }

    def __init__(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        pac_images: list[pygame.Surface],
        config: dict,
        buttons: list,
        game_state: GameState,
    ) -> None:
        """Create tge gameplay screen and load the first level.

        Args:
        screen: Surface everything is drawn on.
        font: FOnt used for the HUD text.
        pac_images: Animation frames for the Pac-Man sprite
        config: parse game configuration
        (levels, lives, seed, points, pacgum count).
        buttons: Buttons shown during gameplay
        game_state: shared game logic object for pacgums placement
        and collision handling.
        """
        self.screen: pygame.Surface = screen
        self.font: pygame.font.Font = font
        self.pac_images: list[pygame.Surface] = pac_images
        self.config: dict = config
        self.buttons: list = buttons
        self.level_index: int = 0
        self.game_state: GameState = game_state
        self.speed_bost: bool = False
        self.invinsible: bool = False
        self.frozen: bool = False
        self.get_time: float = 0.0
        self.ghost_img: dict = {
            "red": pygame.image.load(resource_path("img/ghost.png")).convert_alpha(),
            "pink": pygame.image.load(resource_path("img/pink_ghost.png")).convert_alpha(),
            "yellow": pygame.image.load(
                resource_path("img/yellow_ghost.png")).convert_alpha(),
            "green": pygame.image.load(resource_path("img/green_ghost.png")).convert_alpha(),
        }
        self.reset()

    def reset(self) -> str | None:
        """
        Load the current level and reset all pre-level state

        Build the maze from the configured seed and level size, creates
        (or respawn) the player,
        spawns one ghost per corner restarts timers and the sprite animation,
        computes the cell size and centering
        offsets and places pacgums and superpacgums.

        Returns:
        "name_entry" if there are no level left to load, otherwise None.
        """
        if len(self.config["level"]) <= self.level_index:
            self.config["end_game"] = (
                "Congratulation, Type your name to save your score"
            )
            return "name_entry"
        level = self.config["level"][self.level_index]
        maze = load_maze(level["width"], level["height"], self.config["seed"])
        self.maze_grid = maze["maze"]
        self.qued_move: int | None = None
        midx = len(self.maze_grid[0]) // 2
        midy = len(self.maze_grid) // 2
        safe_x, safe_y = self.find_open_cell(midx, midy)
        width, hieght = self.screen.get_size()
        if getattr(self, "player", None) is None:
            self.player = Player(
                x=safe_x,
                y=safe_y,
                lives=self.config["lives"],
                direction=RIGHT,
                maze_grid=self.maze_grid,
            )
        else:
            self.player.respawn()
            self.player.x, self.player.y = safe_x, safe_y
            self.player.old_x, self.player.old_y = safe_x, safe_y
            self.player.maze_grid = self.maze_grid
        self.ghost = Ghost(
            direction=RIGHT,
            maze_grid=self.maze_grid,
            corner=GhostCorners.BOTTOMRIGHT,
            color="red",
        )
        self.ghost3 = Ghost(
            direction=RIGHT,
            maze_grid=self.maze_grid,
            corner=GhostCorners.TOPLEFT,
            color="pink",
        )
        self.ghost2 = Ghost(
            direction=RIGHT,
            maze_grid=self.maze_grid,
            corner=GhostCorners.TOPRIGHT,
            color="green",
        )
        self.ghost4 = Ghost(
            direction=RIGHT,
            maze_grid=self.maze_grid,
            corner=GhostCorners.BOTTOMLEFT,
            color="yellow",
        )
        self.ghosts_list = [self.ghost, self.ghost2, self.ghost3, self.ghost4]
        self.ghost_last_move: float = 0.0
        self.time_left = self.config["level_max_time"]
        self.cell_size = min(width // level["width"], (
            hieght - 400) // level["height"])
        self.offset_x = (width - len(self.maze_grid[0]) * self.cell_size) // 2
        self.offset_y = (hieght - len(self.maze_grid) * self.cell_size) // 2
        self.last_move: float = 0.0
        self.frame_counter = 0
        self.pac_animation = cycle(self.pac_images)
        self.current_image = next(self.pac_animation)
        self.excluded = {
            (0, 0),
            (maze["width"] - 1, 0),
            (0, maze["height"] - 1),
            (maze["width"] - 1, maze["height"] - 1),
        }
        self.pacgums = self.game_state.place_pacgums(
            maze["width"], maze["height"], maze["maze"], self.config["pacgum"]
        )
        self.super_pacgums = self.game_state.place_super_pacgums(
            maze["width"], maze["height"]
        )
        return None

    def find_open_cell(self, midx: int, midy: int) -> tuple[int, int]:
        """
        Find the valid center spawn cell.

        Args:
            midx: horizontal middle cell
            midy: vertical middle cell

        Returns:
            A set of the valid spawn cords.
        """
        queue = [(midx, midy)]
        visited = set([(midx, midy)])
        while queue:
            curr_x, curr_y = queue.pop(0)
            if self.maze_grid[curr_y][curr_x] < 15:
                return (curr_x, curr_y)
            for dx, dy in [(0, -1), (-1, 0), (1, 0), (0, 1)]:
                nx, ny = curr_x + dx, curr_y + dy
                if (0 <= nx < len(self.maze_grid[0]) and
                        0 <= ny < len(self.maze_grid)):
                    if (nx, ny) not in visited:
                        # print(visited)
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        return (midx, midy)

    def update_ghost_state(self, now: float) -> None:
        """
        Respawn ghost after a set amount of time.
        """
        for ghost in self.ghosts_list:
            if ghost.state == GhostStates.EATEN:
                if ghost.respawn_until == 0:
                    ghost.x, ghost.y = ghost._get_corner()
                    ghost.respawn_until = int(now) + ghost.respawn_duration
                elif now >= ghost.respawn_until:
                    ghost.respawn()
            elif (ghost.state == GhostStates.SCARED and
                    now >= ghost.scared_until):
                ghost.state = GhostStates.CHASE

    def reset_after_death(self) -> None:
        """
        Reset the player and ghost to their default place

        Returns:
            None
        """
        midx = len(self.maze_grid[0]) // 2
        midy = len(self.maze_grid) // 2
        safe_x, safe_y = self.find_open_cell(midx, midy)
        for ghost in self.ghosts_list:
            ghost.respawn()
        self.qued_move = None
        self.player.x, self.player.y = safe_x, safe_y
        self.player.old_x, self.player.old_y = safe_x, safe_y

    def update(
            self,
            events: list[pygame.event.Event],
            dt: float) -> str | None:
        """
        Advance the game by one frame.

        Handles cheat keys and button clicks, decreases the remaining time
        cheks end conditions (time out, no lives, no levels left), then
        resolves collisions, animation, pacgum eating, ghost,
        movements, player movements, and queued direction input.

        Args:
            events: Pygame events collected this frame.
            dt: Seconds elapsed since the previous frame.

        Returns:
            "name_entry": when the game is over, otherwise None.
        """
        self.get_time += dt * 1000
        for event in events:
            for button in self.buttons:
                if button.handle_event(event):
                    return None
        if self.cheat_mode(events):
            self.config["end_game"] = self.config["end_game"] = (
                "Congratulation, Type your name to save your score"
            )
            return "name_entry"
        self.time_left = max(self.time_left - dt, 0)
        if self.time_left == 0:
            self.config["end_game"] = "Oh Oh time is up"
            return "name_entry"
        if self.player.lives <= 0:
            self.config["end_game"] = "Game is over good luck next time"
            return "name_entry"
        if len(self.config["level"]) <= self.level_index:
            self.config["end_game"] = (
                "Congratulation, Type your name to save your score"
            )
            return "name_entry"
        # now = pygame.time.get_ticks()
        now = self.get_time
        if not self.invinsible:
            lives = self.player.lives
            self.game_state.check_collisions(
                self.player, self.ghosts_list, self.config["points_per_ghost"]
            )
            if self.player.lives < lives:
                self.reset_after_death()
        self.update_ghost_state(now)
        self.animate()
        self.eat_pacgum()
        self.eat_super_pacgum()
        # now = pygame.time.get_ticks()
        now = self.get_time
        if not self.frozen and now - self.ghost_last_move >= GHOST_DELAY:
            for ghost in self.ghosts_list:
                ghost.take_turn(self.player.x, self.player.y)
            self.ghost_last_move = now
        player_delay = FAST_PLAYER_DELAY if self.speed_bost else PLAYER_DELAY
        if now - self.last_move >= player_delay and self.move_player():
            self.last_move = now
        keys = pygame.key.get_pressed()
        for key, direction in self.KEYS.items():
            if keys[key]:
                self.qued_move = direction
                break
        return None

    def draw_pacgums(self) -> None:
        """Draw every remaining regular pacgum as a small white dot."""
        for x, y in self.pacgums:
            center = self.center_cell(x, y)
            pygame.draw.circle(self.screen, "white", center, 2)

    def draw_super_pacgums(self) -> None:
        """Draw every renaining superpagums as a large white dot."""
        for x, y in self.super_pacgums:
            center = self.center_cell(x, y)
            pygame.draw.circle(self.screen, "white", center, 6)

    def eat_pacgum(self) -> None:
        """Advance to the next level if no pacgums remain, then process pacgums
        collection and scoring for the player's current cell."""
        if len(self.pacgums) <= 0:
            self.level_index += 1
            self.reset()
        self.game_state.check_pacgums_collisions(
            self.player, self.pacgums, self.config["points_per_pacgum"]
        )

    def eat_super_pacgum(self) -> None:
        """Process superpacgums collection, awrding points and scaring the
        ghosts that have not been eaten."""
        self.game_state.check_superpacgums_collisions(
            self.player,
            self.super_pacgums,
            self.ghosts_list,
            int(self.get_time),
            self.config["points_per_super_pacgum"],
        )

    def animate(self) -> None:
        """Advance the pacman sprite to it's next animation frame every
        FRAME_PER_IMAGE calls."""
        self.frame_counter += 1
        if self.frame_counter >= FRAME_PER_IMAGE:
            self.current_image = next(self.pac_animation)
            self.frame_counter = 0

    def move_player(self) -> bool | None:
        """Move the player one cell, preferring the queued direction.

        if the queued direction is blocked, keeps moving in the current
        direction. Updated the player's previous position

        Returns:
            True if the player changed cell, False otherwise
        """
        if not self.qued_move:
            return None
        before = (self.player.x, self.player.y)
        self.player.old_x, self.player.old_y = before
        if self.qued_move:
            self.player.move(self.qued_move)
        if (self.player.x, self.player.y) == before:
            self.player.move(self.player.direction)
        else:
            self.player.direction = self.qued_move
        return (self.player.x, self.player.y) != before

    def origin_cell(self, x: int, y: int) -> tuple[int, int]:
        """Return the top lef screen pixel of a maze cell
        Args:
            x: cell column.
            y: cell row.
        Returns:
            (top, left) pixel cirrdubates including the maze offset.
        """
        return (self.offset_x + x * self.cell_size,
                self.offset_y + y * self.cell_size)

    def center_cell(self, x: int, y: int) -> tuple[int, int]:
        """Rturn the center screen pixel of a maze cell.
        Args:
            x: cell colums.
            y: cell row.
        Returns:
            (centerx, centery) pixel coordinates.
        """
        left, top = self.origin_cell(x, y)
        return left + self.cell_size // 2, top + self.cell_size // 2

    def draw(self) -> None:
        """Draw the whole gameolay screen: backgrounds,
        maze, pacgums, ghosts, player, HUD and buttons."""
        self.screen.fill(BACKGROUND)
        self.draw_maze()
        self.draw_super_pacgums()
        self.draw_pacgums()
        self.draw_ghost()
        self.draw_player()
        self.draw_hud()
        for button in self.buttons:
            button.draw()

    def cheat_mode(
                self,
                events: list[pygame.event.Event] | None = None) -> bool:
        """Apply the cheat bound to a pressed key"""
        if events:
            for event in events:
                if (event.type != pygame.KEYDOWN or not
                        event.mod & pygame.KMOD_SHIFT):
                    continue
                if event.key == pygame.K_l:
                    self.player.lives += 1
                elif event.key == pygame.K_n:
                    self.level_index += 1
                    if self.level_index >= len(self.config["level"]):
                        return True
                    self.reset()
                elif event.key == pygame.K_i:
                    self.invinsible = not self.invinsible
                elif event.key == pygame.K_f:
                    self.frozen = not self.frozen
                elif event.key == pygame.K_v:
                    self.speed_bost = not self.speed_bost
        return False

    def draw_maze(self) -> None:
        """
        Draw the maze walls.
        Each cell value is a bitmask: 1 = top wall, 2 = right wall,
        4 = bottom wall, 8 left wall.
        """
        for y, n in enumerate(self.maze_grid):
            for x, cell in enumerate(n):
                left, top = self.origin_cell(x, y)
                right, bottom = left + self.cell_size, top + self.cell_size
                if cell & 1:
                    pygame.draw.line(self.screen, "white", (left, top), (
                            right, top), 1)
                if cell & 2:
                    pygame.draw.line(
                        self.screen, "white", (right, top), (right, bottom), 1
                    )
                if cell & 4:
                    pygame.draw.line(
                        self.screen, "white", (left, bottom), (
                                right, bottom), 1
                    )
                if cell & 8:
                    pygame.draw.line(
                        self.screen, "white", (left, top), (left, bottom), 1
                    )

    def draw_player(self) -> None:
        """Draw the rotated pacman sprite,
        interpolated between the previous and current cell
        base on time since the last move."""
        # now = pygame.time.get_ticks()
        now = self.get_time
        player_delay = FAST_PLAYER_DELAY if self.speed_bost else PLAYER_DELAY
        t = min((now - self.last_move) / player_delay, 1.0)
        old_center = self.center_cell(self.player.old_x, self.player.old_y)
        new_center = self.center_cell(self.player.x, self.player.y)
        lerp_x = old_center[0] + (new_center[0] - old_center[0]) * t
        lerp_y = old_center[1] + (new_center[1] - old_center[1]) * t
        scaled_img = pygame.transform.scale(
                self.current_image,
                (self.cell_size / 2, self.cell_size / 2))
        img = pygame.transform.rotate(
            scaled_img, self.DIRE[self.player.direction]
        )
        self.screen.blit(img, img.get_rect(center=(lerp_x, lerp_y)))

    def draw_ghost(self) -> None:
        """Draw every ghost centered on it's current cell."""
        for ghost in self.ghosts_list:
            if ghost.state == GhostStates.EATEN:
                continue
            ghost_img = pygame.transform.scale(
                self.ghost_img[ghost.color], (
                        self.cell_size / 2, self.cell_size / 2)
            )
            center = self.center_cell(ghost.x, ghost.y)
            self.screen.blit(ghost_img, ghost_img.get_rect(center=center))

    def draw_hud(self) -> None:
        """Draw lives, score, remaining time and current level,
        active cheats and ghosts states on the left."""
        lines = [
            f"Lives: {self.player.lives}",
            f"scores: {self.player.score}",
            f"time_left: {self.time_left:.1f}",
            f"level: {self.level_index + 1}",
            f"cheat: {" ".join(self.active_cheats())}",
            f"Ghost_state: {" ".join(self.active_states())}",
        ]
        for i, text in enumerate(lines):
            surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (20, 30 + i * 120))

    def active_cheats(self) -> list[str]:
        """Keep track of the active cheats.

        Returns:
            A list of the active cheats.
        """
        active = []
        if self.invinsible:
            active.append("INV")
        if self.speed_bost:
            active.append("BOOST")
        if self.frozen:
            active.append("FRZ")
        return active

    def active_states(self) -> list[str]:
        """Keep track of the active ghosts states.

        Returns:
            A list of the active ghosts states.
        """
        active: list[str] = []
        for ghost in self.ghosts_list:
            if ghost.state == GhostStates.SCARED:
                if ("Scared") not in active:
                    active.append("Scared")
            if ghost.state == GhostStates.CHASE:
                if "Chase" not in active:
                    active.append("Chase")
        return active


class Name_entry:
    """
    Screen where the player types a name to save their score.

    Acceps up to 10 alphanumeruc characters and saves the entry to the
    highscore file when Enter is pressed.
    """

    def __init__(
                self, screen: pygame.Surface, font: pygame.font.Font,
                score: int, config: dict, buttons: list) -> None:
        """
        Create the name entry screen.

        Args:
            screen: Surface to draw on.
            font: Font used for all text.
            score: Final score to display and save.
            config: Prased game configuration.
        """
        self.screen: pygame.Surface = screen
        self.font: pygame.font.Font = font
        self.player_name: str = ""
        self.score: int = score
        self.config: dict = config
        self.button: list = buttons

    def update(
                self, events: list[pygame.event.Event],
                dt: float) -> str | None:
        """
        Handle typing and saving.

        Backspace deltes the last character.
        Enter saves the entry (an empty name defaults to "Player"),
        which is validated, sortedby score and trimmed to the top 10.

        Args:
            events: Pygame events collected this frame.
            dt: seconds elapsed since the previous frame

        Returns: "highscores" after a successfull save, otherwise None.
        Nothign is saved if the file is too large, malformed or unreadable.
        """
        try:
            for event in events:
                for button in self.button:
                    if button.handle_event(event):
                        return "main_menu"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.player_name == "":
                            self.player_name = "Player"
                        name_entry = {
                            "name": self.player_name,
                            "score": self.score}
                        highscores = []
                        if os.path.exists(
                            self.config.get(
                                "highscore_filename",
                                "highscores.json")
                        ):
                            if (
                                os.path.getsize(
                                    self.config.get(
                                        "highscore_filename", "highscores.json"
                                    )
                                )
                                // 1024
                                > 100
                            ):
                                print("FILE TOO BIG")
                                return None
                            with open(
                                self.config.get(
                                    "highscore_filename", "highscores.json"
                                ),
                                "r",
                            ) as f:
                                highscores = json.load(f)
                        if not isinstance(highscores, list):
                            print("invalid data format")
                            return None
                        valid_data = HighScoreScreen.dig(highscores)
                        highscores = valid_data
                        highscores.append(name_entry)
                        highscores = sorted(
                            highscores, key=lambda item: item["score"],
                            reverse=True
                        )
                        highscores = highscores[:10]
                        with open(
                            self.config.get(
                                "highscore_filename",
                                "highscores.json"),
                                "w",
                        ) as f:
                            json.dump(highscores, f, indent=4)
                        self.player_name = ""
                        return "highscores"
                    else:
                        if (event.unicode.isalnum() and
                                len(self.player_name) < 10):
                            self.player_name += event.unicode
        except (JSONDecodeError, PermissionError) as e:
            print({e})
        return None

    def draw(self) -> None:
        """Draw the prompt, the achieved score and name input box."""
        self.screen.fill((28, 28, 28))
        display_text = self.config.get(
            "end_game",
            "Enter you name to save your score")
        Game_over = self.font.render(
            display_text,
            True,
            "white",
        )
        score_sur = self.font.render(f"{self.score} Pts", True, "white")
        text_sur = self.font.render(self.player_name, True, "black")
        score_rect = score_sur.get_rect(center=(1280 // 2, 300))

        rect = text_sur.get_rect(center=(1280 // 2, 720 // 2))
        rect_rect = pygame.Surface((250, 50)).get_rect(center=(
                    1280 // 2, 720 // 2))
        game_rect = Game_over.get_rect(center=(1280 // 2, 70))
        pygame.draw.rect(self.screen, "white", rect_rect)
        self.screen.blit(text_sur, rect)
        self.screen.blit(score_sur, score_rect)
        self.screen.blit(Game_over, game_rect)
        for button in self.button:
            button.draw()


class HighScoreScreen:
    """Screen displaying the top 10 saved scores."""

    def __init__(
                self,
                screen: pygame.Surface, font: pygame.font.Font,
                config: dict, buttons: list) -> None:
        """Create the highscore screen.

        Args:
            screen: Surface to draw on.
            font: Font used for all text.
            config: parse game configuration.
            buttons: Buttons shown on the screen.
        """
        self.screen: pygame.Surface = screen
        self.font = font
        self.config = config
        self.button = buttons
        self.scores_data: list[dict] = []

    def load_data(self) -> None:
        """
        Load and valudate scores from the highscore file.

        Does noting if the file is larger than 100kb or the json is not a list.
        Read and parse errors are caught and reported.
        """
        try:
            validating_data = []
            if os.path.exists(self.config.get(
                        "highscore_filename",
                        "highscores.json")):
                if (
                    os.path.getsize(
                        self.config.get(
                            "highscore_filename",
                            "highscores.json")
                    )
                    // 1024
                    > 100
                ):
                    print("FILE TOO BIG")
                    return
                with open(
                    self.config.get(
                        "highscore_filename",
                        "highscores.json"),
                        "r"
                ) as f:
                    validating_data = json.load(f)
            if not isinstance(validating_data, list):
                print("invalid data format")
                return
            valid_data = HighScoreScreen.dig(validating_data)
            self.scores_data = valid_data
        except (JSONDecodeError, PermissionError) as e:
            print({e})

    @staticmethod
    def dig(validating_data: list) -> list:
        """Recursively collect valid score entries from parse JSON.

        Accepts a dict or an arbitrily nested list.
        an entry is accepted when it has a string name and no negative
        integer "score", Everything else is ignored.

        Returns:
            A flat list of the valid entry dicts.
        """
        valid_data = []
        if isinstance(validating_data, dict):
            if (
                "name" in validating_data
                and "score" in validating_data
                and not isinstance(validating_data["score"], bool)
                and isinstance(validating_data["name"], str)
                and isinstance(validating_data["score"], int)
                and validating_data["score"] >= 0
                and validating_data["name"].isalnum()
                and len(validating_data["name"]) <= 10
            ):
                valid_data.append(validating_data)
        elif isinstance(validating_data, list):
            for i in validating_data:
                dig_data = HighScoreScreen.dig(i)
                valid_data.extend(dig_data)
        return valid_data

    def update(
                self,
                events: list[pygame.event.Event],
                dt: float) -> str | None:
        """
        Forward events to the buttons.

        Args:
            events: Pygame events collected this frame.
            dt: seconds elapsed since the previous frame
        Returns:
            "main_menu" if a button was clicked, otherwise None
        """
        for event in events:
            for button in self.button:
                if button.handle_event(event):
                    return "main_menu"
        return None

    def draw(self) -> None:
        """Draw the title, the buttons and the ranked list of scores."""
        self.screen.fill("black")
        for button in self.button:
            button.draw()
        title_surf = self.font.render("Top 10 Scores", True, "Yellow")
        rect = title_surf.get_rect(center=(1280 // 2, 75))

        self.screen.blit(title_surf, rect)
        starting_y = 200
        spacing = 40
        for i, entery in enumerate(self.scores_data):
            text = f"{i + 1}. {entery["name"]}: {entery["score"]} pts"
            text_surf = self.font.render(text, True, "White")
            rect = text_surf.get_rect(center=(1280 // 2, starting_y))
            self.screen.blit(text_surf, rect)
            starting_y += spacing
