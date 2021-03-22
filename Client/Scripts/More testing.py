import tkinter.messagebox
from tkinter import *
from math import sin, cos, pi
import threading
from time import sleep, time
import json
from client import Client


root = Tk()

root.title("Catan Board Game")
x = 1980
y = 1080
root.geometry("%dx%d" % (x, y))
root.iconbitmap('../Pictures/Catan_Logo.ico')
# root.resizable(width=False, height=False)
# root.attributes("-fullscreen", True)

s_width = root.winfo_width()
s_height = root.winfo_height()

client_socket = None
current_frame = None
screens = []

# Load images


def to_rgb(rgb):
    return "#%02x%02x%02x" % rgb


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
    dice_image = PhotoImage(file='../Pictures/dice.png')
    red_settlement = PhotoImage(file='../Pictures/red_settlement.png')
    blue_settlement = PhotoImage(file='../Pictures/blue_settlement.png')
    green_settlement = PhotoImage(file='../Pictures/green_settlement.png')
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
                       '2': green_settlement,
                       '3': orange_settlement}

    road_dict = {'0': to_rgb((237, 28, 36)),
                 '1': to_rgb((0, 162, 232)),
                 '2': to_rgb((34, 177, 76)),
                 '3': to_rgb((255, 127, 39))}
except:
    tkinter.messagebox.showerror("Error", "Missing Image Files")

# https://github.com/rosshamish/hexgrid

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
              0x61: (477, 815), 0x63: (553, 680), 0x65: (629, 545), 0x67: (707, 410), 0x69: (784, 275), 0x6B: (862, 140),
              0x72: (553, 770), 0x74: (629, 635), 0x76: (707, 500), 0x78: (784, 365), 0x7A: (862, 230),
              0x83: (629, 815), 0x85: (707, 680), 0x87: (784, 545), 0x89: (862, 410), 0x8B: (935, 275),
              0x94: (707, 770), 0x96: (784, 635), 0x98: (862, 500), 0x9A: (935, 365),
              0xA5: (784, 815), 0xA7: (862, 680), 0xA9: (935, 545), 0xAB: (1017, 410),
              0xB6: (862, 770), 0xB8: (935, 635), 0xBA: (1017, 500)}

road_cords = {0x0: ((245, 432,5), (245, 477.5)), 0x1: ((263.875, 398.75), (301.625, 376.25)), 0x2: ((322.5, 297.5), (322.5, 347.5)), 0x3: ((341.375, 263.75), (379.125, 241.25)), 0x4: ((399.5, 162.5), (398.5, 207.5)),  0x5: ((418.5, 128.75), (455.5, 106.25)),
              0x10: ((264.0, 511.25), (302.0, 533.75)), 0x12: ((339.875, 376.25), (378.625, 398.75)), 0x14: ((417.0, 241.25), (455.0, 263.75)), 0x16: ((493.75, 106.25), (533.25, 128.75)),
              0x20: ((321.0, 567.5), (321.0, 612.5)), 0x21: ((340.25, 533.75), (378.75, 511.25)), 0x22: ((398.0, 432.5), (398.0, 477.5)), 0x23: ((417.0, 398.75), (455.0, 376.25)), 0x24: ((474.0, 297.5), (474.0, 342.5)), 0x25: ((493.75, 263.75), (533.25, 241.25)), 0x26: ((553.0, 162.5), (553.0, 207.5)), 0x27: ((572.0, 128.75), (610.0, 106.25)),
              0x30: ((340.25, 646.25), (378.75, 668.75)), 0x32: ((417.875, 511.25), (457.625, 533.75)), 0x34: ((493.75, 376.25), (533.25, 398.75)), 0x36: ((571.75, 241.25), (609.25, 263.75)), 0x38: ((648.5, 106.25), (687.5, 128.75)),
              0x40: ((398.0, 702.5), (398.0, 747.5)), 0x41: ((417.75, 668.75), (457.25, 646.25)), 0x42: ((477.375, 567.5), (477.125, 612.5)), 0x43: ((496.375, 533.75), (534.125, 511.25)), 0x44: ((553.0, 432.5), (553.0, 477.5)), 0x45: ((571.75, 398.75), (609.25, 376.25)), 0x46: ((629.0, 297.5), (629.0, 342.5)), 0x47: ((647.75, 263.75), (687.25, 241.25)), 0x48: ((707.0, 162.5), (707.0, 207.5)), 0x49: ((726.25, 128.75), (764.75, 106.25)),
              0x50: ((417.75, 781.25), (457.25, 803.75)), 0x52: ((496.0, 646.25), (534.0, 668.75)), 0x54: ((571.75, 511.25), (609.25, 533.75)), 0x56: ((647.75, 376.25), (687.25, 398.75)), 0x58: ((726.25, 241.25), (764.75, 263.75)), 0x5A: ((803.5, 106.25), (842.5, 128.75)),
              0x61: ((496.0, 803.75), (534.0, 781.25)), 0x62: ((553.0, 702.5), (553.0, 747.5)), 0x63: ((571.75, 668.75), (609.25, 646.25)), 0x64: ((629.0, 567.5), (629.0, 612.5)), 0x65: ((647.75, 533.75), (687.25, 511.25)), 0x66: ((707.0, 432.5), (707.0, 477.5)), 0x67: ((726.25, 398.75), (764.75, 376.25)), 0x68: ((784.0, 297.5), (784.0, 342.5)), 0x69: ((803.5, 263.75), (842.5, 241.25)), 0x6A: ((862.0, 162.5), (862.0, 207.5)),
              0x72: ((571.75, 781.25), (609.25, 803.75)), 0x74: ((647.75, 646.25), (687.25, 668.75)), 0x76: ((726.25, 511.25), (764.75, 533.75)), 0x78: ((803.5, 376.25), (842.5, 398.75)), 0x7A: ((880.25, 241.25), (916.75, 263.75)),
              0x83: ((647.75, 803.75), (687.25, 781.25)), 0x84: ((707.0, 702.5), (707.0, 747.5)), 0x85: ((726.25, 668.75), (764.75, 646.25)), 0x86: ((784.0, 567.5), (784.0, 612.5)), 0x87: ((803.5, 533.75), (842.5, 511.25)), 0x88: ((862.0, 432.5), (862.0, 477.5)), 0x89: ((880.25, 398.75), (916.75, 376.25)), 0x8A: ((935.0, 297.5), (935.0, 342.5)),
              0x94: ((726.25, 781.25), (764.75, 803.75)), 0x96: ((803.5, 646.25), (842.5, 668.75)), 0x98: ((880.25, 511.25), (916.75, 533.75)), 0x9A: ((955.5, 376.25), (996.5, 398.75)),
              0xA5: ((803.5, 803.75), (842.5, 781.25)), 0xA6: ((862.0, 702.5), (862.0, 747.5)), 0xA7: ((880.25, 668.75), (916.75, 646.25)), 0xA8: ((935.0, 567.5), (935.0, 612.5)), 0xA9: ((955.5, 533.75), (996.5, 511.25)), 0xAA: ((1017.0, 432.5), (1017.0, 477.5))}

background_frame = Frame(root)
background_frame.place()
canvas = Canvas(background_frame)
canvas.pack(expand=True, fill=BOTH)
canvas.create_image(0, 0, anchor="nw", image=background_image)


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


def attempt_connection(start, client_socket, canvas):
    global connected
    error = canvas.create_text(960, 900, text='', font=('Comic Sans', 30))
    showing_message = False
    while connected is not True:
        if not showing_message and start < time() - 6:
            canvas.itemconfig(error, text='Attempting connection to server')
            showing_message = True
        connected = client_socket.start()


def go_back():
    global stop
    if len(screens) != 0:
        stop = True
        screen = screens.pop()
        if isinstance(screen, tuple):
            screen[0](screen[1])
        else:
            screen()
    else:
        exit()


def connect_to_server():
    global client_socket
    global current_frame
    global connected
    if current_frame is not None:
        current_frame.destroy()

    current_frame = Frame(root)
    current_frame.pack(expand=True, fill=BOTH)
    canvas = Canvas(current_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(960, 540, image=background_image)
    canvas.create_image(960, 194.5, image=title_image)
    back_button = Button(canvas, text='Exit', font=('Comic Sans', 25), command=go_back)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)
    client_socket = Client('127.0.0.1', 1731)
    connected = client_socket.start()
    if connected is not True:
        cycles = loading_cycles()
        start = time()
        client_handler = threading.Thread(target=attempt_connection, args=(start, client_socket, canvas), daemon=True)
        client_handler.start()

    while connected is not True:
        try:
            cycle = next(cycles)
            for i in range(len(cycle)):
                center_x = 962 + 60 * cos(i * pi / 4)
                center_y = 707 + 60 * sin(i * pi / 4)
                canvas.create_oval(center_x - 25, center_y - 25, center_x + 25, center_y + 25,
                                   fill=cycle[i], outline='')
            canvas.update()
            sleep(0.1)
        except:
            pass
    log_in_screen()


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
    canvas.create_text(960, 500, text='Username:', font=('Comic Sans', 25))
    canvas.create_window(960, 540, window=username_entry, height=40, width=300)
    password_entry = Entry(canvas, show='*', textvariable=password, font=('Comic Sans', 25))
    canvas.create_text(960, 600, text='Password:', font=('Comic Sans', 25))
    canvas.create_window(960, 640, window=password_entry, height=40, width=300)
    email_entry = Entry(canvas, textvariable=email, font=('Comic Sans', 25))
    email_entry.bind('<Return>', lambda event=None: register_user(username.get(), password.get(), email.get()))
    canvas.create_text(960, 700, text='Email:', font=('Comic Sans', 25))
    canvas.create_window(960, 740, window=email_entry, height=40, width=300)
    register_button = Button(canvas, text='Register', font=('Comic Sans', 25), command=lambda: register_user(username.get(), password.get(), email.get()))
    canvas.create_window(960, 800, window=register_button, height=45, width=160)
    back_button = Button(canvas, text='Back', font=('Comic Sans', 25), command=go_back)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)

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
    canvas.create_text(960, 500, text='Username:', font=('Comic Sans', 25))
    canvas.create_window(960, 540, window=username_entry, height=40, width=300)
    password_entry = Entry(canvas, show='*', textvariable=password, font=('Comic Sans', 25))
    canvas.create_text(960, 600, text='Password:', font=('Comic Sans', 25))
    canvas.create_window(960, 640, window=password_entry, height=40, width=300)
    log_in_button = Button(canvas, text='Log In', font=('Comic Sans', 25), command=lambda : log_in_user(username.get(), password.get()))
    password_entry.bind('<Return>', lambda event=None: log_in_user(username.get(), password.get()))
    canvas.create_window(960, 720, window=log_in_button, height=45, width=160)
    register_button = Button(canvas, text='Create New Account', font=('Comic Sans', 25), command=register_screen)
    canvas.create_window(960, 800, window=register_button, height=45, width=320)
    back_button = Button(canvas, text='Exit', font=('Comic Sans', 25), command=go_back)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)

    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame


def host_game(username):
    code = client_socket.host_game()
    if code[0] == '1':
        print('confirmed host')
        lobby_screen(code[3:], username)
    else:
        tkinter.messagebox.showerror("Error", get_error(code))


def leave_lobby():
    client_socket.leave_lobby()
    go_back()


def log_off():
    client_socket.log_off()
    go_back()


def start_game():
    client_socket.start_game()


def roll_dice():
    client_socket.roll_dice()


def build_settlement(cords):
    x = client_socket.build_settlement(cords)
    print('built settlement;', x)

def build_road(cords):
    x = client_socket.build_road(cords)
    print('built road;', x)

def finish_turn():
    client_socket.finish_turn()



def get_game_data(client_socket):
    global stop
    global ended
    global game_data
    while True:
        print('getting data..')
        if stop:
            break
        data = client_socket.get_board().split('\t')
        print('data', data)
        if data[0][0] == '4':
            tkinter.messagebox.showerror("Error", get_error(data[0]))
        else:
            game_data = data


def game_screen(username):
    global current_frame
    global client_socket
    global stop
    global ended
    global game_data
    game_data = client_socket.get_board().split('\t')
    threading.Thread(target=get_game_data, args=(client_socket,), daemon=True).start()

    screen_frame = Frame(root)

    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)

    canvas.create_image(195, 50, anchor="nw", image=board_background)
    canvas.create_text(1800, 300, text='Resources', font=('Comic Sans', 25))
    canvas.create_image(1320, 300, anchor="nw", image=dice_image)
    canvas.create_image(1250, 300, anchor="nw", image=dice_image)
    print(game_data)
    current_player = game_data[1]
    points = game_data[3]
    resources = [game_data[i] for i in range(4, 9)]
    tiles = [(game_data[i], game_data[i + 1]) for i in range(9, 46, 2)]
    old_game_data = game_data
    for i in range(len(tiles)):
        x = tile_cords[i][0]
        y = tile_cords[i][1]

        canvas.create_image(x, y, anchor="nw", image=tile_dict[tiles[i][0]])
        if tiles[i][1] != '0':
            canvas.create_oval(x + 55, y + 65, x + 95, y + 105, fill='burlywood2', outline='')
            if len(tiles[i][1]) == 1:
                canvas.create_text(x + 67, y + 70, anchor="nw", text=tiles[i][1], font=('Comic Sans', 22))
            else:
                canvas.create_text(x + 59, y + 70, anchor="nw", text=tiles[i][1], font=('Comic Sans', 22))

    dice_button = Button(canvas, text='Roll Dice', font=('Comic Sans', 25), command=roll_dice)
    canvas.create_window(1275, 400, window=dice_button, height=45, width=200)
    finish_turn_button = Button(canvas, text='Finish Turn', font=('Comic Sans', 25), command=finish_turn)
    canvas.create_window(1275, 600, window=finish_turn_button, height=45, width=200)
    back_button = Button(canvas, text='Back', font=('Comic Sans', 25), command=leave_lobby)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)
    current_roll = canvas.create_text(1150, 500, anchor="nw", text='Last Roll: ', font=('Comic Sans', 25))
    current_play = canvas.create_text(1150, 70, anchor="nw", text='Current Player: ' + current_player, font=('Comic Sans', 25))
    current_points = canvas.create_text(1150, 120, anchor="nw", text='Your Points: ' + points, font=('Comic Sans', 25))
    resources_arr = []

    for i in range(len(resources)):
        x = 1800
        y = 250 + (i + 1) * 100
        canvas.create_image(x, y, anchor="nw", image=resources_dict[str(i)])
        resources_arr.append(canvas.create_text(x - 45, y + 20, anchor="nw", text=resources[i] + 'X', font=('Comic Sans', 25)))

    building_buttons = {}
    for value, cords in node_cords.items():
        building = Button(canvas, image=building_plot, borderwidth=0, highlightthickness=0,
                          command=lambda value=value: build_settlement(value))
        building.bind("<Enter>", func=lambda e, button=building: button.config(image=building_plot_hovered))
        building.bind("<Leave>", func=lambda e, button=building: button.config(image=building_plot))
        building_buttons[str(value)] = canvas.create_window(cords[0], cords[1], window=building, width=20, height=20)

    building_images = {}
    for value, cords in node_cords.items():
        building_images[str(value)] = canvas.create_image(cords[0], cords[1], image=red_settlement)
        canvas.itemconfig(building_images[str(value)], state=HIDDEN)

    road_buttons = {}
    for value, cords in road_cords.items():
        road = canvas.create_line(cords[0][0], cords[0][1], cords[1][0], cords[1][1], width=10, fill='black')
        canvas.tag_bind(road, "<ButtonPress-1>", lambda e, value=value: build_road(value))
        # building.bind("<Enter>", func=lambda e, button=building: button.config(image=building_plot_hovered))
        # building.bind("<Leave>", func=lambda e, button=building: button.config(image=building_plot))
        road_buttons[str(value)] = road

    if current_player != username:
        dice_button.config(state=DISABLED)
        for button in building_buttons.values():
            canvas.itemconfig(button, state=HIDDEN)
        for button in road_buttons.values():
            canvas.itemconfig(button, state=HIDDEN)
    else:
        for button in building_buttons.values():
            canvas.itemconfig(button, state=NORMAL)
        for button in road_buttons.values():
            canvas.itemconfig(button, state=NORMAL)
        dice_button.config(state=NORMAL)

    while True:
        if stop:
            break
        if game_data != old_game_data:
            old_game_data = game_data
            command = game_data[0]
            current_player = game_data[1]
            roll = game_data[2]
            points = game_data[3]
            resources = [game_data[i] for i in range(4, 9)]
            nodes = [(game_data[i], game_data[i + 1], game_data[i + 2]) for i in
                     range(game_data.index('n') + 1, game_data.index('e') - 1, 3)]
            edges = [(game_data[i], game_data[i + 1]) for i in
                     range(game_data.index('e') + 1, game_data.index('x') - 1, 3)]
            extra = [game_data[i] for i in range(game_data.index('x') + 1, len(game_data) - 1)]

            print(game_data)

            if command == 'del':
                restore_nodes = [extra[i] for i in range(extra.index('N') + 1, extra.index('E'),)]
                restore_edges = [extra[i] for i in range(extra.index('E') + 1, len(extra))]

                for node in restore_nodes:
                    print('node', node)
                    canvas.itemconfig(building_images[node], state=HIDDEN)
                    canvas.itemconfig(building_images[node], image=red_settlement)

                for edge in restore_edges:
                    print('edge', edge)
                    canvas.itemconfig(road_buttons[edge], fill='black')
                    canvas.tag_bind(road_buttons[edge], "<ButtonPress-1>", lambda e, value=edge: build_road(value))


            # https://onlinepngtools.com/resize-png
            if current_player != username:
                dice_button.config(state=DISABLED)
                for cords, button in building_buttons.items():
                    if canvas.itemcget(building_images[cords], 'state') == HIDDEN:
                        canvas.itemconfig(button, state=HIDDEN)
                for button in road_buttons.values():
                    if canvas.itemcget(button, 'fill') == 'black':
                        canvas.itemconfig(button, state=HIDDEN)
            else:
                for cords, button in building_buttons.items():
                    if canvas.itemcget(building_images[cords], 'state') == HIDDEN:
                        canvas.itemconfig(button, state=NORMAL)
                for button in road_buttons.values():
                    if canvas.itemcget(button, 'fill') == 'black':
                        canvas.itemconfig(button, state=NORMAL)
                dice_button.config(state=NORMAL)

            canvas.itemconfig(current_points, text='Your Points: ' + points)
            canvas.itemconfig(current_play, text='Current Player: ' + current_player)
            canvas.itemconfig(current_roll, text='Last Roll: ' + roll)
            for i in range(len(resources)):
                canvas.itemconfig(resources_arr[i], text=resources[i] + 'X')

            for i in range(len(nodes)):
                # nodes[i][1] is building type WIP
                canvas.itemconfig(building_buttons[nodes[i][2]], state=HIDDEN)
                canvas.itemconfig(building_images[nodes[i][2]], state=NORMAL)
                canvas.itemconfig(building_images[nodes[i][2]], image=settlement_dict[nodes[i][0]])

            for i in range(len(edges)):
                canvas.itemconfig(road_buttons[edges[i][1]], state=NORMAL)
                canvas.itemconfig(road_buttons[edges[i][1]], fill=road_dict[edges[i][0]])
                canvas.tag_unbind(road_buttons[edges[i][1]], "<ButtonPress-1>")

        canvas.update()
        sleep(0.1)


def get_player_names(client_socket):
    global started
    global player_names
    global stop
    server_input = client_socket.get_player_names()
    player_names = server_input[4:].split('\t')
    started = server_input[:3] == 'srt'
    while not started:
        if stop:
            return
        server_input = client_socket.get_player_names()
        started = server_input[:3] == 'srt'
        if started:
            return
        print('input:', server_input)
        player_names = server_input[4:].split('\t')


def lobby_screen(code, username):
    screens.append((main_menu, username))
    global current_frame
    global started
    global client_socket
    global player_names
    global stop

    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(960, 540, image=background_image)
    canvas.create_image(960, 194.5, image=title_image)
    canvas.create_image(940, 689, image=menu_background_image)
    canvas.create_text(960, 500, text='Players:', font=('Comic Sans', 25))
    canvas.create_text(960, 750, text='Code:', font=('Comic Sans', 25))
    canvas.create_text(960, 785, text=code, font=('Comic Sans', 25))
    start_game_button = Button(canvas, text='Start Game', font=('Comic Sans', 25), command=start_game)
    start_button = canvas.create_window(960, 825, window=start_game_button, height=45, width=180)
    back_button = Button(canvas, text='Back', font=('Comic Sans', 25), command=leave_lobby)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)

    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame

    old_player_names = ''
    stop = False
    server_input = client_socket.get_players(code)
    started = server_input[:3] == 'srt'
    player_names = server_input[4:].split('\t')

    players_arr = []
    for i in range(4):
        players_arr.append(canvas.create_text(960, 500 + (i + 1) * 50, text='', font=('Comic Sans', 25)))

    if not started:
        update_players = threading.Thread(target=get_player_names, args=(client_socket,), daemon=True)
        update_players.start()

    while not started:
        if stop:
            return
        if old_player_names != player_names:
            for i in range(4):
                if i in range(len(player_names)):
                    txt = player_names[i]
                else:
                    txt = ''
                canvas.itemconfig(players_arr[i], text=txt)
            if username == player_names[0]: #and len(player_names) >= 2:
                canvas.itemconfig(start_button, state=NORMAL)
            else:
                canvas.itemconfig(start_button, state=HIDDEN)

            old_player_names = player_names
        canvas.update()
        sleep(0.1)
    game_screen(username)


def join_lobby(join_code, username):
    code = client_socket.join_game(join_code)
    if code[0] == '1':
        lobby_screen(join_code, username)
    else:
        tkinter.messagebox.showerror("Error", get_error(code))


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
    canvas.create_text(960, 500, text='Welcome ' + username, font=('Comic Sans', 25))
    host_lobby_button = Button(canvas, text='Host Game', font=('Comic Sans', 25),
                               command=lambda: host_game(username))
    canvas.create_window(960, 575, window=host_lobby_button, height=45, width=180)
    join_lobby_button = Button(canvas, text='Join Game', font=('Comic Sans', 25),
                               command=lambda: join_lobby(code.get(), username))
    canvas.create_window(960, 650, window=join_lobby_button, height=45, width=180)
    code_entry = Entry(canvas, textvariable=code, font=('Comic Sans', 25))
    code_entry.bind('<Return>', lambda event=None: join_lobby(code.get(), username))
    canvas.create_window(960, 700, window=code_entry, height=40, width=180)

    back_button = Button(canvas, text='Back', font=('Comic Sans', 25), command=log_off)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)

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
        print('confirmed email')
        log_in_user(username, password)
    else:
        tkinter.messagebox.showerror("Error", get_error(code))


def cancel_code():
    client_socket.cancel()
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
    canvas.create_text(960, 600, text='Enter Received Code:', font=('Comic Sans', 25))
    code_entry = Entry(canvas, textvariable=code, font=('Comic Sans', 25))
    canvas.create_window(960, 650, window=code_entry, height=40, width=180)
    code_entry.bind('<Return>', lambda event=None: confirm_email(code.get(), username, password))
    confirm_button = Button(canvas, text='Confirm Email', font=('Comic Sans', 25),
           command=lambda: confirm_email(code.get(), username, password))
    canvas.create_window(960, 720, window=confirm_button, height=45, width=240)
    back_button = Button(canvas, text='Back', font=('Comic Sans', 25), command= cancel_code)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)

    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame


def register_user(username, password, email):
    global current_frame
    code = client_socket.register(username, password, email)
    if code[0] == '1':
        confirm_email_screen(username, password)
    else:
        tkinter.messagebox.showerror("Error", get_error(code))


def log_in_user(username, password):
    username = 'cwicik1'
    password = 'Shnizel123'
    code = client_socket.log_in(username, password)
    if code[0] == '1':
        print('logged in!')
        main_menu(username)
    else:
        tkinter.messagebox.showerror("Error", get_error(code))


def main():
    threading.Thread(target=connect_to_server, daemon=True).start()
    mainloop()


if __name__ == '__main__':
    main()

# TODO: road building, trade screen, winning condition, only show buttons that you can click
