from collections.abc import Callable
from functools import partial
from typing import Any

import pygame

from src.resources import resource_path
from src.logic.maze import MazeLoader
from src.logic.game_state import GameState
from src.UI.Gameplay import Gameplay, HighScoreScreen, Name_entry
from src.UI.menu import Menu

WIDTH, HEIGHT = 1280, 720
FONT_PATH = resource_path("img/Pixel Game.otf")
FPS = 60


class Button:
    """Clickable rectangular button with hove and pressed colors."""

    COLORS = {
        "normal": (51, 55, 150),
        "hover": "#18285C",
        "pressed": "#919191",
    }

    def __init__(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        font: pygame.font.Font,
        text: str,
        on_click: Callable,
        color: dict = COLORS,
    ) -> None:
        """
        Create a button.

        Args:
            screen: Surface to draw on.
            x: left position in pixels.
            y: top position in pixels.
            width: button witdth in pixels.
            height: button height in pixels.
            font: Font usde to render the label.
            text: label text.
            on_click: callable invoked when the button is clicked.
            color: button color.
        """
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.on_click = on_click
        self.label = font.render(text, True, "white")
        self.color = color

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Run the click callback in a left mouse press inside the button.

        Args:
            event: Pygame event to inspect.

        Returns:
            True if the button was clicked, otherwise False.
        """
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        ):
            self.on_click()
            return True
        return False

    def draw(self) -> None:
        """
        Draw the button using the color for it's current state and it's label.
        """
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            state = "pressed" if pygame.mouse.get_pressed()[0] else "hover"
        else:
            state = "normal"
        pygame.draw.rect(self.screen, self.color[state], self.rect)
        self.screen.blit(
            self.label, self.label.get_rect(center=self.rect.center)
        )


class Game:
    """
    Application controller: owns the window, assets, screens and the main loop,
    and switches between screens by name.

    Attributes:
        CHCOLORS: red color set used for the cheat sheet button.

    """

    CHCOLORS = {
        "normal": (255, 0, 0),
        "hover": "#631616",
        "pressed": "#2B1B1B",
    }

    def __init__(
        self, game_state: GameState, config: dict, maze: MazeLoader
    ) -> None:
        """
        Initialize pyage, create the window and font, laod assets and screens.

        Args:
        game_state: Shared game logic object passed to the gameplay screen.
        config: parsed game config.
        """
        self.config = config
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac_Man")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, 48)
        self.running = True
        self.state = "main_menu"
        self.game_state = game_state
        self.maze = maze
        self.screens: dict[str, Any] = {}
        self.load_assets()
        self.load_screens()

    @staticmethod
    def images(
        path: str, size: tuple[int, int] | None = None
    ) -> pygame.Surface:
        """
        Load an image with transparency, optionaly scaled.

        Args:
            path: Path to the image file.
            size: Optional (width, height) to scale to.

        Returns:
            the converted pygame Surface.
        """
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size) if size else image

    def load_assets(self) -> None:
        """
        Load background, logo, pacman animation frames, and the ghost images"""
        window = (WIDTH, HEIGHT)
        self.logo = self.images(resource_path("./img/pacmanlogo"), (350, 150))
        self.menu_bg = self.images(resource_path("img/pause_back.jpg"), window)
        self.pause_bg = self.images(resource_path("img/pause.png"), (500, 150))
        self.pause_bg2 = self.images(
            resource_path("img/pause_back2.jpg"), window
        )
        self.instructions = self.images(
            resource_path("img/Instructions.png"), window
        )
        self.cheat_bg = self.images(
            resource_path("img/cheat_screen.png"), window
        )
        self.pac_images = [
            self.images(resource_path(f"img/{name}"), (14, 14))
            for name in (
                "pacmanopen.png",
                "pacmanclosed.png",
                "pacmanmid.png",
                "pacmant1.png",
                "pacmant2.png",
                "pacmant3.png",
                "pacmant4.png",
                "pacmant5.png",
                "pacmant6.png",
            )
        ]
        # self.ghost = self.images(resource_path("img/my_ghost.png"), (14, 14))

    def switch(self, state: str) -> Callable:
        """Create a callable that set the application state to `state`

        Args:
            state : the state to set

        Returns:
            a partial function that calls self.set_state(state) when invoked.
        """
        return partial(self.set_state, state)

    def load_screens(self) -> None:
        """Build every screen and store then by name in self.screens."""
        screen, font = self.screen, self.font
        # switch = lambda state: partial(self.set_state, state)
        self.screens = {
            "main_menu": Menu(
                screen,
                font,
                self.menu_bg,
                [
                    Button(
                        screen,
                        450,
                        150,
                        300,
                        100,
                        font,
                        "Start Game",
                        self.new_game,
                    ),
                    Button(
                        screen,
                        450,
                        275,
                        300,
                        100,
                        font,
                        "Highscores",
                        self.switch("highscores"),
                    ),
                    Button(
                        screen,
                        450,
                        400,
                        300,
                        100,
                        font,
                        "Instructions",
                        self.switch("instructions"),
                    ),
                    Button(
                        screen,
                        450,
                        525,
                        300,
                        100,
                        font,
                        "QUIT GAME",
                        self.quit,
                    ),
                ],
                images=[(self.logo, (420, 5))],
            ),
            "playing": Gameplay(
                screen,
                font,
                self.pac_images,
                self.config,
                [
                    Button(
                        screen,
                        640,
                        15,
                        100,
                        30,
                        font,
                        "Pause",
                        self.switch("pause"),
                    ),
                ],
                game_state=self.game_state,
                maze=self.maze,
            ),
            "pause": Menu(
                screen,
                font,
                self.pause_bg2,
                [
                    Button(
                        screen,
                        700,
                        360,
                        150,
                        50,
                        font,
                        "Resume",
                        self.switch("playing"),
                    ),
                    Button(
                        screen, 540, 460, 200, 50, font, "Quit Game", self.quit
                    ),
                    Button(
                        screen,
                        390,
                        360,
                        200,
                        50,
                        font,
                        "main_menu",
                        self.switch("main_menu"),
                    ),
                ],
                images=[(self.pause_bg, (400, 190))],
            ),
            "cheat_screen": Menu(
                screen,
                font,
                self.cheat_bg,
                [
                    Button(
                        screen,
                        400,
                        650,
                        200,
                        50,
                        font,
                        "main_menu",
                        self.switch("main_menu"),
                    )
                ],
            ),
            "instructions": Menu(
                screen,
                font,
                self.instructions,
                [
                    Button(
                        screen,
                        400,
                        650,
                        200,
                        50,
                        font,
                        "main_menu",
                        self.switch("main_menu"),
                    ),
                    Button(
                        screen,
                        650,
                        650,
                        250,
                        50,
                        font,
                        "Cheat_Sheet",
                        self.switch("cheat_screen"),
                        self.CHCOLORS,
                    ),
                ],
            ),
            "game_over": Menu(
                screen,
                font,
                "black",
                [
                    Button(
                        screen,
                        340,
                        380,
                        230,
                        50,
                        font,
                        "Play Again",
                        self.new_game,
                    ),
                    Button(
                        screen,
                        650,
                        380,
                        230,
                        50,
                        font,
                        "main_menu",
                        self.switch("main_menu"),
                    ),
                ],
                title="Game Over",
                title_pos=(520, 300),
            ),
            "highscores": HighScoreScreen(
                screen,
                font,
                self.config,
                [
                    Button(
                        screen,
                        550,
                        650,
                        200,
                        50,
                        font,
                        "main_menu",
                        self.switch("main_menu"),
                    ),
                ],
            ),
            "name_entry": Name_entry(
                screen,
                font,
                0,
                self.config,
                [
                    Button(
                        screen,
                        550,
                        650,
                        200,
                        50,
                        font,
                        "main_menu",
                        self.switch("main_menu"),
                    ),
                ],
            ),
        }

    def set_state(self, state: str) -> None:
        """
        Switch the active screen, reloading highscore data when
        entering the highscore screen

        Args:
            state: Name of the screen to show.
        """
        self.state = state
        if state == "highscores":
            self.screens["highscores"].load_data()

    def new_game(self) -> None:
        """
        Reset the gameplay screen and switch to it.
        """
        self.screens["playing"].player = None
        self.screens["playing"].level_index = 0
        self.screens["playing"].speed_bost = False
        self.screens["playing"].invinsible = False
        self.screens["playing"].frozen = False
        self.screens["playing"].reset()
        self.state = "playing"

    def quit(self) -> None:
        """Stop the main loop."""
        self.running = False

    def run(self) -> None:
        """
        Run the main loop until the game quits.

        Each frame: tick the clock, collect events, upfate the active screen,
        apply the returned state change, draw and flip the display,
        Calls pygame.quit() on exit.
        """
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            events = pygame.event.get()
            if any(event.type == pygame.QUIT for event in events):
                self.running = False
            next_state = self.screens[self.state].update(events, dt)
            if next_state:
                if next_state == "name_entry":
                    final_score = self.screens["playing"].player.score
                    self.screens["name_entry"].score = final_score
                elif next_state == "highscores":
                    self.screens["highscores"].load_data()
                self.state = next_state
            self.screens[self.state].draw()
            pygame.display.flip()
        pygame.quit()
