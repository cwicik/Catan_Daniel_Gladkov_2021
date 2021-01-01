import socket
import math
import pygame
import threading
import time
from button import Button
from textbox import TextBox
from client import Client
from error_message import Message

pygame.font.init()

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
REFRESH_RATE = 60
LEFT = 1
running = True

# Initializing Vars
clock = pygame.time.Clock()
font = pygame.font.SysFont('Comic Sans MS', 75)
title_font = pygame.font.SysFont('Comic Sans MS', 100)

# Init screen
screen = pygame.display.set_mode((960, 540), pygame.RESIZABLE)
WINDOW_WIDTH = screen.get_width()
WINDOW_HEIGHT = screen.get_height()
pygame.display.set_caption("Catan")
screen.fill(BLACK)

# Current items activated
active_buttons = ()
active_text_box = ()
active_message_codes = []
client_socket = None


def loading_cycles():
    color1 = (255, 255, 255)
    color2 = (230, 230, 230)
    color3 = (179, 179, 179)
    color4 = (102, 102, 102)
    color5 = (77, 77, 77)
    color6 = (51, 51, 51)
    color7 = (26, 26, 26)
    color8 = (13, 13, 13)
    cycle = [color1, color2, color3, color4, color5, color6, color7, color8]
    while True:
        yield cycle
        cycle.insert(0, cycle.pop())

cycles = loading_cycles()

def loading(cycles):
    center = (300, 300)
    cycle = next(cycles)
    for i in range(8):
        pygame.draw.circle(screen, cycle[i],
                           (center[0] + 30 * math.cos(i * math.pi / 4), center[1] + 30 * math.sin(i * math.pi / 4)),
                           10)

def connect_to_server():
    global active_message_codes
    global client_socket
    client_socket = Client('127.0.0.1', 1731)
    start = time.time()
    active_message_codes.append('400')
    connected = client_socket.start()
    while connected is not True:
        connected = client_socket.start()
        if '200' not in active_message_codes and time.time() > start + 4:
            active_message_codes.append('200')
        pygame.time.delay(1000)
    if '200' in active_message_codes:
        active_message_codes.remove('200')
    active_message_codes.remove('400')
    opening_screen()

def check_username(username):
    if username_too_short in active_message_codes:
        active_message_codes.remove(username_too_short)
    if 4 < len(username) < 16:
        return True
    active_message_codes.append(username_too_short)
    return False


def check_password(password):
    digit = False
    for character in password:
        if character.isdigit():
            digit = True
    if password_must_contain in active_message_codes:
        active_message_codes.remove(password_must_contain)
    if 6 < len(password) < 32 and not password.islower() and not password.isupper() and digit:
        return True
    active_message_codes.append(password_must_contain)
    return False


def register_user():
    username = active_text_box[0].get_text()
    password = active_text_box[1].get_text()
    usr = check_username(username)
    psw = check_password(password)
    if usr and psw:
        # Hash password here
        #
        #
        #
        if client_socket.register(username, password):
            if username_already_taken in active_message_codes:
                active_message_codes.remove(username_already_taken)
            print('registered!')
            # main_menu()
        else:
            active_message_codes.append(username_already_taken)


def log_in_user():
    username = active_text_box[0].get_text()
    password = active_text_box[1].get_text()
    if client_socket.log_in(username, password):
        #if incorrect_log_in_info in active_message_codes:
            #active_message_codes.remove(incorrect_log_in_info)
        print('logged in!')
        # main_menu()
    else:
        pass
        #active_message_codes.append(incorrect_log_in_info)


def opening_screen():
    global active_text_box
    global active_buttons
    global active_message_codes
    # Buttons
    log_in_button = Button(screen, WINDOW_WIDTH / 2 - 120, WINDOW_HEIGHT - 3 * WINDOW_HEIGHT / 4, 'Log In', log_in)
    register_page_button = Button(screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT - 100, 'Register', register)
    active_buttons = (log_in_button, register_page_button)
    active_text_box = ()
    active_message_codes = []


def register():
    global active_text_box
    global active_buttons
    # Buttons
    register_button = Button(screen, WINDOW_WIDTH / 2 - 120, WINDOW_HEIGHT - 3 * WINDOW_HEIGHT / 4, 'Register', register_user)
    go_back_register = Button(screen, WINDOW_WIDTH / 3 + 65, WINDOW_HEIGHT - 100, 'Go Back', opening_screen)
    active_buttons = (go_back_register, register_button)
    # TextBox
    username = TextBox(screen, WINDOW_WIDTH / 3,  WINDOW_HEIGHT / 3, default_text='Enter Username')
    password = TextBox(screen, WINDOW_WIDTH / 3, WINDOW_HEIGHT / 2, default_text='Enter Password', hidden=True)
    active_text_box = (username, password)


def log_in():
    global active_text_box
    global active_buttons
    # Buttons
    log_in_button = Button(screen, WINDOW_WIDTH / 2 - 120, WINDOW_HEIGHT - 3 * WINDOW_HEIGHT / 4, 'Log In', log_in_user)
    go_back_register = Button(screen, WINDOW_WIDTH / 3 + 65, WINDOW_HEIGHT - 100, 'Go Back', opening_screen)
    active_buttons = (go_back_register, log_in_button)
    # TextBox
    username = TextBox(screen, WINDOW_WIDTH / 3,  WINDOW_HEIGHT / 3, default_text='Enter Username')
    password = TextBox(screen, WINDOW_WIDTH / 3, WINDOW_HEIGHT / 2, default_text='Enter Password', hidden=True)
    active_text_box = (username, password)

def manage_game():
    global cycles
    capitalize = False
    pygame.key.set_repeat(300, 75)
    global running
    while running:
        # Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                for button in active_buttons:
                    button.pressed()
                for text_box in active_text_box:
                    text_box.cancel_edit()
                    text_box.pressed()
            elif event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == 'left shift' or pygame.key.name(event.key) == 'caps lock':
                    capitalize = not capitalize
                for text_box in active_text_box:
                    text_box.update(event.key, capitalize)
            elif event.type == pygame.KEYUP:
                if pygame.key.name(event.key) == 'left shift':
                    capitalize = False

        # Manage Display
        screen.fill(BLACK)
        for button in active_buttons:
            button.hovered_over()
        for text_box in active_text_box:
            text_box.draw_self()
        for code in active_message_codes:
            if code == '400':
                Message(screen, WINDOW_WIDTH / 3, 0, code, 60).draw_self()
                loading(cycles)
            else:
                Message(screen, 0 , WINDOW_WIDTH / 2, code).draw_self()
        pygame.display.flip()
        pygame.time.delay(100)


def main():
    connection_thread = threading.Thread(target=connect_to_server)
    connection_thread.setDaemon(True)
    connection_thread.start()

    manage_game()

if __name__ == '__main__':
    main()
