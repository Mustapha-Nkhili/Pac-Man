from itertools import cycle

import pygame

from src.logic.entities import Ghost, GhostCorners, GhostStates, Player
from src.logic.maze import DOWN, LEFT, RIGHT, UP, load_maze
CELL_SIZE = 40
BACKGROUND = (51, 55, 150)
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
        self.reset()
    
    def reset(self):
        level = self.config["level"][self.level_index]
        maze = load_maze(level["width"], level["height"],
                         self.config["seed"])
        self.maze_grid = maze["maze"]
        width, hieght = self.screen.get_size()
        self.offset_x = (width - len(self.maze_grid[0]) * CELL_SIZE) // 2
        self.offset_y = (hieght - len(self.maze_grid) * CELL_SIZE) // 2
        self.player = Player(x=2, y=2, lives=self.config["lives"], direction=RIGHT, maze_grid=self.maze_grid)
        self.ghost = Ghost(direction=RIGHT, maze_grid=self.maze_grid, corner=GhostCorners.BOTTOMRIGHT)
        self.ghost_last_move = 0.
        self.time_left = self.config["level_max_time"]
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
        elif self.ghost.x == self.player.x and self.ghost.y == self.player.y:
            self.player.lives -= 1
            self.player.x = 5 
            self.player.y = 5
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
        return None
    def draw_pacgums(self):
        for x, y in self.pacgums:
            print(x, y)
            center = self.center_cell(x, y)
            pygame.draw.circle(self.screen, "red", center, 4)
            print(self.excluded)
    def draw_super_pacgums(self):
        for x, y in self.excluded:
            center = self.center_cell(x, y)
            pygame.draw.circle(self.screen, "black", center, 10)

    def eat_pacgum(self):
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
        keys = pygame.key.get_pressed()
        before = (self.player.x, self.player.y)
        for key, direction in self.KEYS.items():
            if keys[key]:
                self.player.move(direction)
                break
        if (self.player.x, self.player.y) == before:
            self.player.move(self.player.direction)
        return (self.player.x, self.player.y) != before
    def origin_cell(self, x, y):
        return self.offset_x + x * CELL_SIZE, self.offset_y + y * CELL_SIZE
    def center_cell(self, x, y):
        left, top = self.origin_cell(x, y)
        return left + CELL_SIZE // 2, top + CELL_SIZE // 2
    def draw(self):
        self.screen.fill(BACKGROUND)
        self.draw_maze()
        self.draw_ghost()
        self.draw_player()
        self.draw_hud()
        self.draw_pacgums()
        self.draw_super_pacgums()
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
                right, bottom = left + CELL_SIZE, top + CELL_SIZE
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
        center = self.center_cell(self.player.x, self.player.y)
        self.screen.blit(self.current_image, self.current_image.get_rect(center=center))
    def draw_ghost(self):
        center = self.center_cell(self.ghost.x, self.ghost.y)
        pygame.draw.circle(self.screen, "red", center, 6)

    def draw_hud(self):
        lines = [
            f"Lives: {self.player.lives}",
            f"scores: {self.player.score}",
            f"time_left: {self.time_left:.1f}",
            f"level: {self.level_index + 1}"
        ]
        for i, text in enumerate(lines):
            surface = self.font.render(text, True, (20,20,20))
            self.screen.blit(surface, (20, 30 + i * 60))
        