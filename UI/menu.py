import pygame
from itertools import cycle

class Button:
        def __init__(self, screen, x, y, width, height, font, button_text, objects, onclickFunction=None, onePress=False) -> None:
            self.x = x
            self.y = y
            self.screen = screen
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
            self.screen.blit(self.buttonSurface, self.rect)

class Gameplay:
    def __init__(self, player, ghost, maze_grid, cell_size, delta_x, delta_y, font, pac_images, level_time, screen, movement) -> None:
        self.player = player
        self.ghost = ghost
        self.maze_grid = maze_grid
        self.cell_size = cell_size
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.font = font
        self.pac_images = pac_images
        self.level_time = level_time
        self.screen = screen
        self.movement = movement
        self.clock = pygame.time.Clock()
        self.pac_animation = cycle(self.pac_images)
        self.current_image = next(self.pac_animation)
        self.frame_per_image = 8
        self.last_move = 0
        self.frame_counter = 0
        self.ghost_last_move = 0
        self.delay = 90
        self.ghost_delay = 250
        self.dt = self.clock.tick(60) / 1000
    def update(self):
        
        self.level_time -= self.dt
        time = max(self.level_time, 0)
        if time == 0:
            return "game_over"
        self.frame_counter += 1
        if self.frame_counter >= self.frame_per_image:
            self.current_image = next(self.pac_animation)
            self.frame_counter = 0
        curre_time = pygame.time.get_ticks()
        self.screen.fill((51, 55, 150))
        key_input = pygame.key.get_pressed()
        pac_screen_x = (self.player.x * self.cell_size) + (self.delta_x / 2)
        pac_screen_y = (self.player.y * self.cell_size) + (self.delta_y / 2)
        ghost_screen_x = (self.ghost.x * self.cell_size) + (self.delta_x / 2) + self.cell_size / 2
        ghost_screen_y = (self.ghost.y * self.cell_size) + (self.delta_y / 2) + self.cell_size / 2
        pygame.draw.circle(self.screen, "red",(ghost_screen_x,ghost_screen_y), 6)
        if curre_time - self.ghost_last_move >= self.ghost_delay:
            self.ghost.take_turn(self.player.x, self.player.y)
            self.ghost_last_move = curre_time
        if curre_time - self.last_move >= self.delay:
            moved = False
            for k, v in self.movement.items():
                if key_input[k]:
                    before = (self.player.x, self.player.y)
                    self.player.move(v)
                    if (self.player.x, self.player.y) != before:
                        moved = True
                        self.last_move = curre_time
                    break
            if not moved:
                before = (self.player.x, self.player.y)
                self.player.move(self.player.direction)
                if (self.player.x, self.player.y) != before:
                    self.last_move = curre_time
            self.last_move = curre_time
        self.screen.blit(self.current_image,(int(pac_screen_x), int(pac_screen_y)))
        # SCREEN.blit(current_image,(int(pac_screen_x), int(pac_screen_y)))
        lives_surf = self.font.render(f"lives: {self.player.lives}", True, (20,20,20))
        time_surf = self.font.render(f"time_left: {time:.1f}", True, (20,20,20))
        level_surf = self.font.render("level", True, (20,20,20))
        self.screen.blit(lives_surf, (20, 30))
        self.screen.blit(time_surf, (20, 90))
        self.screen.blit(level_surf, (20, 150))
    def draw(self):
         for y, n in enumerate(self.maze_grid):
             for x, n in enumerate(n):
                screen_x = (x * self.cell_size) + (self.delta_x / 2)
                screen_y = (y * self.cell_size) + (self.delta_y / 2)
                if n & 1:
                    pygame.draw.line(self.screen, "white", (screen_x,screen_y), (screen_x + self.cell_size, screen_y),1)
                if n & 2:
                    pygame.draw.line(self.screen, "white", (screen_x + self.cell_size,screen_y), (screen_x + self.cell_size, screen_y + self.cell_size),1)
                if n & 4:
                    pygame.draw.line(self.screen, "white", (screen_x,screen_y + self.cell_size), (screen_x + self.cell_size, screen_y + self.cell_size),1)
                if n & 8:
                    pygame.draw.line(self.screen, "white", (screen_x,screen_y), (screen_x, screen_y + self.cell_size),1)
                # self.screen.fill((51, 55, 150))