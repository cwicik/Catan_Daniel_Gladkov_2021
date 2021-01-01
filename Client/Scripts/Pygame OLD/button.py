import pygame
pygame.init()

base_color = (180, 30, 45)
text_color = (255, 200, 10)
hovered_base_color = (190, 40, 55)
font = pygame.font.SysFont('Comic Sans MS', 40)


class Button:
    """
        A class that represents a button
        Attributes
        ----------
        :var screen: The screen the button is drawn on
        :type screen: pygame.display
        :var text: The text the button displays
        :type text: string
        :var x: The X position of the button
        :type x: int
        :var y: The Y position of the button
        :type y: int
        :var width: The width of the button
        :type width: int
        :var height: The height of the button
        :type height: int
        :var action: The actions the button does when pressed
        :type action: function
        :var active: Is the button active?
        :type active: boolean
        Methods
        -------
        draw_self()
            draws the object
        hovered_over()
            checks if the mouse is on the button, if yes return True change its color, else return False
        pressed()
            checks if button is pressed, if yes activate its action
        activate()
            makes the button active
        deactivate()
            makes the button not active
    """

    def __init__(self, screen, x, y, text, action):
        self.screen = screen
        self.text = font.render(text, True, text_color)
        self.x = x
        self.y = y
        self.width = 12 + self.text.get_width()
        self.height = 65
        self.action = action

    def draw_self(self, b_color=base_color):
        pygame.draw.rect(self.screen, b_color, (self.x, self.y, self.width, self.height))
        self.screen.blit(self.text, (self.x + 6, self.y))

    def hovered_over(self):
        mouse = pygame.mouse.get_pos()
        if (self.x + self.width > mouse[0] > self.x) and (self.y + self.height > mouse[1] > self.y):
            self.draw_self(hovered_base_color)
            return True
        else:
            self.draw_self()
            return False

    def pressed(self):
        if self.hovered_over():
            self.action()
