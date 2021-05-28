"""
Student Name: Daniel Gladkov
Date: 21/5/2021
"""

#Install all dependencies
import subprocess
print('Installing dependencies...')
subprocess.call(['Install_dependencies_client.bat'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
print('All dependencies installed!')


import json
import threading
import tkinter.messagebox
from webbrowser import open as open_link
from math import sin, cos, pi
from random import randint
from time import sleep, time
from tkinter import *
from tkinter.font import nametofont
from winsound import PlaySound, SND_ASYNC
from client import Client

root = Tk()
root.title('Catan Board Game')
root.iconbitmap('../Pictures/Catan_Logo.ico')

default_font = nametofont('TkDefaultFont')
default_font.configure(size=25)
default_font.configure(family='Comic Sans')

root.attributes('-fullscreen', True)

current_frame = Frame(root)
screens = []
stop = True
connected = False


def to_rgb(rgb):
    return '#%02x%02x%02x' % rgb


try:
    background_image = PhotoImage(file='../Pictures/Catan_Background.png')
    title_image = PhotoImage(file='../Pictures/Catan_Title.png')
    menu_background_image = PhotoImage(file='../Pictures/Red_Ribbon_Background.png')

    clay_tile = PhotoImage(file='../Pictures/clay_tile.png')
    desert_tile = PhotoImage(file='../Pictures/desert_tile.png')
    sheep_tile = PhotoImage(file='../Pictures/sheep_tile.png')
    stone_tile = PhotoImage(file='../Pictures/stone_tile.png')
    tree_tile = PhotoImage(file='../Pictures/tree_tile.png')
    wheat_tile = PhotoImage(file='../Pictures/wheat_tile.png')

    clay_logo = PhotoImage(file='../Pictures/clay_logo.png')
    sheep_logo = PhotoImage(file='../Pictures/sheep_logo.png')
    stone_logo = PhotoImage(file='../Pictures/stone_logo.png')
    tree_logo = PhotoImage(file='../Pictures/tree_logo.png')
    wheat_logo = PhotoImage(file='../Pictures/wheat_logo.png')
    board_background = PhotoImage(file='../Pictures/board_background.png')

    building_plot = PhotoImage(file='../Pictures/building_plot.png')
    building_plot_hovered = PhotoImage(file='../Pictures/building_plot_hovered.png')

    dice_1_image = PhotoImage(file='../Pictures/dice_1.png')
    dice_2_image = PhotoImage(file='../Pictures/dice_2.png')
    dice_3_image = PhotoImage(file='../Pictures/dice_3.png')
    dice_4_image = PhotoImage(file='../Pictures/dice_4.png')
    dice_5_image = PhotoImage(file='../Pictures/dice_5.png')
    dice_6_image = PhotoImage(file='../Pictures/dice_6.png')
    cost_card_image = PhotoImage(file='../Pictures/building_cost_card.png')

    rolling_dice_image = PhotoImage(file='../Pictures/rolling_dice.png')
    building_image = PhotoImage(file='../Pictures/hammer.png')
    waiting_image = PhotoImage(file='../Pictures/waiting.png')

    up_arrow_image = PhotoImage(file='../Pictures/up_arrow.png')
    down_arrow_image = PhotoImage(file='../Pictures/down_arrow.png')

    red_settlement = PhotoImage(file='../Pictures/red_settlement.png')
    blue_settlement = PhotoImage(file='../Pictures/blue_settlement.png')
    purple_settlement = PhotoImage(file='../Pictures/purple_settlement.png')
    orange_settlement = PhotoImage(file='../Pictures/orange_settlement.png')

    resources_dict = {'0': sheep_logo,
                      '1': tree_logo,
                      '2': wheat_logo,
                      '3': clay_logo,
                      '4': stone_logo}

    tile_dict = {'0': sheep_tile,
                 '1': tree_tile,
                 '2': wheat_tile,
                 '3': clay_tile,
                 '4': stone_tile,
                 '5': desert_tile}

    settlement_dict = {'0': red_settlement,
                       '1': blue_settlement,
                       '2': purple_settlement,
                       '3': orange_settlement}

    player_color_dict = {'0': to_rgb((237, 28, 36)),
                         '1': to_rgb((0, 162, 232)),
                         '2': to_rgb((163, 73, 164)),
                         '3': to_rgb((255, 127, 39))}

    dice_dict = {1: dice_1_image,
                 2: dice_2_image,
                 3: dice_3_image,
                 4: dice_4_image,
                 5: dice_5_image,
                 6: dice_6_image}

except TclError:
    tkinter.messagebox.showerror('Error', 'Missing Some Image Files')

tile_cords = [(400, 100), (322.5, 235), (245, 370),
              (322.5, 505), (400, 640), (555, 640), (710, 640),
              (787.5, 505), (865, 370), (787.5, 235), (710, 100), (555, 100),
              (477.5, 235), (400, 370), (477.5, 505), (632.5, 505),
              (710, 370), (632.5, 235), (555, 370)]

node_cords = {0x1: (245, 410), 0x3: (322.5, 275),  0x5: (400, 140),
              0x10: (245, 500), 0x12: (320.5, 365), 0x14: (398, 230), 0x16: (474, 95),
              0x21: (321, 545), 0x23: (398, 410), 0x25: (474, 275), 0x27: (553, 140),
              0x30: (321, 635), 0x32: (398, 500), 0x34: (474, 365), 0x36: (553, 230), 0x38: (629, 95),
              0x41: (398, 680), 0x43: (477.5, 545), 0x45: (553, 410), 0x47: (629, 275), 0x49: (707, 140),
              0x50: (398, 770), 0x52: (477, 635), 0x54: (553, 500), 0x56: (629, 365), 0x58: (707, 230), 0x5A: (784, 95),
              0x61: (477, 815), 0x63: (553, 680), 0x65: (629, 545), 0x67: (707, 410), 0x69: (784, 275),
              0x6B: (862, 140), 0x72: (553, 770), 0x74: (629, 635), 0x76: (707, 500), 0x78: (784, 365),
              0x7A: (862, 230), 0x83: (629, 815), 0x85: (707, 680), 0x87: (784, 545), 0x89: (862, 410),
              0x8B: (935, 275), 0x94: (707, 770), 0x96: (784, 635), 0x98: (862, 500), 0x9A: (935, 365),
              0xA5: (784, 815), 0xA7: (862, 680), 0xA9: (935, 545), 0xAB: (1017, 410),
              0xB6: (862, 770), 0xB8: (935, 635), 0xBA: (1017, 500)}

road_cords = {0x0: ((245, 432.5), (245, 477.5)), 0x1: ((263.875, 398.75), (301.625, 376.25)),
              0x2: ((322.5, 297.5), (322.5, 347.5)), 0x3: ((341.375, 263.75), (379.125, 241.25)),
              0x4: ((399.5, 162.5), (398.5, 207.5)),  0x5: ((418.5, 128.75), (455.5, 106.25)),
              0x10: ((264.0, 511.25), (302.0, 533.75)), 0x12: ((339.875, 376.25), (378.625, 398.75)),
              0x14: ((417.0, 241.25), (455.0, 263.75)), 0x16: ((493.75, 106.25), (533.25, 128.75)),
              0x20: ((321.0, 567.5), (321.0, 612.5)), 0x21: ((340.25, 533.75), (378.75, 511.25)),
              0x22: ((398.0, 432.5), (398.0, 477.5)), 0x23: ((417.0, 398.75), (455.0, 376.25)),
              0x24: ((474.0, 297.5), (474.0, 342.5)), 0x25: ((493.75, 263.75), (533.25, 241.25)),
              0x26: ((553.0, 162.5), (553.0, 207.5)), 0x27: ((572.0, 128.75), (610.0, 106.25)),
              0x30: ((340.25, 646.25), (378.75, 668.75)), 0x32: ((417.875, 511.25), (457.625, 533.75)),
              0x34: ((493.75, 376.25), (533.25, 398.75)), 0x36: ((571.75, 241.25), (609.25, 263.75)),
              0x38: ((648.5, 106.25), (687.5, 128.75)), 0x40: ((398.0, 702.5), (398.0, 747.5)),
              0x41: ((417.75, 668.75), (457.25, 646.25)), 0x42: ((477.375, 567.5), (477.125, 612.5)),
              0x43: ((496.375, 533.75), (534.125, 511.25)), 0x44: ((553.0, 432.5), (553.0, 477.5)),
              0x45: ((571.75, 398.75), (609.25, 376.25)), 0x46: ((629.0, 297.5), (629.0, 342.5)),
              0x47: ((647.75, 263.75), (687.25, 241.25)), 0x48: ((707.0, 162.5), (707.0, 207.5)),
              0x49: ((726.25, 128.75), (764.75, 106.25)), 0x50: ((417.75, 781.25), (457.25, 803.75)),
              0x52: ((496.0, 646.25), (534.0, 668.75)), 0x54: ((571.75, 511.25), (609.25, 533.75)),
              0x56: ((647.75, 376.25), (687.25, 398.75)), 0x58: ((726.25, 241.25), (764.75, 263.75)),
              0x5A: ((803.5, 106.25), (842.5, 128.75)), 0x61: ((496.0, 803.75), (534.0, 781.25)),
              0x62: ((553.0, 702.5), (553.0, 747.5)), 0x63: ((571.75, 668.75), (609.25, 646.25)),
              0x64: ((629.0, 567.5), (629.0, 612.5)), 0x65: ((647.75, 533.75), (687.25, 511.25)),
              0x66: ((707.0, 432.5), (707.0, 477.5)), 0x67: ((726.25, 398.75), (764.75, 376.25)),
              0x68: ((784.0, 297.5), (784.0, 342.5)), 0x69: ((803.5, 263.75), (842.5, 241.25)),
              0x6A: ((862.0, 162.5), (862.0, 207.5)), 0x72: ((571.75, 781.25), (609.25, 803.75)),
              0x74: ((647.75, 646.25), (687.25, 668.75)), 0x76: ((726.25, 511.25), (764.75, 533.75)),
              0x78: ((803.5, 376.25), (842.5, 398.75)), 0x7A: ((880.25, 241.25), (916.75, 263.75)),
              0x83: ((647.75, 803.75), (687.25, 781.25)), 0x84: ((707.0, 702.5), (707.0, 747.5)),
              0x85: ((726.25, 668.75), (764.75, 646.25)), 0x86: ((784.0, 567.5), (784.0, 612.5)),
              0x87: ((803.5, 533.75), (842.5, 511.25)), 0x88: ((862.0, 432.5), (862.0, 477.5)),
              0x89: ((880.25, 398.75), (916.75, 376.25)), 0x8A: ((935.0, 297.5), (935.0, 342.5)),
              0x94: ((726.25, 781.25), (764.75, 803.75)), 0x96: ((803.5, 646.25), (842.5, 668.75)),
              0x98: ((880.25, 511.25), (916.75, 533.75)), 0x9A: ((955.5, 376.25), (996.5, 398.75)),
              0xA5: ((803.5, 803.75), (842.5, 781.25)), 0xA6: ((862.0, 702.5), (862.0, 747.5)),
              0xA7: ((880.25, 668.75), (916.75, 646.25)), 0xA8: ((935.0, 567.5), (935.0, 612.5)),
              0xA9: ((955.5, 533.75), (996.5, 511.25)), 0xAA: ((1017.0, 432.5), (1017.0, 477.5))}

background_frame = Frame(root)
background_frame.place()
main_canvas = Canvas(background_frame)
main_canvas.pack(expand=True, fill=BOTH)
main_canvas.create_image(0, 0, anchor='nw', image=background_image)


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
    for i in range(len(cycle)):
        cycle[i] = to_rgb(cycle[i])
    while True:
        yield cycle
        cycle.insert(0, cycle.pop())


def attempt_connection(start, connection_canvas):
    global connected
    error = connection_canvas.create_text(960, 900, text='', font=('Comic Sans', 30))
    showing_message = False
    while not connected:
        if not showing_message and start < time() - 6:
            connection_canvas.itemconfig(error, text='Attempting connection to server')
            showing_message = True
        connected = client_socket.start()


def go_back():
    global stop
    if len(screens) != 0:
        if not stop:
            stop = True
            client_socket.stop()
        screen = screens.pop()
        if isinstance(screen, tuple):
            screen[0](screen[1])
        else:
            screen()
    else:
        exit()


def connect_to_server():
    global current_frame
    global connected
    global client_socket
    if current_frame is not None:
        current_frame.destroy()

    current_frame = Frame(root)
    current_frame.pack(expand=True, fill=BOTH)
    canvas = Canvas(current_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(960, 540, image=background_image)
    canvas.create_image(960, 194.5, image=title_image)
    back_button = Button(canvas, text='Exit', command=go_back)
    canvas.create_window(62, 1055, window=back_button, height=45, width=130)
    with open('../Text/Server_IP.txt') as IP_file:
        client_socket = Client(IP_file.readline(), 1731)
    connected = client_socket.start()
    if not connected:
        cycles = loading_cycles()
        start = time()
        client_handler = threading.Thread(target=attempt_connection, args=(start, canvas), daemon=True)
        client_handler.start()

    while not connected:
        try:
            cycle = next(cycles)
            for i, color in enumerate(cycle):
                center_x = 962 + 60 * cos(i * pi / 4)
                center_y = 707 + 60 * sin(i * pi / 4)
                canvas.create_oval(center_x - 25, center_y - 25, center_x + 25, center_y + 25,
                                   fill=color, outline='')
            canvas.update()
            sleep(0.1)
        except:
            pass
    log_in_screen()


def except_server_disconnect():
    global stop
    client_socket.quit()
    stop = True
    tkinter.messagebox.showerror('Error', 'Connection To Server Has Been Disconnected.\nTrying To Reconnect.')
    while len(screens) != 0:
        go_back()
    connect_to_server()


def register_screen():
    screens.append(log_in_screen)
    global current_frame
    username = StringVar()
    password = StringVar()
    email = StringVar()

    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(960, 540, image=background_image)
    canvas.create_image(960, 194.5, image=title_image)
    canvas.create_image(940, 689, image=menu_background_image)

    username_entry = Entry(canvas, textvariable=username, font=('Comic Sans', 25))
    canvas.create_text(960, 500, text='Username:')
    canvas.create_window(960, 540, window=username_entry, height=40, width=300)
    password_entry = Entry(canvas, show='*', textvariable=password, font=('Comic Sans', 25))
    canvas.create_text(960, 600, text='Password:')
    canvas.create_window(960, 640, window=password_entry, height=40, width=300)
    email_entry = Entry(canvas, textvariable=email, font=('Comic Sans', 25))
    email_entry.bind('<Return>', lambda event=None: register_user(username.get(), password.get(), email.get()))
    canvas.create_text(960, 700, text='Email:')
    canvas.create_window(960, 740, window=email_entry, height=40, width=300)
    register_button = Button(canvas, text='Register',
                             command=lambda: register_user(username.get(), password.get(), email.get()))
    canvas.create_window(960, 800, window=register_button, height=45, width=160)
    back_button = Button(canvas, text='Back', command=go_back)
    canvas.create_window(62, 1055, window=back_button, height=45, width=130)
    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame


def log_in_screen():
    global current_frame

    username = StringVar()
    password = StringVar()

    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(960, 540, image=background_image)
    canvas.create_image(960, 194.5, image=title_image)
    canvas.create_image(940, 689, image=menu_background_image)
    username_entry = Entry(canvas, textvariable=username, font=('Comic Sans', 25))
    canvas.create_text(960, 500, text='Username:')
    canvas.create_window(960, 540, window=username_entry, height=40, width=300)
    password_entry = Entry(canvas, show='*', textvariable=password, font=('Comic Sans', 25))
    canvas.create_text(960, 600, text='Password:')
    canvas.create_window(960, 640, window=password_entry, height=40, width=300)
    log_in_button = Button(canvas, text='Log In',
                           command=lambda : log_in_user(username.get(), password.get()))
    password_entry.bind('<Return>', lambda event=None: log_in_user(username.get(), password.get()))
    canvas.create_window(960, 720, window=log_in_button, height=45, width=160)
    register_button = Button(canvas, text='Create New Account', command=register_screen)
    canvas.create_window(960, 800, window=register_button, height=45, width=320)
    back_button = Button(canvas, text='Exit', command=go_back)
    canvas.create_window(62, 1055, window=back_button, height=45, width=130)
    manual_button = Button(canvas, text='Game Rules', command=lambda:
                           open_link(r'https://www.catan.com/files/downloads/catan_base_rules_2020_200707.pdf'))
    canvas.create_window(1825, 1055, window=manual_button, height=45, width=200)
    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame


def host_game(username):
    try:
        code = client_socket.host_game()
    except ConnectionError:
        except_server_disconnect()
        return
    if code[0] == '1':
        lobby_screen(code[3:], username)
    else:
        tkinter.messagebox.showerror('Error', get_error(code))


def win_screen(winner):
    global current_frame
    PlaySound('../Sounds/SFX_Win.wav', SND_ASYNC)

    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(960, 540, image=background_image)
    canvas.create_image(960, 194.5, image=title_image)
    canvas.create_image(940, 689, image=menu_background_image)
    canvas.create_text(960, 500, text='The Winner Is')
    canvas.create_text(960, 550, text=winner)
    back_button = Button(canvas, text='Return To Main Menu', command=go_back)
    canvas.create_window(960, 600, window=back_button, height=45, width=320)

    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame


def leave_lobby():
    try:
        client_socket.leave_lobby()
    except ConnectionError:
        except_server_disconnect()
        return
    go_back()


def log_out():
    try:
        client_socket.log_off()
    except ConnectionError:
        except_server_disconnect()
        return
    go_back()


def start_game():
    try:
        client_socket.start_game()
    except ConnectionError:
        except_server_disconnect()


def roll_dice():
    try:
        PlaySound('../Sounds/SFX_Dice_Roll.wav', SND_ASYNC)
        client_socket.roll_dice()
    except ConnectionError:
        except_server_disconnect()


def build_settlement(cords):
    try:
        PlaySound('../Sounds/SFX_Building.wav', SND_ASYNC)
        client_socket.build_settlement(cords)
    except ConnectionError:
        except_server_disconnect()


def build_road(cords):
    try:
        PlaySound('../Sounds/SFX_Building.wav', SND_ASYNC)
        client_socket.build_road(cords)
    except ConnectionError:
        except_server_disconnect()


def finish_turn():
    try:
        client_socket.finish_turn()
    except ConnectionError:
        except_server_disconnect()


def reset_trade_offer(trade_canvas):
    for i in range(5):
        trade_canvas.itemconfig(giving_arr[i][0], text='X0')
        trade_canvas.itemconfig(receiving_arr[i][0], text='X0')
        giving_arr[i][1] = 0
        receiving_arr[i][1] = 0


def trading_screen_toggle_on(game_canvas, trade_canvas):
    PlaySound('../Sounds/SFX_Trade.wav', SND_ASYNC)
    reset_trade_offer(trade_canvas)
    game_canvas.pack_forget()
    trade_canvas.pack(expand=True, fill=BOTH)
    try:
        client_socket.start_trade()
    except ConnectionError:
        except_server_disconnect()


def trading_screen_toggle_off(game_canvas, trade_canvas):
    game_canvas.pack(expand=True, fill=BOTH)
    trade_canvas.pack_forget()


def change_value_up_give(trade_canvas, arr, resource_type):
    global resources
    if arr[resource_type][1] < int(resources[resource_type]):
        arr[resource_type][1] += 1
        trade_canvas.itemconfig(arr[resource_type][0], text='X' + str(arr[resource_type][1]))


def change_value_up_get(trade_canvas, arr, resource_type):
    arr[resource_type][1] += 1
    trade_canvas.itemconfig(arr[resource_type][0], text='X' + str(arr[resource_type][1]))


def change_value_down(trade_canvas, arr, resource_type):
    if arr[resource_type][1]:
        arr[resource_type][1] -= 1
        trade_canvas.itemconfig(arr[resource_type][0], text='X' + str(arr[resource_type][1]))


def offer_trade(offer_to_player):
    global giving_arr
    global receiving_arr
    global trading_partner
    trading_partner = offer_to_player
    trade_info = ''
    for resource in giving_arr + receiving_arr:
        trade_info += str(resource[1]) + '\t'
    trade_info += offer_to_player
    try:
        client_socket.offer_trade(trade_info)
    except ConnectionError:
        except_server_disconnect()


def ask_about_trade(can_afford, trade_info):
    if can_afford:
        header = 'Trade With: ' + trade_info[0]
        you_get = 'You Get:'
        you_give = 'You Give:'
        resources_types = ['Sheep', 'Wood', 'Wheat', 'Clay', 'Stone']
        for i, resource in enumerate(resources_types):
            if int(trade_info[i + 1]):
                you_get += ' ' + trade_info[i + 1] + ' ' + resource
            if int(trade_info[i + 6]):
                you_give += ' ' + trade_info[i + 6] + ' ' + resource
        message = header + '\n' + you_get + '\n' + you_give
        accept_trade = tkinter.messagebox.askyesno('Trade Offer', message)
    else:
        message = 'Trade Offer From ' + trade_info[0] + ' Has Been Auto-Rejected\nBecause You Cant Afford It'
        tkinter.messagebox.showwarning('Trade Offer', message)
        accept_trade = False
    try:
        client_socket.accept_offer() if accept_trade else client_socket.decline_offer()
    except ConnectionError:
        except_server_disconnect()


def get_game_data():
    global stop
    global ended
    global game_data_queue
    global trading_partner

    while not stop:
        try:
            data = client_socket.get_board().split('\t')
        except ConnectionError:
            except_server_disconnect()
            return
        command = data[0]
        if trading_partner:
            if command == 'liv' or command == 'del':
                extra = [data[i] for i in range(data.index('x') + 1, len(data))]
                if trading_partner == extra[0]:
                    trading_partner = ''
            else:
                if command == 'dcl':
                    tkinter.messagebox.showinfo('Trade Deal',
                                                'Trade With {} Has Been Declined.'.format(trading_partner[1:]))
                elif command == 'acp':
                    tkinter.messagebox.showinfo('Trade Deal',
                                                'Trade With {} Has Been Accepted!'.format(trading_partner[1:]))
                elif command == 'inv':
                    tkinter.messagebox.showinfo('Invalid Trade', ' You Have Requested An Invalid Trade')
                trading_partner = ''
                reset_trade_offer()
        if stop:
            break
        if command[0] == '4':
            tkinter.messagebox.showerror('Error', get_error(data[0]))
        else:
            game_data_queue.insert(0, data)


def game_screen(username, player_names):
    global current_frame
    global stop
    global ended
    global resources
    global trading_partner
    global wait_for_confirm
    global giving_arr
    global receiving_arr
    global game_data_queue
    game_data_queue = []
    try:
        game_data = client_socket.get_board().split('\t')
    except ConnectionError:
        except_server_disconnect()
        return
    threading.Thread(target=get_game_data, daemon=True).start()

    screen_frame = Frame(root)

    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame

    trade_canvas = Canvas(screen_frame, bg='PeachPuff2')
    trade_canvas.create_rectangle(500, 50, 1850, 850, fill='gray80', outline='')
    back_to_game = Button(trade_canvas, text='Back To Game',
                          command=lambda: trading_screen_toggle_off(game_canvas, trade_canvas))
    trade_canvas.create_window(1120, 550, anchor='w', window=back_to_game, height=45, width=240)
    reset_offer_button = Button(trade_canvas, text='Reset Offer',
                                command=lambda: reset_trade_offer(trade_canvas))
    trade_canvas.create_window(1120, 600, anchor='w', window=reset_offer_button, height=45, width=240)

    can_trade = False
    trading_partner = ''
    trading_buttons_arr = []
    trade_canvas.create_text(1150, 180, anchor='w', text='Trade With')
    for i in range(3):
        trading_button = Button(trade_canvas, text='', command=print)
        trading_button_window = trade_canvas.create_window(1120, 250 + i * 85, anchor='w', window=trading_button,
                                                           height=45, width=240, state=HIDDEN)
        trading_buttons_arr.append((trading_button, trading_button_window))

    giving_arr = []
    trade_canvas.create_text(600, 180, anchor='w', text='Give')
    for i in range(5):
        up_button = Button(trade_canvas, image=up_arrow_image,
                           command=lambda i=i: change_value_up_give(trade_canvas, giving_arr, i))
        down_button = Button(trade_canvas, image=down_arrow_image,
                             command=lambda i=i: change_value_down(trade_canvas, giving_arr, i))
        trade_canvas.create_window(700, 235 + i * 85, anchor='w', window=up_button, height=20, width=30)
        trade_canvas.create_window(700, 265 + i * 85, anchor='w', window=down_button, height=20, width=30)
        trade_canvas.create_image(550, 250 + i * 85, anchor='w', image=resources_dict[str(i)])
        giving_arr.append([trade_canvas.create_text(620, 250 + i * 85, anchor='w', text='X0'), 0])

    receiving_arr = []
    trade_canvas.create_text(875, 180, anchor='w', text='Receive')
    for i in range(5):
        up_button = Button(trade_canvas, image=up_arrow_image,
                           command=lambda i=i: change_value_up_get(trade_canvas, receiving_arr, i))
        down_button = Button(trade_canvas, image=down_arrow_image,
                             command=lambda i=i: change_value_down(trade_canvas, receiving_arr, i))
        trade_canvas.create_window(1000, 235 + i * 85, anchor='w', window=up_button, height=20, width=30)
        trade_canvas.create_window(1000, 265 + i * 85, anchor='w', window=down_button, height=20, width=30)
        trade_canvas.create_image(850, 250 + i * 85, anchor='w', image=resources_dict[str(i)])
        receiving_arr.append([trade_canvas.create_text(920, 250 + i * 85, anchor='w', text='X0'), 0])

    game_canvas = Canvas(screen_frame, bg='PeachPuff2')
    game_canvas.pack(expand=True, fill=BOTH)

    game_canvas.create_image(195, 50, anchor='nw', image=board_background)
    game_canvas.create_rectangle(1100, 50, 1850, 850, fill='gray80', outline='')
    game_canvas.create_image(1425, 675, anchor='w', image=cost_card_image)
    dice1 = game_canvas.create_image(1350, 450, anchor='w', image=dice_1_image, state=HIDDEN)
    dice2 = game_canvas.create_image(1425, 450, anchor='w', image=dice_1_image, state=HIDDEN)
    current_player_color = game_data[1][0]
    current_player = game_data[1][1:]
    my_color = game_data[2]
    points = game_data[3]
    resources = [game_data[i] for i in range(4, 9)]
    tiles = [(game_data[i], game_data[i + 1]) for i in range(9, 46, 2)]

    del player_names[player_names.index(str(my_color) + username)]

    for i, tile in enumerate(tiles):
        x = tile_cords[i][0]
        y = tile_cords[i][1]
        game_canvas.create_image(x, y, anchor='nw', image=tile_dict[tile[0]])
        if tile[1] != '0':
            game_canvas.create_oval(x + 55, y + 65, x + 95, y + 105, fill='burlywood2', outline='')
            if len(tile[1]) == 1:
                game_canvas.create_text(x + 67, y + 70, anchor='nw', text=tile[1], font=('Comic Sans', 22),
                                        fill='red' if tile[1] == '8' or tile[1] == '6' else 'black')
            else:
                game_canvas.create_text(x + 59, y + 70, anchor='nw', text=tile[1], font=('Comic Sans', 22))

    action_text = game_canvas.create_text(1120, 250, anchor='w',
                                          text='Current Action: ' + ('Building' if username == current_player else
                                                                     'Waiting'))
    action_image = game_canvas.create_image(1170, 350, anchor='w',
                                            image=building_image if username == current_player else waiting_image)
    dice_button = Button(game_canvas, text='Roll Dice', command=roll_dice)
    game_canvas.create_window(1120, 450, anchor='w', window=dice_button, height=45, width=200)
    finish_turn_button = Button(game_canvas, text='Finish Turn',
                                command=finish_turn)
    game_canvas.create_window(1120, 500, anchor='w', window=finish_turn_button, height=45, width=200)
    trade_menu_button = Button(game_canvas, text='Trade',
                               command=lambda: trading_screen_toggle_on(game_canvas, trade_canvas))
    game_canvas.create_window(1120, 550, anchor='w', window=trade_menu_button, height=45, width=200)
    back_button = Button(game_canvas, text='Back', command=leave_lobby)

    game_canvas.create_window(62, 1055, window=back_button, height=45, width=120)
    game_canvas.create_text(1120, 75, anchor='w', text='Your Player: ')
    game_canvas.create_text(1300, 75, anchor='w', text=username,
                            fill=player_color_dict[my_color])
    game_canvas.create_text(1120, 125, anchor='w', text='Current Turn: ')
    current_play = game_canvas.create_text(1320, 125, anchor='w', text=current_player,
                                           fill=player_color_dict[current_player_color])
    current_points = game_canvas.create_text(1120, 175, anchor='w',
                                             text='Your Points: ' + points)

    resources_arr = []
    game_canvas.create_text(1810, 75, anchor='e', text='Resources')
    for i, resource in enumerate(resources):
        y = 50 + (i + 1) * 85
        game_canvas.create_image(1815, y, anchor='e', image=resources_dict[str(i)])
        resources_arr.append(game_canvas.create_text(1740, y, anchor='e', text=resource + 'X'))

    trade_canvas.create_text(1810, 75, anchor='e', text='Resources')
    for i, resource in enumerate(resources):
        y = 50 + (i + 1) * 85
        trade_canvas.create_image(1815, y, anchor='e', image=resources_dict[str(i)])
        resources_arr.append(trade_canvas.create_text(1740, y, anchor='e', text=resource + 'X'))

    building_buttons = {}
    for value, cords in node_cords.items():
        building = Button(game_canvas, image=building_plot, borderwidth=0, highlightthickness=0,
                          command=lambda value=value: build_settlement(value))
        building.bind('<Enter>', func=lambda e, button=building: button.config(image=building_plot_hovered))
        building.bind('<Leave>', func=lambda e, button=building: button.config(image=building_plot))
        building_buttons[str(value)] = game_canvas.create_window(cords[0], cords[1],
                                                                 window=building, width=20, height=20)

    building_images = {}
    for value, cords in node_cords.items():
        building_images[str(value)] = game_canvas.create_image(cords[0], cords[1], image=red_settlement)
        game_canvas.itemconfig(building_images[str(value)], state=HIDDEN)

    road_buttons = {}
    for value, cords in road_cords.items():
        road = game_canvas.create_line(cords[0][0], cords[0][1], cords[1][0], cords[1][1], width=10, fill='black')
        game_canvas.tag_bind(road, '<ButtonPress-1>', lambda e, value=value: build_road(value))
        road_buttons[str(value)] = road

    dice_button.config(state=DISABLED)
    finish_turn_button.config(state=DISABLED)
    trade_menu_button.config(state=DISABLED)

    for button in building_buttons.values():
        game_canvas.itemconfig(button, state=NORMAL if current_player == username else HIDDEN)
    for button in road_buttons.values():
        game_canvas.itemconfig(button, state=NORMAL if current_player == username else HIDDEN)

    while not stop:
        back_to_game.config(state=DISABLED if len(trading_partner) else NORMAL)
        reset_offer_button.config(state=DISABLED if trading_partner else NORMAL)
        for button in trading_buttons_arr:
            button[0].config(state=DISABLED if trading_partner else NORMAL)

        if len(game_data_queue):
            game_data = game_data_queue.pop()
            command = game_data[0]
            current_player_color = game_data[1][0]
            current_player = game_data[1][1:]
            roll1 = int(game_data[2]) // 10 if len(game_data[2]) else ''
            roll2 = int(game_data[2]) % 10 if len(game_data[2]) else ''
            points = game_data[3]
            resources = [game_data[i] for i in range(4, 9)]
            nodes = [(game_data[i], game_data[i + 1]) for i in
                     range(game_data.index('n') + 1, game_data.index('e') - 1, 3)]
            edges = [(game_data[i], game_data[i + 1]) for i in
                     range(game_data.index('e') + 1, game_data.index('x') - 1, 3)]
            extra = [game_data[i] for i in range(game_data.index('x') + 1, len(game_data))]

            if command == 'win':
                try:
                    client_socket.leave_lobby()
                except ConnectionError:
                    except_server_disconnect()
                    return
                win_screen(extra[0])
                break

            if command == 'tro':
                extra.insert(0, current_player)
                ask_about_trade(True, extra)

            if command == 'cnt':
                extra.insert(0, current_player)
                ask_about_trade(False, extra)

            if command == 'del' or command == 'liv':
                restore_nodes = [extra[i] for i in range(extra.index('N') + 1, extra.index('E'),)]
                restore_edges = [extra[i] for i in range(extra.index('E') + 1, len(extra))]

                del player_names[player_names.index(extra[0])]

                for node in restore_nodes:
                    game_canvas.itemconfig(building_images[node], state=HIDDEN)
                    game_canvas.itemconfig(building_images[node], image=red_settlement)

                for edge in restore_edges:
                    game_canvas.itemconfig(road_buttons[edge], fill='black')
                    game_canvas.tag_bind(road_buttons[edge], '<ButtonPress-1>', lambda e, value=edge: build_road(value))

            if current_player == username:
                game_canvas.itemconfig(action_image, image=building_image)
                game_canvas.itemconfig(action_text, text='Current Action: Building')
                dice_button.config(state=DISABLED)
                finish_turn_button.config(state=NORMAL)
                trade_menu_button.config(state=NORMAL if can_trade else DISABLED)
                if command == 'rol' or command == 'del':
                    can_trade = True
                    game_canvas.itemconfig(action_image, image=rolling_dice_image)
                    game_canvas.itemconfig(action_text, text='Current Action: Rolling Dice')
                    dice_button.config(state=NORMAL)
                    finish_turn_button.config(state=DISABLED)
                    trade_menu_button.config(state=DISABLED)
                    for cords, button in building_buttons.items():
                        if game_canvas.itemcget(building_images[cords], 'state') == HIDDEN:
                            game_canvas.itemconfig(button, state=HIDDEN)
                    for button in road_buttons.values():
                        if game_canvas.itemcget(button, 'fill') == 'black':
                            game_canvas.itemconfig(button, state=HIDDEN)
                else:
                    if command == 'srt' or command == 'liv':
                        finish_turn_button.config(state=DISABLED)
                        trade_menu_button.config(state=DISABLED)
                        game_canvas.itemconfig(action_image, image=building_image)
                        game_canvas.itemconfig(action_text, text='Current Action: Building')
                    for cords, button in building_buttons.items():
                        if game_canvas.itemcget(building_images[cords], 'state') == HIDDEN:
                            game_canvas.itemconfig(button, state=NORMAL)
                    for button in road_buttons.values():
                        if game_canvas.itemcget(button, 'fill') == 'black':
                            game_canvas.itemconfig(button, state=NORMAL)
            else:
                game_canvas.itemconfig(action_image, image=waiting_image)
                game_canvas.itemconfig(action_text, text='Current Action: Waiting')
                dice_button.config(state=DISABLED)
                finish_turn_button.config(state=DISABLED)
                trade_menu_button.config(state=DISABLED)
                for cords, button in building_buttons.items():
                    if game_canvas.itemcget(building_images[cords], 'state') == HIDDEN:
                        game_canvas.itemconfig(button, state=HIDDEN)
                for button in road_buttons.values():
                    if game_canvas.itemcget(button, 'fill') == 'black':
                        game_canvas.itemconfig(button, state=HIDDEN)

            if command == 'tri':
                player_names = extra
            for i, trade_button in enumerate(trading_buttons_arr):
                if i < len(player_names):
                    color = player_names[i][0]
                    player_username = player_names[i][1:]
                    trade_button[0].config(text=player_username, fg=player_color_dict[color],
                                           command=lambda color=color, player=player_username:
                                           offer_trade(color + player_username))
                    trade_canvas.itemconfig(trade_button[1], state=NORMAL)
                else:
                    trade_canvas.itemconfig(trade_button[1], state=HIDDEN)

            game_canvas.itemconfig(current_points, text='Your Points: ' + points)
            game_canvas.itemconfig(current_play, text=current_player, fill=player_color_dict[current_player_color])
            if roll1:
                game_canvas.itemconfig(dice1, state=NORMAL, image=dice_dict[roll1])
                game_canvas.itemconfig(dice2, state=NORMAL, image=dice_dict[roll2])
            for i, resource in enumerate(resources):
                game_canvas.itemconfig(resources_arr[i], text=resource + 'X')
                trade_canvas.itemconfig(resources_arr[i + 5], text=resource + 'X')

            for node in nodes:
                game_canvas.itemconfig(building_buttons[node[1]], state=HIDDEN)
                game_canvas.itemconfig(building_images[node[1]], state=NORMAL)
                game_canvas.itemconfig(building_images[node[1]], image=settlement_dict[node[0]])

            for edge in edges:
                game_canvas.itemconfig(road_buttons[edge[1]], state=NORMAL)
                game_canvas.itemconfig(road_buttons[edge[1]], fill=player_color_dict[edge[0]])
                game_canvas.tag_unbind(road_buttons[edge[1]], '<ButtonPress-1>')

        game_canvas.update()
        sleep(0.1)


def get_player_names():
    global started
    global player_names
    global stop
    try:
        server_input = client_socket.get_player_names()
    except ConnectionError:
        except_server_disconnect()
        return
    player_names = server_input[4:].split('\t')
    started = server_input[:3] == 'srt'
    while not started:
        if stop:
            return
        try:
            server_input = client_socket.get_player_names()
        except ConnectionError:
            except_server_disconnect()
            return
        started = server_input[:3] == 'srt'
        if started or stop:
            return
        player_names = server_input[4:].split('\t')


def lobby_screen(code, username):
    screens.append((main_menu, username))
    global current_frame
    global started
    global player_names
    global stop

    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(960, 540, image=background_image)
    canvas.create_image(960, 194.5, image=title_image)
    canvas.create_image(940, 689, image=menu_background_image)
    canvas.create_text(960, 500, text='Players:')
    canvas.create_text(960, 750, text='Code:')
    canvas.create_text(960, 785, text=code)
    start_game_button = Button(canvas, text='Start Game', command=start_game)
    start_button = canvas.create_window(960, 825, window=start_game_button, height=45, width=180)
    back_button = Button(canvas, text='Back', command=leave_lobby)
    canvas.create_window(62, 1055, window=back_button, height=45, width=130)
    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame

    old_player_names = ''
    stop = False
    try:
        server_input = client_socket.get_players(code)
    except ConnectionError:
        except_server_disconnect()
        return
    started = server_input[:3] == 'srt'
    player_names = server_input[4:].split('\t')

    players_arr = [canvas.create_text(960, 500 + (i + 1) * 50, text='') for i in range(4)]

    if not started:
        update_players = threading.Thread(target=get_player_names, daemon=True)
        update_players.start()

    while not started:
        if stop:
            return
        if old_player_names != player_names:
            for i in range(4):
                if i in range(len(player_names)):
                    txt = player_names[i][1:]
                else:
                    txt = ''
                canvas.itemconfig(players_arr[i], text=txt)
            if username == player_names[0][1:] and len(player_names) >= 2:
                canvas.itemconfig(start_button, state=NORMAL)
            else:
                canvas.itemconfig(start_button, state=HIDDEN)

            old_player_names = player_names
        canvas.update()
        sleep(0.1)
    game_screen(username, old_player_names)


def join_lobby(join_code, username):
    try:
        code = client_socket.join_game(join_code)
    except ConnectionError:
        except_server_disconnect()
        return
    if code[0] == '1':
        lobby_screen(join_code, username)
    else:
        tkinter.messagebox.showerror('Error', get_error(code))


def main_menu(username):
    if log_in_screen not in screens:
        screens.append(log_in_screen)
    global current_frame
    code = StringVar()

    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(960, 540, image=background_image)
    canvas.create_image(960, 194.5, image=title_image)
    canvas.create_image(940, 689, image=menu_background_image)
    canvas.create_text(960, 500, text='Welcome ' + username)
    host_lobby_button = Button(canvas, text='Host Game',
                               command=lambda: host_game(username))
    canvas.create_window(960, 575, window=host_lobby_button, height=45, width=180)
    join_lobby_button = Button(canvas, text='Join Game',
                               command=lambda: join_lobby(code.get(), username))
    canvas.create_window(960, 650, window=join_lobby_button, height=45, width=180)
    code_entry = Entry(canvas, textvariable=code, font=('Comic Sans', 20))
    code_entry.bind('<Return>', lambda event=None: join_lobby(code.get(), username))
    canvas.create_text(900, 700, text='Code:', font=('Comic Sans', 20))
    canvas.create_window(995, 700, window=code_entry, height=40, width=110)
    back_button = Button(canvas, text='Log Out', command=log_out)
    canvas.create_window(62, 1055, window=back_button, height=45, width=130)

    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame


def get_error(code):
    with open('../Json/error_messages.json') as file:
        return json.load(file)[code]


def confirm_email(code, username, password):
    code = client_socket.confirm_code(code)
    if code[0] == '1':
        log_in_user(username, password)
    else:
        tkinter.messagebox.showerror('Error', get_error(code))


def cancel_code():
    try:
        client_socket.cancel()
    except ConnectionError:
        except_server_disconnect()
    go_back()


def confirm_email_screen(username, password):
    global current_frame

    code = StringVar()

    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(960, 540, image=background_image)
    canvas.create_image(960, 194.5, image=title_image)
    canvas.create_image(940, 689, image=menu_background_image)
    canvas.create_text(960, 600, text='Enter Received Code:')
    code_entry = Entry(canvas, textvariable=code, font=('Comic Sans', 25))
    canvas.create_window(960, 650, window=code_entry, height=40, width=180)
    code_entry.bind('<Return>', lambda event=None: confirm_email(code.get(), username, password))
    confirm_button = Button(canvas, text='Confirm Email', command=lambda: confirm_email(code.get(), username, password))
    canvas.create_window(960, 720, window=confirm_button, height=45, width=240)
    back_button = Button(canvas, text='Back', command=cancel_code)
    canvas.create_window(62, 1055, window=back_button, height=45, width=130)
    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame


def register_user(username, password, email):
    global current_frame
    try:
        code = client_socket.register(username, password, email)
    except ConnectionError:
        except_server_disconnect()
        return
    if code[0] == '1':
        confirm_email_screen(username, password)
    else:
        tkinter.messagebox.showerror('Error', get_error(code))


def log_in_user(username, password):
    try:
        code = client_socket.log_in(username, password)
    except ConnectionError:
        except_server_disconnect()
        return
    if code[0] == '1':
        main_menu(username)
    else:
        tkinter.messagebox.showerror('Error', get_error(code))


def main():
    PlaySound('../Sounds/Fanfare.wav' if randint(0, 2) else '../Sounds/Fanfare2.wav', SND_ASYNC)
    threading.Thread(target=connect_to_server, daemon=True).start()
    mainloop()


if __name__ == '__main__':
    main()
