import sys

import pygame

from mazegenerator import MazeGenerator

pygame.init()
SCREEN = pygame.display.set_mode((1280, 720))
get_font = pygame.font.SysFont("Consolas", 32)
main_menu = []
gameplay = []
pause_menu = []
instruction = []
GAME_STATE = 'main_menu'
maze_gen = MazeGenerator(size=(30,35), entry_cell=(0,0), exit_cell=(0,0), perfect=True, seed=0)
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
            'normal': "#E6DEB4",
            'hover': "#E1E1E1",
            'pressed':"#919191"
        }
        self.font = font
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(self.y, self.x, self.width, self.height)
        self.buttomSurf = font.render(button_text, True, (20,20,20))
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

Button(100, 75, 300, 100, get_font, "Start Game", main_menu, Start)
Button(225, 75, 300, 100, get_font, "View Highscores", main_menu, Highscores)
Button(350, 75, 300, 100, get_font, "Instructions", main_menu, instructions)
Button(475, 75, 300, 100, get_font, "EXIT", main_menu, Exit)
Button(720/2, 1280/2, 150, 50, get_font, "Resume", pause_menu, Start)
Button(720/2, 1280/2 - 250, 200, 50, get_font, "main menu", pause_menu, menu)
Button(650, 550, 200, 50, get_font, "main menu", instruction, menu)
Button(15, 1280/2, 100, 50, get_font, "Pause", gameplay, Pause)
pac_col = 0
pac_row = 0
speed = 1
last_move = 0
delay = 120
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    SCREEN.fill("black")
    if GAME_STATE == "main_menu":
        
        for object in main_menu:
            object.process()
    if GAME_STATE == "playing":
        curre_time = pygame.time.get_ticks()
        SCREEN.fill((51, 55, 150))
        maze_grid = maze_gen.maze
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
                    pygame.draw.line(SCREEN, "white", (screen_x,screen_y), (screen_x + cell_size, screen_y),1)
                if n & 2:
                    pygame.draw.line(SCREEN, "white", (screen_x + cell_size,screen_y), (screen_x + cell_size, screen_y + cell_size),1)
                if n & 4:
                    pygame.draw.line(SCREEN, "white", (screen_x,screen_y + cell_size), (screen_x + cell_size, screen_y + cell_size),1)
                if n & 8:
                    pygame.draw.line(SCREEN, "white", (screen_x,screen_y), (screen_x, screen_y + cell_size),1)
        
        key_input = pygame.key.get_pressed()
        pac_screen_x = (pac_col * cell_size) + (delta_x / 2) + cell_size / 2
        pac_screen_y = (pac_row * cell_size) + (delta_y / 2) + cell_size / 2
        if key_input[pygame.K_RIGHT] and not maze_grid[pac_row][pac_col] & 2 and curre_time - last_move >= delay:
                pygame.draw.circle(SCREEN, "yellow", (int(pac_screen_x), int(pac_screen_y)), 10, 20)
                pac_col += 1
                last_move = curre_time
        if key_input[pygame.K_DOWN] and not maze_grid[pac_row][pac_col] & 4 and curre_time - last_move >= delay:
            pygame.draw.circle(SCREEN, "yellow", (int(pac_screen_x), int(pac_screen_y)), 10, 20)
            pac_row += 1
            last_move = curre_time
        if key_input[pygame.K_LEFT] and not maze_grid[pac_row][pac_col] & 8 and curre_time - last_move >= delay:
            pygame.draw.circle(SCREEN, "yellow", (int(pac_screen_x), int(pac_screen_y)), 10, 20)
            pac_col -= 1
            last_move = curre_time
        if key_input[pygame.K_UP] and not maze_grid[pac_row][pac_col] & 1 and curre_time - last_move >= delay:
            pygame.draw.circle(SCREEN, "yellow", (int(pac_screen_x), int(pac_screen_y)), 10, 20)
            pac_row -= 1
            last_move = curre_time
        pygame.draw.circle(SCREEN, "yellow", (int(pac_screen_x), int(pac_screen_y)), 10, 20)
        for object in gameplay:
            object.process()
    if GAME_STATE == "pause":
        SCREEN.fill("black")
        for object in pause_menu:
                object.process()
    if GAME_STATE == "instructions":
        SCREEN.fill("white")
        text_surf = get_font.render("Instrictions", True, (20,20,20))
        SCREEN.blit(text_surf, (550 - 40, 30))
        for object in instruction:
            object.process()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()