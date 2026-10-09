from functools import partial

import pygame

from UI.menu import Menu

from UI.Gameplay import Gameplay
from src.logic.entities import Ghost, GhostCorners, GhostStates, Player
from src.logic.game_state import GameState
from src.logic.maze import load_maze

WIDTH, HEIGHT = 1280, 720
FONT_PATH = "img/pixel-game/Pixel Game.otf"
FPS = 60

class Button:
    COLORS = {
        "normal": (51, 55, 150),
        "hover": "#18285C",
        "pressed": "#919191"
    }

    def __init__(self, screen, x, y, width, height, font, text, on_click) -> None:
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.on_click = on_click
        self.label = font.render(text, True, "white")
    
    def handle_event(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)):
            self.on_click()
            return True
        return False

    def draw(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            state = "pressed" if pygame.mouse.get_pressed()[0] else "hover"
        else:
            state = "normal"
        pygame.draw.rect(self.screen, self.COLORS[state], self.rect)
        self.screen.blit(self.label, self.label.get_rect(center=self.rect.center))

class Game:
    def __init__(self, game_state: GameState, config) -> None:
        self.config = config
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac_Man")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, 48)
        self.running = True
        self.state = "main_menu"
        self.game_state = game_state
        self.load_assets()
        self.load_screens()
    @staticmethod
    def images(path, size=None):
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size) if size else image

    def load_assets(self):
        window = (WIDTH, HEIGHT)
        self.logo = self.images("./img/Pac-Man-Logo-2-2736475491.webp", (350, 90))
        self.menu_bg = self.images("img/pause_back.jpg", window)
        self.pause_bg = self.images("img/pause.png", window)
        self.pause_bg2 = self.images("img/pause_back2.jpg", window)
        self.instructions = self.images("img/Instructions.png", window)
        self.pac_images = [self.images(f"img/{name}", (14, 14))
                           for name in 
                           ("pacmanopen.png",
                            "pacmanclosed.png", 
                            "pacmanmid.png")]

    def load_screens(self):
        screen, font = self.screen, self.font
        switch = lambda state: partial(self.set_state, state)
        self.screens = {
            "main_menu": Menu(screen, font, self.menu_bg, [
                Button(screen, 450, 150, 300, 100, font, "Start Game", self.new_game),
                Button(screen, 450, 275, 300, 100, font, "Highscores", switch("highscores")),
                Button(screen, 450, 400, 300, 100, font, "Instructions", switch("instructions")),
                Button(screen, 450, 525, 300, 100, font, "QUIT GAME", self.quit),
            ], images=[(self.logo, (420, 20))]),
            "playing": Gameplay(screen, font, self.pac_images, self.config,
                                [Button(screen, 640, 15, 100, 50, font, "Pause", switch("pause")),
                                ], game_state=self.game_state),
            "pause": Menu(screen, font, self.pause_bg2, [
                Button(screen,700, 360, 150, 50, font, "Resume", switch("playing")),
                Button(screen, 540, 460, 200, 50, font, "Quit Game", self.quit),
                Button(screen, 390, 360, 200, 50, font, "main_menu", switch("main_menu")),
            ], images=[(self.pause_bg, (400, 190))]),
            "instructions": Menu(screen, font, self.instructions, [
                Button(screen, 550, 650, 200, 50, font, "main_menu", switch("main_menu")),
            ]),
            "game_over": Menu(screen, font, "black", [
                Button(screen, 340, 380, 230, 50, font, "Play Again", self.new_game),
                Button(screen, 650, 380, 230, 50, font, "main_menu", switch("main_menu")),
            ], title="Game Over", title_pos=(520, 300)),
            "highscores": Menu(screen, font, "black", [
                Button(screen, 550, 650, 200, 50, font, "main_menu", switch("main_menu")),
            ])

        }
    def set_state(self, state):
        self.state = state
    def new_game(self):
        self.screens["playing"].reset()
        self.state = "playing"
    def quit(self):
        self.running = False
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            events = pygame.event.get()
            if any(event.type == pygame.QUIT for event in events):
                self.running = False
            next_state = self.screens[self.state].update(events, dt)
            if next_state:
                self.state = next_state
            self.screens[self.state].draw()
            pygame.display.flip()    
        pygame.quit()