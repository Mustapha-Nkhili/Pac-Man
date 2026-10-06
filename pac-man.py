import sys

import pygame
from src.logic.maze import DOWN, LEFT, RIGHT, UP
from src.config_loader import load_config
from src.logic.maze import load_maze
from src.logic.entities import Ghost, GhostStates, GhostCorners, Player
from src.logic.game_state import GameState
from UI.menu import Button, Gameplay

GAME_STATE = "main_menu"


def Exit():
    sys.exit()


def instructions():
    global GAME_STATE
    GAME_STATE = "instructions"


def Pause():
    global GAME_STATE
    GAME_STATE = "pause"


def menu():
    global GAME_STATE
    GAME_STATE = "main_menu"


def Start():
    global GAME_STATE
    GAME_STATE = "playing"


def GAME_Over():
    global GAME_STATE
    GAME_STATE = "game_over"


def main():
    global GAME_STATE
    if len(sys.argv) != 2:
        print("Error: Invalid number of arguments.", file=sys.stderr)
        print(f"Usage: python {sys.argv[0]} config.json", file=sys.stderr)
        sys.exit(1)

    config = load_config(sys.argv[1])
    maze = load_maze(
        config["level"][0]["width"], config["level"][0]["height"], config["seed"]
    )
    print(maze["maze"])

    pygame.init()
    SCREEN = pygame.display.set_mode((1280, 720))
    get_font = pygame.font.Font("img/pixel-game/Pixel Game.otf", 48)
    main_menu = []
    gameplay = []
    pause_menu = []
    instruction = []
    game_over = []
    pacman_logo = pygame.image.load(
        "./img/Pac-Man-Logo-2-2736475491.webp"
    ).convert_alpha()
    pacman_back = pygame.image.load("img/pause_back.jpg").convert_alpha()
    scaled_logo = pygame.transform.scale(pacman_logo, (350, 90))
    scaled_back = pygame.transform.scale(pacman_back, (1280, 720))
    GAME_STATE = "main_menu"
    pac_open = pygame.image.load("img/pacmanopen.png").convert_alpha()
    pac_close = pygame.image.load("img/pacmanclosed.png").convert_alpha()
    pac_mid = pygame.image.load("img/pacmanmid.png").convert_alpha()
    pac_images = [
        pygame.transform.scale(pac_open, (14, 14)),
        pygame.transform.scale(pac_close, (14, 14)),
        pygame.transform.scale(pac_mid, (14, 14)),
    ]
    pause_img = pygame.image.load("img/pause.png").convert_alpha()
    s_pause_img = pygame.transform.scale(pause_img, (450, 100))
    ause_back = pygame.image.load("img/pause_back2.jpg")
    pause_back = pygame.transform.scale(ause_back, (1280, 720))

    def Highscores():
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            SCREEN.fill("yellow")
            pygame.display.flip()
            clock.tick(60)

    pygame.display.set_caption("Main Menu")
    clock = pygame.time.Clock()
    running = True

    Button(SCREEN, 100 + 50, 450, 300, 100, get_font, "Start Game", main_menu, Start)
    Button(
        SCREEN,
        225 + 50,
        450,
        300,
        100,
        get_font,
        "View Highscores",
        main_menu,
        Highscores,
    )
    Button(
        SCREEN,
        350 + 50,
        450,
        300,
        100,
        get_font,
        "Instructions",
        main_menu,
        instructions,
    )
    Button(SCREEN, 475 + 50, 450, 300, 100, get_font, "EXIT", main_menu, Exit)
    Button(
        SCREEN, 720 / 2, 1280 / 2 + 60, 150, 50, get_font, "Resume", pause_menu, Start
    )
    Button(
        SCREEN,
        720 / 2 + 100,
        1280 / 2 - 100,
        200,
        50,
        get_font,
        "Quit Game",
        pause_menu,
        Exit,
    )
    Button(
        SCREEN,
        720 / 2,
        1280 / 2 - 250,
        200,
        50,
        get_font,
        "main menu",
        pause_menu,
        menu,
    )
    Button(SCREEN, 650, 550, 200, 50, get_font, "main menu", instruction, menu)
    Button(SCREEN, 15, 1280 / 2, 100, 50, get_font, "Pause", gameplay, Pause)
    Button(SCREEN, 380, 340, 230, 50, get_font, "Start again", game_over, Start)
    Button(SCREEN, 380, 650, 230, 50, get_font, "main menu", game_over, menu)

    time = config["level_max_time"]
    player = Player(
        x=0, y=0, lives=config["lives"], direction=2, maze_grid=maze["maze"]
    )
    ghost = Ghost(
        direction=2, maze_grid=maze["maze"], corner=GhostCorners.BOTTOMLEFT
    )
    maze_grid = maze["maze"]
    cell_size = 20
    total_hight = len(maze_grid) * cell_size
    total_width = len(maze_grid[0]) * cell_size
    delta_y = 720 - total_hight
    delta_x = 1280 - total_width
    movment = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }
    gameplay_UI = Gameplay(
        player,
        ghost,
        maze_grid,
        cell_size,
        delta_x,
        delta_y,
        get_font,
        pac_images,
        time,
        SCREEN,
        movment,
    )
    game_state = GameState()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        SCREEN.blit(scaled_back, (0, 0))
        if GAME_STATE == "main_menu":
            SCREEN.blit(scaled_logo, (420, 20))
            for object in main_menu:
                object.process()
        if GAME_STATE == "playing":
            gameplay_UI.update()
            gameplay_UI.draw()
            game_state.check_collisions(player, [ghost], config["points_per_ghost"])
            for object in gameplay:
                object.process()
            if player.lives <= 0:
                GAME_Over()
        if GAME_STATE == "pause":
            SCREEN.blit(pause_back, (0, 0))
            SCREEN.blit(s_pause_img, (400, 190))
            for object in pause_menu:
                object.process()
        if GAME_STATE == "instructions":
            SCREEN.fill("white")
            text_surf = get_font.render("Instrictions", True, (20, 20, 20))
            SCREEN.blit(text_surf, (720 / 2 - 48, 30))
            for object in instruction:
                object.process()
        if GAME_STATE == "game_over":
            go = get_font.render("GAME OVER", True, "White")
            SCREEN.fill("black")
            SCREEN.blit(go, (520, 300))
            for object in game_over:
                object.process()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
