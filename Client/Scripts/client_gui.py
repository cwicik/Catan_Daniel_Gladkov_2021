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

# 112.5, 200
tile_cords = [(500, 100), (387.5, 300), (275,500),
              (0,0), (0,0), (0,0), (0,0),
              (0,0), (0,0), (0,0), (0,0), (0,0),
              (0,0), (0,0), (0,0), (0,0),
              (0,0), (0,0), (0,0)]

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
    while connected is not True:
        if start < time() - 4:
            canvas.create_text(0, s_height/1.2, anchor="nw", text=connected, font=('Comic Sans', 30))
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
    canvas.create_image(0, 0,anchor="nw", image=background_image)
    canvas.create_image((s_width - title_image.width())/2, 0, anchor="nw", image=title_image)
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
                canvas.create_oval(s_width/2 + 60 * cos(i * pi / 4) - 25, s_height/1.5 + 60 * sin(i * pi / 4) - 25,
                               s_width/2 + 60 * cos(i * pi / 4) + 25, s_height/1.5 + 60 * sin(i * pi / 4) + 25,
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
    canvas.create_image(0, 0,anchor="nw", image=background_image)
    canvas.create_image((s_width - title_image.width())/2, 0, anchor="nw", image=title_image)
    canvas.create_image((s_width - menu_background_image.width()) / 2, title_image.height() + 50,anchor="nw", image=menu_background_image)

    username_entry = Entry(canvas, textvariable=username, font=('Comic Sans', 25))
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 135, title_image.height() + 80, anchor="nw", text='Username:', font=('Comic Sans', 25))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 150, window=username_entry, height=40, width=300)
    password_entry = Entry(canvas, show='*', textvariable=password, font=('Comic Sans', 25))
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 135, title_image.height() + 180, anchor="nw", text='Password:', font=('Comic Sans', 25))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 250, window=password_entry, height=40, width=300)
    email_entry = Entry(canvas, textvariable=email, font=('Comic Sans', 25))
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 165, title_image.height() + 280, anchor="nw", text='Email:', font=('Comic Sans', 25))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 350, window=email_entry, height=40, width=300)
    register_button = Button(canvas, text='Register', font=('Comic Sans', 25), command=lambda : register_user(username.get(), password.get(), email.get()))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 420, window=register_button, height=45, width=160)
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
    canvas.create_image(0, 0,anchor="nw", image=background_image)
    canvas.create_image((s_width - title_image.width())/2, 0, anchor="nw", image=title_image)
    canvas.create_image((s_width - menu_background_image.width()) / 2, title_image.height() + 50,anchor="nw", image=menu_background_image)
    username_entry = Entry(canvas, textvariable=username, font=('Comic Sans', 25))
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 135, title_image.height() + 80, anchor="nw", text='Username:', font=('Comic Sans', 25))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 150, window=username_entry, height=40, width=300)
    password_entry = Entry(canvas, show='*', textvariable=password, font=('Comic Sans', 25))
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 135, title_image.height() + 180, anchor="nw", text='Password:', font=('Comic Sans', 25))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 250, window=password_entry, height=40, width=300)
    log_in_button = Button(canvas, text='Log In', font=('Comic Sans', 25), command=lambda : log_in_user(username.get(), password.get()))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 320, window=log_in_button, height=45, width=160)
    register_button = Button(canvas, text='Create New Account', font=('Comic Sans', 25), command=register_screen)
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 400, window=register_button, height=45, width=320)
    back_button = Button(canvas, text='Exit', font=('Comic Sans', 25), command=go_back)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)

    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame


def host_game(username):
    code = client_socket.host_game()
    if code[0] == '1':
        print('confirmed')
        hosting_game_screen(code[3:], username)
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


def game_screen(username):
    screens.append((main_menu, username))
    global current_frame
    global client_socket
    game_data = client_socket.get_board().split('\t')
    command = game_data[0]
    points = game_data[1]
    resources = [game_data[i] for i in range(2, 7)]
    tiles = [(game_data[i], game_data[i+1]) for i in range(7, 44, 2)]
    nodes = [(game_data[i], game_data[i+1]) for i in range(game_data.index('n') + 1, game_data.index('e') - 1, 2)]
    edges = [(game_data[i], game_data[i+1]) for i in range(game_data.index('e') + 1, len(game_data), 2)]

    print(game_data)
    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
# https://onlinepngtools.com/resize-png
    for i in range(len(tiles)):
        x = tile_cords[i][0]
        y = tile_cords[i][1]
        print(tile_dict[tiles[i][0]].width())
        print(tile_dict[tiles[i][0]].height())
        canvas.create_image(x, y, anchor="nw", image=tile_dict[tiles[i][0]])
        canvas.create_text(x + 111, y + 127.5, anchor="nw", text=tiles[i][1], font=('Comic Sans', 25))

    #canvas.create_text((s_width - menu_background_image.width()) / 2 + 145, title_image.height() + 65, anchor="nw",
     #                  text='Players:', font=('Comic Sans', 25))
    #canvas.create_text((s_width - menu_background_image.width()) / 2 + 165, title_image.height() + 320, anchor="nw",
     #                  text='Code:', font=('Comic Sans', 25))
    back_button = Button(canvas, text='Back', font=('Comic Sans', 25), command=leave_lobby)
    canvas.create_window(70, s_height - 70, window=back_button, height=45, width=160)

    if current_frame is not None:
        current_frame.destroy()
        screen_frame.pack(expand=True, fill=BOTH)
        current_frame = screen_frame

def get_player_names(client_socket):
    global started
    global player_names
    global stop
    server_input = client_socket.get_player_names()
    player_names = server_input[3:].split('\t')
    started = server_input[:3] == 'srt'
    while not started:

        if stop:
            return
        server_input = client_socket.get_player_names()
        started = server_input[:3] == 'srt'
        if started:
            print('no names, starting.')
            return
        print(server_input)
        player_names = server_input[3:].split('\t')


def join_game_screen(code, username):
    screens.append((main_menu, username))
    global current_frame
    global started
    global client_socket
    global player_names
    global stop

    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(0, 0, anchor="nw", image=background_image)
    canvas.create_image((s_width - title_image.width()) / 2, 0, anchor="nw", image=title_image)
    canvas.create_image((s_width - menu_background_image.width()) / 2, title_image.height() + 50, anchor="nw",
                        image=menu_background_image)
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 145, title_image.height() + 65, anchor="nw",
                       text='Players:', font=('Comic Sans', 25))
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 165, title_image.height() + 320, anchor="nw",
                       text='Code:', font=('Comic Sans', 25))
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 158, title_image.height() + 360, anchor="nw",
                       text=code, font=('Comic Sans', 25))
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
    player_names = server_input[3:].split('\t')
    print(started)
    if not started:
        update_players = threading.Thread(target=get_player_names, args=(client_socket,), daemon=True)
        update_players.start()
    while not started:
        if stop:
            return
        if old_player_names != player_names:
            if len(old_player_names) > len(player_names):
                canvas.create_image((s_width - menu_background_image.width()) / 2, title_image.height() + 50,
                                    anchor="nw",
                                    image=menu_background_image)
                canvas.create_text((s_width - menu_background_image.width()) / 2 + 145, title_image.height() + 65,
                                   anchor="nw",
                                   text='Players:', font=('Comic Sans', 25))
                canvas.create_text((s_width - menu_background_image.width()) / 2 + 165, title_image.height() + 320,
                                   anchor="nw",
                                   text='Code:', font=('Comic Sans', 25))
                canvas.create_text((s_width - menu_background_image.width()) / 2 + 158, title_image.height() + 360,
                                   anchor="nw",
                                   text=code, font=('Comic Sans', 25))
                if player_names[0] == username:
                    start_game_button = Button(canvas, text='Start Game', font=('Comic Sans', 25), command=start_game)
                    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 440,
                                         window=start_game_button, height=45, width=180)
                for i in range(len(player_names)):
                    canvas.create_text((s_width - menu_background_image.width()) / 2 + 158,
                                       title_image.height() + 35 + (i + 1) * 35,
                                       anchor="nw", text=player_names[i], font=('Comic Sans', 25))
            else:
                for i in range(len(old_player_names), len(player_names)):
                    canvas.create_text((s_width - menu_background_image.width()) / 2 + 158, title_image.height() + 35 + (i + 1) * 35,
                                       anchor="nw", text=player_names[i], font=('Comic Sans', 25))
            old_player_names = player_names
        canvas.update()
        sleep(0.1)
    game_screen(username)


def hosting_game_screen(code, username):
    screens.append((main_menu, username))
    global current_frame
    global started
    global client_socket
    global player_names
    global stop

    screen_frame = Frame(root)
    canvas = Canvas(screen_frame)
    canvas.pack(expand=True, fill=BOTH)
    canvas.create_image(0, 0, anchor="nw", image=background_image)
    canvas.create_image((s_width - title_image.width()) / 2, 0, anchor="nw", image=title_image)
    canvas.create_image((s_width - menu_background_image.width()) / 2, title_image.height() + 50, anchor="nw",
                        image=menu_background_image)
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 145, title_image.height() + 65, anchor="nw",
                       text='Players:', font=('Comic Sans', 25))
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 165, title_image.height() + 320, anchor="nw",
                       text='Code:', font=('Comic Sans', 25))
    canvas.create_text((s_width - menu_background_image.width()) / 2 + 158, title_image.height() + 360, anchor="nw",
                       text=code, font=('Comic Sans', 25))
    start_game_button = Button(canvas, text='Start Game', font=('Comic Sans', 25), command=start_game)
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 440,
                         window=start_game_button, height=45, width=180)
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
    player_names = server_input[3:].split('\t')
    print(started)
    if not started:
        update_players = threading.Thread(target=get_player_names, args=(client_socket,), daemon=True)
        update_players.start()
    while not started:
        if stop:
            return
        if old_player_names != player_names:
            if len(old_player_names) > len(player_names):
                canvas.create_image((s_width - menu_background_image.width()) / 2, title_image.height() + 50,
                                    anchor="nw",
                                    image=menu_background_image)
                canvas.create_text((s_width - menu_background_image.width()) / 2 + 145, title_image.height() + 65,
                                   anchor="nw",
                                   text='Players:', font=('Comic Sans', 25))
                canvas.create_text((s_width - menu_background_image.width()) / 2 + 165, title_image.height() + 320,
                                   anchor="nw",
                                   text='Code:', font=('Comic Sans', 25))
                canvas.create_text((s_width - menu_background_image.width()) / 2 + 158, title_image.height() + 360,
                                   anchor="nw",
                                   text=code, font=('Comic Sans', 25))
                start_game_button = Button(canvas, text='Start Game', font=('Comic Sans', 25), command=start_game)
                canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 440,
                                     window=start_game_button, height=45, width=180)
                for i in range(len(player_names)):
                    canvas.create_text((s_width - menu_background_image.width()) / 2 + 158,
                                       title_image.height() + 35 + (i + 1) * 35,
                                       anchor="nw", text=player_names[i], font=('Comic Sans', 25))
            else:
                for i in range(len(old_player_names), len(player_names)):
                    canvas.create_text((s_width - menu_background_image.width()) / 2 + 158, title_image.height() + 35 + (i + 1) * 35,
                                       anchor="nw", text=player_names[i], font=('Comic Sans', 25))
            old_player_names = player_names
        canvas.update()
        sleep(0.1)
    game_screen(username)

def join_lobby(join_code, username):
    code = client_socket.join_game(join_code)
    if code[0] == '1':
        join_game_screen(join_code, username)
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
    canvas.create_image(0, 0, anchor="nw", image=background_image)
    canvas.create_image((s_width - title_image.width()) / 2, 0, anchor="nw", image=title_image)
    canvas.create_image((s_width - menu_background_image.width()) / 2, title_image.height() + 50, anchor="nw",
                        image=menu_background_image)
    offset = 180 - (len(username) * 15)
    if offset < 50:
        offset = 50
    canvas.create_text((s_width - menu_background_image.width()) / 2 + offset, title_image.height() + 80, anchor="nw", text='Welcome ' + username, font=('Comic Sans', 25))
    host_lobby_button = Button(canvas, text='Host Game', font=('Comic Sans', 25),
                             command=lambda : host_game(username))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 150,
                         window=host_lobby_button, height=45, width=180)
    join_lobby_button = Button(canvas, text='Join Game', font=('Comic Sans', 25),
                             command=lambda: join_lobby(code.get(), username))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 220,
                         window=join_lobby_button, height=45, width=180)
    code_entry = Entry(canvas, textvariable=code, font=('Comic Sans', 25))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 270,
                         window=code_entry, height=40, width=240)


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
        print('confirmed')
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
    canvas.create_image(0, 0,anchor="nw", image=background_image)
    canvas.create_image((s_width - title_image.width())/2, 0, anchor="nw", image=title_image)
    canvas.create_image((s_width - menu_background_image.width()) / 2, title_image.height() + 50,anchor="nw", image=menu_background_image)

    canvas.create_text((s_width - menu_background_image.width()) / 2 + 54, title_image.height() + 180, anchor="nw", text='Enter Received Code:', font=('Comic Sans', 25))
    code_entry = Entry(canvas, textvariable=code, font=('Comic Sans', 25))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 250, window=code_entry, height=40, width=300)
    confirm_button = Button(canvas, text='Confirm Email', font=('Comic Sans', 25),
           command=lambda : confirm_email(code.get(), username, password))
    canvas.create_window((s_width - menu_background_image.width()) / 2 + 210, title_image.height() + 320, window=confirm_button, height=45, width=240)
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
    print(threading.activeCount())
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