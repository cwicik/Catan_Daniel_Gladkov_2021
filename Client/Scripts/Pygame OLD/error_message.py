import pygame
import json
pygame.init()

ERROR_COLOR = (255, 0, 0)
RED = (180, 30, 45)


class Message:

    def __init__(self, screen, x, y, code, size=20):
        self.screen = screen
        with open('../Json/error_messages.json') as file:
            """  
              1xx successful – the request was successfully received, understood, and accepted
              2xx server error – the server failed to fulfil an apparently valid request
              3xx client error – the request contains bad syntax or cannot be fulfilled
            """
            self.text = json.load(file)[code]
        self.x = x
        self.y = y
        self.color = RED if code[0] == '4' else ERROR_COLOR
        self.font = pygame.font.SysFont('Comic Sans MS', size)


    def draw_self(self):
        self.screen.blit(self.font.render(self.text, True, self.color), (self.x, self.y))

    def get_text(self):
        return self.text

    def add_text(self, text):
        self.text = self.text + ' ' + text

    def set_text(self, text):
        self.text = text