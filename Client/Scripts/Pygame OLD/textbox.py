import pygame
import datetime
pygame.init()

text_color = (255, 255, 255)
GRAY = (128, 128, 128)
font = pygame.font.SysFont('Comic Sans MS', 40)
alphabet = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z', '.', '?', "'", '\\')
symbols = {'1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',}


class TextBox:
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

    def __init__(self, screen, x, y, action=None, size=400, limit=30, default_text='Type Here...', hidden=False):
        self.screen = screen
        self.text = ''
        self.x = x
        self.y = y
        self.width = size
        self.height = 55
        self.limit = limit
        self.default_text = default_text
        self.editable = False
        self.blinking = True
        self.end_time = datetime.datetime.now()
        self.action = action
        self.hidden = hidden

    def draw_self(self):
        text_to_render = self.text
        pygame.draw.rect(self.screen, GRAY, (self.x, self.y, self.width, self.height), 2)
        if len(self.text) == 0:
            self.screen.blit(font.render(self.default_text, True, GRAY), (self.x + 6, self.y - 4))
        else:
            while font.render(text_to_render + '|', True, text_color).get_width() >= self.width:
                text_to_render = text_to_render[1:]
            if self.hidden:
                text_to_render = len(text_to_render) * '*'
            if datetime.datetime.now() <= self.end_time - datetime.timedelta(seconds=0.5) and self.editable:
                self.screen.blit(font.render(text_to_render + '|', True, text_color), (self.x + 6, self.y - 4))
            elif datetime.datetime.now() <= self.end_time and self.editable:
                self.screen.blit(font.render(text_to_render, True, text_color), (self.x + 6, self.y - 4))
            else:
                self.screen.blit(font.render(text_to_render, True, text_color), (self.x + 6, self.y - 4))
                self.end_time = datetime.datetime.now() + datetime.timedelta(seconds=1)

    def hovered_over(self):
        mouse = pygame.mouse.get_pos()
        if (self.x + self.width > mouse[0] > self.x) and (self.y + self.height > mouse[1] > self.y):
            return True
        else:
            return False

    def pressed(self):
        if self.hovered_over():
            self.editable = True

    def update(self, letter, capitalize):
        if self.editable:
            self.end_time = datetime.datetime.now() + datetime.timedelta(seconds=1)
            if pygame.key.name(letter) == 'return' and self.action is not None:
                self.action(self.text)
            elif pygame.key.name(letter) == 'backspace':
                self.text = self.text[:-1]
            elif self.limit > len(self.text):
                if pygame.key.name(letter) == 'space':
                    self.text += ' '
                else:
                    letter = pygame.key.name(letter)
                    if letter in alphabet or letter.isdigit():
                        if capitalize:
                            if letter.isdigit():
                                letter = symbols[letter]
                            letter = letter.capitalize()
                        self.text += letter

    def cancel_edit(self):
        self.editable = False

    def get_text(self):
        return self.text
