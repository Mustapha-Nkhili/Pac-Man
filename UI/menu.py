import pygame


class Menu:
    """
    Static screen made fo a background,
    optional images, an optional title and set of buttons
    """

    def __init__(
        self,
        screen,
        font,
        background,
        button,
        images=(),
        title=None,
        title_pos=(0, 0),
        title_color="white",
    ) -> None:
        """
        Create a menu screen

        Args:
            screen: surface to draw on.
            font: Font used to render the title.
            background: A Surface to blit, or a color to fill with.
            button: list of Button objects.
            images = images to draw over the background.
            title_pos: top_left position of the title.
            title_color: color of the title text.
        """
        self.screen = screen
        self.background = background
        self.button = button
        self.images = images
        self.title = font.render(title, True, title_color) if title else None
        self.title_pos = title_pos

    def update(self, events, dt):
        """
        Forward events to the buttons, stopping at the first ine that handles
        and event.
        Args:
            events: Pygame events collected this frame.
            dt: Seconds elapsed since the previous frame

        Returns:
            Alaways None, button callbacks change the state themeselves.
        """
        for event in events:
            for button in self.button:
                if button.handle_event(event):
                    return
        return

    def draw(self):
        """Draw the background, images, tile, and buttons"""
        if isinstance(self.background, pygame.Surface):
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.background)
        for image, pos in self.images:
            self.screen.blit(image, pos)
        if self.title:
            self.screen.blit(self.title, self.title_pos)
        for buttons in self.button:
            buttons.draw()
