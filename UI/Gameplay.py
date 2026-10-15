from itertools import cycle

import pygame

from src.logic.entities import Ghost, GhostCorners, Player
from src.logic.maze import DOWN, LEFT, RIGHT, UP, load_maze
import os
import json
from json import JSONDecodeError

CELL_SIZE = 20
BACKGROUND = (28, 28, 31)
PLAYER_DELAY = 150
FAST_PLAYER_DELAY = 50
FRAME_PER_IMAGE = 8
GHOST_DELAY = 600


class Gameplay:
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

    def __init__(self, screen: pygame.Surface, font: pygame.font.Font,
                 pac_images: dict[str, pygame.Surface], config: dict,
                 buttons: list, game_state) -> None:
        self.screen = screen
        self.font = font
        self.pac_images = pac_images
        self.config = config
        self.buttons = buttons
        self.level_index = 0
        self.game_state = game_state
        self.speed_bost = False
        self.invinsible = False
        self.frozen = False
        self.ghost_img = {
            "red": pygame.image.load(
                "img/ghost.png").convert_alpha(),
            "pink": pygame.image.load(
                "img/pink_ghost.png").convert_alpha(),
            "yellow": pygame.image.load(
                "img/yellow_ghost.png").convert_alpha(),
            "green": pygame.image.load(
                "img/green_ghost.png").convert_alpha()
            }
        self.reset()

    def reset(self):
        if len(self.config["level"]) <= self.level_index:
            self.config["end_game"] = "Congratulation, Type your name to save your score"
            return "name_entry"
        level = self.config["level"][self.level_index]
        maze = load_maze(level["width"], level["height"], self.config["seed"])
        self.maze_grid = maze["maze"]
        self.qued_move = None
        width, hieght = self.screen.get_size()
        if getattr(self, "player", None) is None:
            self.player = Player(
                x=2,
                y=2,
                lives=self.config["lives"],
                direction=RIGHT,
                maze_grid=self.maze_grid,
            )
        else:
            self.player.respawn()
            self.player.maze_grid = self.maze_grid
        self.ghost = Ghost(
            direction=RIGHT, maze_grid=self.maze_grid,
            corner=GhostCorners.BOTTOMRIGHT, color="red"
        )
        self.ghost3 = Ghost(
            direction=RIGHT, maze_grid=self.maze_grid,
            corner=GhostCorners.TOPLEFT, color="pink"
        )
        self.ghost2 = Ghost(
            direction=RIGHT, maze_grid=self.maze_grid,
            corner=GhostCorners.TOPRIGHT, color="green"
        )
        self.ghost4 = Ghost(
            direction=RIGHT, maze_grid=self.maze_grid,
            corner=GhostCorners.BOTTOMLEFT, color="yellow"
        )
        self.ghosts_list = [self.ghost, self.ghost2, self.ghost3, self.ghost4]
        self.ghost_last_move = 0.0
        self.time_left = self.config["level_max_time"]
        self.cell_size = min(width // level["width"],
                             (hieght - 400) // level["height"])
        self.offset_x = (width - len(self.maze_grid[0]) * self.cell_size) // 2
        self.offset_y = (hieght - len(self.maze_grid) * self.cell_size) // 2
        self.last_move = 0
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

    def update(self, events, dt):
        for event in events:
            for button in self.buttons:
                if button.handle_event(event):
                    return None
        if self.cheat_mode(events):
            self.config["end_game"] = self.config["end_game"] = "Congratulation, Type your name to save your score"
            return "name_entry"
        self.time_left = max(self.time_left - dt, 0)
        if self.time_left == 0:
            self.config["end_game"] = "Oh Oh time is up"
            return "name_entry"
        if self.player.lives <= 0:
            self.config["end_game"] = "Game is over good luck next time"
            return "name_entry"
        if len(self.config["level"]) <= self.level_index:
            self.config["end_game"] = "Congratulation, Type your name to save your score"
            return "name_entry"
        if not self.invinsible:
            self.game_state.check_collisions(
                self.player, self.ghosts_list, self.config["points_per_ghost"]
            )
        self.animate()
        self.eat_pacgum()
        self.eat_super_pacgum()
        now = pygame.time.get_ticks()
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

    def draw_pacgums(self):
        for x, y in self.pacgums:
            center = self.center_cell(x, y)
            pygame.draw.circle(self.screen, "white", center, 2)

    def draw_super_pacgums(self):
        for x, y in self.super_pacgums:
            center = self.center_cell(x, y)
            pygame.draw.circle(self.screen, "white", center, 6)

    def eat_pacgum(self):
        if len(self.pacgums) <= 0:
            self.level_index += 1
            self.reset()
        self.game_state.check_pacgums_collisions(
            self.player, self.pacgums, self.config["points_per_pacgum"]
        )

    def eat_super_pacgum(self):
        self.game_state.check_superpacgums_collisions(
            self.player,
            self.super_pacgums,
            self.ghosts_list,
            pygame.time.get_ticks(),
            self.config["points_per_super_pacgum"],
        )

    def animate(self):
        self.frame_counter += 1
        if self.frame_counter >= FRAME_PER_IMAGE:
            self.current_image = next(self.pac_animation)
            self.frame_counter = 0

    def move_player(self):
        before = (self.player.x, self.player.y)
        self.player.old_x, self.player.old_y = before
        if self.qued_move:
            self.player.move(self.qued_move)
        if (self.player.x, self.player.y) == before:
            self.player.move(self.player.direction)
        else:
            self.player.direction = self.qued_move
        return (self.player.x, self.player.y) != before

    def origin_cell(self, x, y):
        return (self.offset_x + x * self.cell_size,
                self.offset_y + y * self.cell_size)

    def center_cell(self, x, y):
        left, top = self.origin_cell(x, y)
        return left + self.cell_size // 2, top + self.cell_size // 2

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.draw_maze()
        self.draw_super_pacgums()
        self.draw_pacgums()
        self.draw_ghost()
        self.draw_player()
        self.draw_hud()
        for button in self.buttons:
            button.draw()

    def cheat_mode(self, events=None):
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

    def draw_maze(self):
        for y, n in enumerate(self.maze_grid):
            for x, cell in enumerate(n):
                left, top = self.origin_cell(x, y)
                right, bottom = left + self.cell_size, top + self.cell_size
                if cell & 1:
                    pygame.draw.line(self.screen, "white", (left, top),
                                     (right, top), 1)
                if cell & 2:
                    pygame.draw.line(
                        self.screen, "white", (right, top), (right, bottom), 1
                    )
                if cell & 4:
                    pygame.draw.line(
                        self.screen, "white", (left, bottom),
                        (right, bottom), 1
                    )
                if cell & 8:
                    pygame.draw.line(
                        self.screen, "white", (left, top), (left, bottom), 1
                    )

    def draw_player(self):
        now = pygame.time.get_ticks()
        player_delay = FAST_PLAYER_DELAY if self.speed_bost else PLAYER_DELAY
        t = min((now - self.last_move) / player_delay, 1.0)
        old_center = self.center_cell(self.player.old_x, self.player.old_y)
        new_center = self.center_cell(self.player.x, self.player.y)
        lerp_x = old_center[0] + (new_center[0] - old_center[0]) * t
        lerp_y = old_center[1] + (new_center[1] - old_center[1]) * t
        img = pygame.transform.rotate(
            self.current_image, self.DIRE[self.player.direction]
        )
        self.screen.blit(img, img.get_rect(center=(lerp_x, lerp_y)))

    def draw_ghost(self):
        for ghost in self.ghosts_list:
            ghost_img = pygame.transform.scale(
                self.ghost_img[ghost.color], (self.cell_size / 2,
                                              self.cell_size / 2)
            )
            center = self.center_cell(ghost.x, ghost.y)
            self.screen.blit(ghost_img, ghost_img.get_rect(center=center))

    def draw_hud(self):
        lines = [
            f"Lives: {self.player.lives}",
            f"scores: {self.player.score}",
            f"time_left: {self.time_left:.1f}",
            f"level: {self.level_index + 1}",
            f"cheat: {" ".join(self.active_cheats())}",
        ]
        for i, text in enumerate(lines):
            surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (20, 30 + i * 120))

    def active_cheats(self):
        active = []
        if self.invinsible:
            active.append("INV")
        if self.speed_bost:
            active.append("BOOST")
        if self.frozen:
            active.append("FRZ")
        return active


class Name_entry:
    def __init__(self, screen, font, score, config) -> None:
        self.screen = screen
        self.font = font
        self.player_name = ""
        self.score = score
        self.config = config

    def update(self, events, dt):
        try:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.player_name == "":
                            self.player_name = "Player"
                        name_entry = {"name": self.player_name,
                                      "score": self.score}
                        highscores = []
                        if os.path.exists(
                            self.config.get("highscore_filename",
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
                                return
                            with open(
                                self.config.get(
                                    "highscore_filename", "highscores.json"
                                ),
                                "r",
                            ) as f:
                                highscores = json.load(f)
                        if not isinstance(highscores, list):
                            print("invalid data format")
                            return
                        valid_data = HighScoreScreen.dig(highscores)
                        highscores = valid_data
                        highscores.append(name_entry)
                        highscores = sorted(
                            highscores, key=lambda item: item["score"],
                            reverse=True
                        )
                        highscores = highscores[:10]
                        with open(
                            self.config.get("highscore_filename",
                                            "highscores.json"),
                            "w",
                        ) as f:
                            json.dump(highscores, f, indent=4)
                        return "highscores"
                    else:
                        if (event.unicode.isalnum() and
                                len(self.player_name) < 10):
                            self.player_name += event.unicode
        except (JSONDecodeError, PermissionError) as e:
            print({e})
        return None

    def draw(self):
        self.screen.fill((28, 28, 28))
        display_text = self.config.get("end_game", "Enter you name to save your score")
        Game_over = self.font.render(
            display_text,
            True,
            "white",
        )
        score_sur = self.font.render(f"{self.score} Pts", True, "white")
        text_sur = self.font.render(self.player_name, True, "black")
        score_rect = score_sur.get_rect(center=(1280 // 2, 300))

        rect = text_sur.get_rect(center=(1280 // 2, 720 // 2))
        rect_rect = pygame.Surface((250, 50)).get_rect(center=(1280 // 2,
                                                               720 // 2))
        game_rect = Game_over.get_rect(center=(1280 // 2, 70))
        pygame.draw.rect(self.screen, "white", rect_rect)
        self.screen.blit(text_sur, rect)
        self.screen.blit(score_sur, score_rect)
        self.screen.blit(Game_over, game_rect)


class HighScoreScreen:
    def __init__(self, screen, font, config, buttons) -> None:
        self.screen = screen
        self.font = font
        self.config = config
        self.button = buttons
        self.scores_data = []

    def load_data(self):
        try:
            validating_data = []
            if os.path.exists(self.config.get("highscore_filename",
                                              "highscores.json")):
                if (
                    os.path.getsize(
                        self.config.get("highscore_filename",
                                        "highscores.json")
                    )
                    // 1024
                    > 100
                ):
                    print("FILE TOO BIG")
                    return
                with open(
                    self.config.get("highscore_filename",
                                    "highscores.json"), "r"
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
    def dig(validating_data):
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

    def update(self, events, dt):
        for event in events:
            for button in self.button:
                if button.handle_event(event):
                    return "main_menu"
        return

    def draw(self):
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
            # Button(self.screen,390, 360, 200,50, self.font,"main_menu", self.asd())
            self.screen.blit(text_surf, rect)
            starting_y += spacing
    # @staticmethod
    # def asd():
    #     return "main_menu"