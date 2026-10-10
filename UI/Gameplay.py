from itertools import cycle

import pygame

from src.logic.entities import Ghost, GhostCorners, GhostStates, Player
from src.logic.maze import DOWN, LEFT, RIGHT, UP, load_maze
CELL_SIZE = 20
BACKGROUND = (28, 28, 31)
PLAYER_DELAY = 90
FRAME_PER_IMAGE = 8
GHOST_DELAY = 250
class Gameplay:
    KEYS = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT
        }
    def __init__(self, screen, font, pac_images, config, buttons, game_state) -> None:
        self.screen = screen
        self.font = font
        self.pac_images = pac_images
        self.config = config
        self.buttons = buttons
        self.level_index = 0
        self.game_state = game_state
        # self.player = None
        self.reset()
   
    def reset(self):
        level = self.config["level"][self.level_index]
        maze = load_maze(level["width"], level["height"],
                         self.config["seed"])
        self.maze_grid = maze["maze"]
        self.qued_move = None
        width, hieght = self.screen.get_size()
        # self.offset_x = (width - len(self.maze_grid[0]) * self.cell_size) // 2
        # self.offset_y = (hieght - len(self.maze_grid) * self.cell_size) // 2
        if getattr(self, "player", None) is None:
            self.player = Player(x=2, y=2, lives=self.config["lives"], direction=RIGHT, maze_grid=self.maze_grid)
        else:
            self.player.x = 2
            self.player.y = 2
            self.player.maze_grid = self.maze_grid
        self.ghost = Ghost(direction=RIGHT, maze_grid=self.maze_grid, corner=GhostCorners.BOTTOMRIGHT)
        self.ghost_last_move = 0.
        self.time_left = self.config["level_max_time"]
        self.cell_size = min(width // level["width"], (hieght - 150) // level["height"])
        self.offset_x = (width - len(self.maze_grid[0]) * self.cell_size) // 2
        self.offset_y = (hieght - len(self.maze_grid) * self.cell_size) // 2
        self.last_move = 0
        self.frame_counter = 0
        self.pac_animation = cycle(self.pac_images)
        self.current_image = next(self.pac_animation)
        self.excluded = {(0, 0), (maze["width"] - 1, 0),
                (0, maze["height"] - 1),
                (maze["width"] - 1, maze["height"] - 1)}
        self.pacgums = self.game_state.place_pacgums(maze["width"], 
                                       maze["height"],
                                       self.config["pacgum"],
                                       self.excluded)
    def update(self, events, dt):
        for event in events:
            for button in self.buttons:
                if button.handle_event(event):
                    return None
        self.time_left = max(self.time_left - dt, 0)
        if self.time_left == 0:
            return "game_over"
        if self.player.lives <= 0:
            return "game_over"
        elif self.ghost.x == self.player.x and self.ghost.y == self.player.y and self.ghost.state == GhostStates.SCARED:
            self.ghost.x, self.ghost.y = 0 , 0 
        elif self.ghost.x == self.player.x and self.ghost.y == self.player.y:
            self.player.lives -= 1
            self.player.x = 5 
            self.player.y = 5
            self.ghost.x = 4
            self.ghost.y = 4
            self.player.old_x = self.player.x
            self.player.old_y = self.player.y
        self.animate()
        self.eat_pacgum()
        self.eat_super_pacgum()
        self.cheat_mode()
        now = pygame.time.get_ticks()
        if now - self.ghost_last_move >= GHOST_DELAY:
            self.ghost.take_turn(self.player.x, self.player.y)
            self.ghost_last_move = now
        if now - self.last_move >= PLAYER_DELAY and self.move_player():
            self.last_move = now
        keys = pygame.key.get_pressed()
        for key, direction in self.KEYS.items():
            if keys[key]:
                self.qued_move = direction
                break
        return None
    def draw_pacgums(self):
        for x, y in self.pacgums:
            print(x, y)
            center = self.center_cell(x, y)
            pygame.draw.circle(self.screen, "white", center, 2)
    def draw_super_pacgums(self):
        for x, y in self.excluded:
            center = self.center_cell(x, y)
            pygame.draw.circle(self.screen, "white", center, 6)

    def eat_pacgum(self):
            if len(self.pacgums) <= 0:
                self.level_index += 1
                self.reset()
            if (self.player.x, self.player.y) in self.pacgums:
                self.pacgums.remove((self.player.x,self.player.y))
                self.player.score += self.config["points_per_pacgum"]
    def eat_super_pacgum(self):
        if (self.player.x, self.player.y) in self.excluded:
            self.ghost.state = GhostStates.SCARED
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
        return self.offset_x + x * self.cell_size, self.offset_y + y * self.cell_size
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
       
        
        # self.draw_pacgums()
        # self.death()
        for button in self.buttons:
            button.draw()
    def cheat_mode(self):
        key = pygame.key.get_pressed()
        if key == pygame.K_0:
            print("waaaa")
    def draw_maze(self):
         for y, n in enumerate(self.maze_grid):
             for x, cell in enumerate(n):
                left, top = self.origin_cell(x, y)
                right, bottom = left + self.cell_size, top + self.cell_size
                # screen_y = (y * CELL_SIZE) + (CELL_SIZE / 2)
                if cell & 1:
                    pygame.draw.line(self.screen, "white", (left, top), (right, top),1)
                if cell & 2:
                    pygame.draw.line(self.screen, "white", (right, top), (right, bottom),1)
                if cell & 4:
                    pygame.draw.line(self.screen, "white", (left, bottom), (right, bottom),1)
                if cell & 8:
                    pygame.draw.line(self.screen, "white", (left, top), (left, bottom),1)
    def draw_player(self):
        now = pygame.time.get_ticks()
        t = min((now - self.last_move) / PLAYER_DELAY, 1.0)
        old_center = self.center_cell(self.player.old_x, self.player.old_y)
        new_center = self.center_cell(self.player.x, self.player.y)
        lerp_x = old_center[0] + (new_center[0] - old_center[0]) * t
        lerp_y = old_center[1] + (new_center[1] - old_center[1]) * t
        # center = self.center_cell(lerp_x, lerp_y)
        self.screen.blit(self.current_image, self.current_image.get_rect(center=(lerp_x,lerp_y)))
    def draw_ghost(self):
        ghost = pygame.image.load("img/my_ghost.png").convert_alpha()
        center = self.center_cell(self.ghost.x, self.ghost.y)
        self.screen.blit(ghost, ghost.get_rect(center=center))
        # pygame.draw.circle(self.screen, "red", center, 6)
    
    def draw_hud(self):
        lines = [
            f"Lives: {self.player.lives}",
            f"scores: {self.player.score}",
            f"time_left: {self.time_left:.1f}",
            f"level: {self.level_index + 1}"
        ]
        for i, text in enumerate(lines):
            surface = self.font.render(text, True, (255,255,255))
            self.screen.blit(surface, (20, 30 + i * 60))
    # def full_reset(self):
    #     self.player = None
    #     self.level_index = 0
    #     self.reset()