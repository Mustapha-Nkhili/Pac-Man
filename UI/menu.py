import pygame


class Menu:
    def __init__(self, screen, font, background, button, images=(), title=None,title_pos = (0,0), title_color="white") -> None:
        self.screen = screen
        self.background = background
        self.button = button
        self.images = images
        self.title = font.render(title, True, title_color) if title else None
        self.title_pos = title_pos
    
    def update(self, events, dt):
        for event in events:
            for button in self.button:
                if button.handle_event(event):
                    return
        return
    
    def draw(self):
        if isinstance(self.background, pygame.Surface):
            self.screen.blit(self.background, (0,0))
        else:
            self.screen.fill(self.background)
        for image, pos in self.images:
            self.screen.blit(image, pos)
        if self.title:
            self.screen.blit(self.title, self.title_pos)
        for buttons in self.button:
            buttons.draw()