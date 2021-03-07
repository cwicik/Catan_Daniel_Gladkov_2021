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
root.geometry("%dx%d" % (x,y))
root.iconbitmap('../Pictures/Catan_Logo.ico')
#root.resizable(width=False, height=False)
#root.attributes("-fullscreen", True)

s_width = root.winfo_width()
s_height = root.winfo_height()

client_socket = None
current_frame = None
screens = []

#Load images
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
except:
    tkinter.messagebox.showerror("Error", "Missing Image Files")


# 77.5, 135
tile_cords = [(400, 100), (322.5, 235), (245, 370),
              (322.5, 505), (400, 640), (555, 640), (710, 640),
              (787.5, 505), (865, 370), (787.5, 235), (710, 100), (555, 100),
              (477.5, 235), (400, 370), (477.5, 505), (632.5,505),
              (710, 370), (632.5, 235), (555, 370)]

node_cords = {0x1: (245, 410), 0x3: (322.5, 275),  0x5: (400, 140), 0x10:(0,0),
              0x12:(0,0), 0x14:(0,0), 0x16:(0,0), 0x21:(0,0),
              0x23:(0,0), 0x25:(0,0), 0x27:(0,0), 0x30:(0,0),
              0x32:(0,0), 0x34:(0,0), 0x36:(0,0), 0x38:(0,0),
              0x41:(0,0), 0x43:(0,0), 0x45:(0,0), 0x47:(0,0),
              0x49:(0,0), 0x50:(0,0), 0x52:(0,0), 0x54:(0,0),
              0x56:(0,0), 0x58:(0,0), 0x5A:(0,0), 0x61:(0,0),
              0x63:(0,0), 0x65:(0,0), 0x67:(0,0), 0x69:(0,0),
              0x6B:(0,0), 0x72:(0,0), 0x74:(0,0), 0x76:(0,0),
              0x78:(0,0), 0x7A:(0,0), 0x83:(0,0), 0x85:(0,0),
              0x87:(0,0), 0x89:(0,0), 0x8B:(0,0), 0x94:(0,0),
              0x96:(0,0), 0x98:(0,0), 0x9A:(0,0), 0xA5:(0,0),
              0xA7:(0,0), 0xA9:(0,0), 0xAB:(0,0), 0xB6:(0,0),
              0xB8:(0,0), 0xBA:(0,0)}



background_frame = Frame(root)
background_frame.place()
canvas = Canvas(background_frame)
canvas.pack(expand=True, fill=BOTH)
canvas.create_image(0, 0, anchor="nw", image=background_image)


def to_rgb(rgb):
    return "#%02x%02x%02x" % rgb


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
        if type(screen) == type((1,)):
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
        client_handler = threading.Thread(target=attempt_connection, args=(start, client_socket, canvas),daemon=True)
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
    canvas.create_image(940, 689,image=menu_background_image)

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
    register_button = Button(canvas, text='Register', font=('Comic Sans', 25), command=lambda : register_user(username.get(), password.get(), email.get()))
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
    canvas.create_image(940, 689,image=menu_background_image)
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


def get_game_data(client_socket):
    global stop
    global ended
    global game_data
    while True:
        print('getting data..')
        if stop:
            break
        game_data = client_socket.get_board().split('\t')
        print(game_data)
        if game_data[0] == 'win':
            break


def game_screen():
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
    old_game_data = ''
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)

    canvas.create_image(195, 50, anchor="nw", image=board_background)
    canvas.create_text(1800, 300, text='Resources', font=('Comic Sans', 25))
    canvas.create_image(1320, 300, anchor="nw", image=dice_image)
    canvas.create_image(1250, 300, anchor="nw", image=dice_image)
    print(game_data)
    command = game_data[0]
    current_player = game_data[1]
    roll = game_data[2]
    points = game_data[3]
    resources = [game_data[i] for i in range(4, 9)]
    tiles = [(game_data[i], game_data[i + 1]) for i in range(9, 46, 2)]
    nodes = [(game_data[i], game_data[i + 1], game_data[i + 2]) for i in
             range(game_data.index('n') + 1, game_data.index('e') - 1, 3)]
    edges = [(game_data[i], game_data[i + 1], game_data[i + 2]) for i in
             range(game_data.index('e') + 1, game_data.index('x') - 1, 3)]
    extra = [game_data[i] for i in range(game_data.index('x') + 1, len(game_data))]
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
    back_button = Button(canvas, text='Back', font=('Comic Sans', 25), command=leave_lobby)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)
    current_roll = canvas.create_text(1150, 500, anchor="nw", text='', font=('Comic Sans', 25))
    current_play = canvas.create_text(1150, 70, anchor="nw", text='Current Player: ' + current_player, font=('Comic Sans', 25))
    current_points = canvas.create_text(1150, 120, anchor="nw", text='Your Points: ' + points, font=('Comic Sans', 25))
    resources_arr = []

    for i in range(len(resources)):
        x = 1800
        y = 250 + (i + 1) * 100
        canvas.create_image(x, y, anchor="nw", image=resources_dict[str(i)])
        resources_arr.append(canvas.create_text(x - 45, y + 20, anchor="nw", text=resources[i] + 'X', font=('Comic Sans', 25)))

    for value, cords in node_cords.items():
        building = Button(canvas, image=building_plot, borderwidth=0, highlightthickness=0,
                          command=lambda value=value: print(value))
        building.bind("<Enter>", func=lambda e, button=building: button.config(image=building_plot_hovered))
        building.bind("<Leave>", func=lambda e, button=building: button.config(image=building_plot))
        canvas.create_window(cords[0], cords[1], window=building, width=20, height=20)

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
            # tiles = [(game_data[i], game_data[i + 1]) for i in range(9, 46, 2)]
            nodes = [(game_data[i], game_data[i + 1], game_data[i + 2]) for i in
                     range(game_data.index('n') + 1, game_data.index('e') - 1, 3)]
            edges = [(game_data[i], game_data[i + 1], game_data[i + 2]) for i in
                     range(game_data.index('e') + 1, game_data.index('x') - 1, 3)]
            extra = [game_data[i] for i in range(game_data.index('x') + 1, len(game_data))]

            print(game_data)

            # https://onlinepngtools.com/resize-png

            canvas.itemconfig(current_points, text='Your Points: ' + points)
            canvas.itemconfig(current_play, text='Current Player: ' + current_player)
            canvas.itemconfig(current_roll, text='Last Roll: ' + roll)
            for i in range(len(resources)):
                canvas.itemconfig(resources_arr[i], text=resources[i] + 'X')

            for node in nodes:
                pass
            # check if building exists, else do button

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
    canvas.create_image(940, 689,image=menu_background_image)
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
    game_screen()


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
    canvas.create_image(940, 689,image=menu_background_image)
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
    canvas.create_image(940, 689,image=menu_background_image)
    canvas.create_text(960, 600, text='Enter Received Code:', font=('Comic Sans', 25))
    code_entry = Entry(canvas, textvariable=code, font=('Comic Sans', 25))
    canvas.create_window(960, 650, window=code_entry, height=40, width=180)
    code_entry.bind('<Return>', lambda event=None: confirm_email(code.get(), username, password))
    confirm_button = Button(canvas, text='Confirm Email', font=('Comic Sans', 25),
           command=lambda : confirm_email(code.get(), username, password))
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