import sys
from itertools import cycle

import pygame

from src.config_loader import load_config
from src.logic.maze import load_maze

GAME_STATE = 'main_menu'
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
    maze = load_maze(config["level"][0]["width"],
                     config["level"][0]["height"],
                     config["seed"])
    print(maze["maze"])

    pygame.init()
    SCREEN = pygame.display.set_mode((1280, 720))
    get_font = pygame.font.Font("img/pixel-game/Pixel Game.otf", 48)
    main_menu = []
    gameplay = []
    pause_menu = []
    instruction = []
    game_over = []
    pacman_logo = pygame.image.load("/home/maissam/Pictures/pc/Pac-Man.svg").convert_alpha()
    pacman_back = pygame.image.load("img/pause_back.jpg").convert_alpha()
    scaled_logo = pygame.transform.scale(pacman_logo, (350, 90))
    scaled_back = pygame.transform.scale(pacman_back, (1280, 720))
    GAME_STATE = 'main_menu'
    maze_gen = maze["maze"]
    pac_open = pygame.image.load("img/pacmanopen.png").convert_alpha()
    pac_close = pygame.image.load("img/pacmanclosed.png").convert_alpha()
    pac_mid = pygame.image.load("img/pacmanmid.png").convert_alpha()
    pac_images = [pygame.transform.scale(pac_open, (14, 14)),
    pygame.transform.scale(pac_close, (14, 14)),
    pygame.transform.scale(pac_mid, (14, 14))]
    top_wall = pygame.image.load("img/Wall.png").convert_alpha()
    right_wall = pygame.image.load("img/Wall.png").convert_alpha()
    pause_img = pygame.image.load("img/pause.png").convert_alpha()
    s_pause_img = pygame.transform.scale(pause_img, (450, 100))
    # s_pause_img = pygame.transform.scale(top_wall, (20, 10))
    s_top_wall = pygame.transform.scale(top_wall, (20, 10))
    s_right_wall = pygame.transform.scale(right_wall, (10, 20))
    pac_animation = cycle(pac_images)
    current_image = next(pac_animation)
    frame_counter = 0
    frame_per_image = 8
    ause_back = pygame.image.load("img/pause_back2.jpg")
    pause_back = pygame.transform.scale(ause_back, (1280, 720))
    class Button:
        def __init__(self, x, y, width, height, font, button_text, objects, onclickFunction=None, onePress=False) -> None:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.bytton_text = button_text
            self.onclickFunction = onclickFunction
            self.onePress = onePress
            self.alreadyPressed = False
            self.fill_colors = {
                'normal': (51, 55, 150),
                'hover': "#18285C",
                'pressed':"#919191"
            }
            self.font = font
            self.buttonSurface = pygame.Surface((self.width, self.height))
            self.rect = pygame.Rect(self.y, self.x, self.width, self.height)
            self.buttomSurf = font.render(button_text, True, "white")
            objects.append(self)
        def process(self):
            mousePos = pygame.mouse.get_pos()
            self.buttonSurface.fill(self.fill_colors["normal"])
            if self.rect.collidepoint(mousePos):
                self.buttonSurface.fill(self.fill_colors["hover"])
                if pygame.mouse.get_pressed(num_buttons=3)[0]:
                    self.buttonSurface.fill(self.fill_colors["pressed"])
                    if self.onePress:
                        self.onclickFunction()
                    elif not self.alreadyPressed:
                        self.onclickFunction()
                        self.alreadyPressed = True
                else:
                    self.alreadyPressed = False
            self.buttonSurface.blit(self.buttomSurf, [
                self.rect.width/2 - self.buttomSurf.get_rect().width/2,
                self.rect.height/2 - self.buttomSurf.get_rect().height/2
            ])
            SCREEN.blit(self.buttonSurface, self.rect)


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

    Button(100 + 50, 450, 300, 100, get_font, "Start Game", main_menu, Start)
    Button(225 + 50, 450, 300, 100, get_font, "View Highscores", main_menu, Highscores)
    Button(350 + 50, 450, 300, 100, get_font, "Instructions", main_menu, instructions)
    Button(475 + 50, 450, 300, 100, get_font, "EXIT", main_menu, Exit)
    Button(720/2, 1280/2 + 60, 150, 50, get_font, "Resume", pause_menu, Start)
    Button(720/2 + 100, 1280/2 - 100, 200, 50, get_font, "Quit Game", pause_menu, Exit)
    Button(720/2, 1280/2 - 250, 200, 50, get_font, "main menu", pause_menu, menu)
    Button(650, 550, 200, 50, get_font, "main menu", instruction, menu)
    Button(15, 1280/2, 100, 50, get_font, "Pause", gameplay, Pause)
    Button(380,340 , 230, 50, get_font, "Start again", game_over, Start)
    Button(380, 650, 230, 50, get_font, "main menu", game_over, menu)


    pac_col = 0
    pac_row = 0
    speed = 1
    last_move = 0
    delay = 90
    lives = 3
    time = config["level_max_time"]
    level = config["lives"]
    last_col = 0
    last_row = 0
    last_dir = 0

    def can_move(maze_grid, row, col, direction):
        return (not maze_grid[row][col] & direction)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # SCREEN.fill("black")
        SCREEN.blit(scaled_back, (0,0))
        if GAME_STATE == "main_menu":
            SCREEN.blit(scaled_logo, (420, 20))
            for object in main_menu:
                object.process()
        if GAME_STATE == "playing":
            dt = clock.tick(60) / 1000
            time -= dt
            time = max(time, 0)
            if time == 0:
                GAME_STATE = "game_over"
            frame_counter += 1
            if frame_counter >= frame_per_image:
                current_image = next(pac_animation)
                frame_counter = 0
            curre_time = pygame.time.get_ticks()
            SCREEN.fill((51, 55, 150))
            maze_grid = maze["maze"]
            cell_size = 20
            total_hight = len(maze_grid) * cell_size
            total_width = len(maze_grid[0]) * cell_size
            delta_y = 720 - total_hight
            delta_x = 1280 - total_width 
            for y, n in enumerate(maze_grid):
                for x, n in enumerate(n):
                    screen_x = (x * cell_size) + (delta_x / 2)
                    screen_y = (y * cell_size) + (delta_y / 2)
                    if n & 1:
                        # SCREEN.blit(s_top_wall, (screen_x,screen_y))
                        pygame.draw.line(SCREEN, "white", (screen_x,screen_y), (screen_x + cell_size, screen_y),1)
                        
                    if n & 2:
                        pygame.draw.line(SCREEN, "white", (screen_x + cell_size,screen_y), (screen_x + cell_size, screen_y + cell_size),1)
                    if n & 4:
                        pygame.draw.line(SCREEN, "white", (screen_x,screen_y + cell_size), (screen_x + cell_size, screen_y + cell_size),1)
                    if n & 8:
                        # SCREEN.blit(s_right_wall, (screen_x,screen_y))
                        pygame.draw.line(SCREEN, "white", (screen_x,screen_y), (screen_x, screen_y + cell_size),1)
            
            key_input = pygame.key.get_pressed()
            pac_screen_x = (pac_col * cell_size) + (delta_x / 2)
            pac_screen_y = (pac_row * cell_size) + (delta_y / 2)
            movment = {pygame.K_UP: (1, -1, 0),
            pygame.K_DOWN: (4, 1, 0),
            pygame.K_LEFT: (8, 0, -1),
            pygame.K_RIGHT: (2, 0, 1)}
        
            for k, v in movment.items():
                direction, dx, dy, = v
                if key_input[k] and can_move(maze_grid, pac_row, pac_col, direction) and curre_time - last_move >= delay:
                    SCREEN.blit(current_image,(int(pac_screen_x), int(pac_screen_y)))
                    pac_col += dy
                    pac_row += dx
                    last_col = dy
                    last_row = dx
                    last_dir = direction
                    last_move = curre_time
                    break
            
            if can_move(maze_grid, pac_row, pac_col, last_dir) and curre_time - last_move >= delay:
                pac_col += last_col
                pac_row += last_row
                last_move = curre_time
                SCREEN.blit(current_image,(int(pac_screen_x), int(pac_screen_y)))
            SCREEN.blit(current_image,(int(pac_screen_x), int(pac_screen_y)))
            lives_surf = get_font.render(f"lives: {lives}", True, (20,20,20))
            time_surf = get_font.render(f"time_left: {time:.1f}", True, (20,20,20))
            level_surf = get_font.render("level", True, (20,20,20))

            SCREEN.blit(lives_surf, (20, 30))
            SCREEN.blit(time_surf, (20, 90))
            SCREEN.blit(level_surf, (20, 150))
            for object in gameplay:
                object.process()
        if GAME_STATE == "pause":
            SCREEN.blit(pause_back, (0, 0))
            SCREEN.blit(s_pause_img, (400, 190))
            for object in pause_menu:
                    object.process()
        if GAME_STATE == "instructions":
            SCREEN.fill("white")
            text_surf = get_font.render("Instrictions", True, (20,20,20))
            SCREEN.blit(text_surf, (720/2 - 48, 30))
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
