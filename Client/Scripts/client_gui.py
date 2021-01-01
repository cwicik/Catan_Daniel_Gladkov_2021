from tkinter import *
from PIL import ImageTk, Image
from math import sin, cos, pi
import socket
import threading
import time
import json
from client import Client



root = Tk()

root.title("Catan")
# x = root.winfo_screenwidth()
# y = root.winfo_screenheight()
x = 960
y = 540
root.geometry("%dx%d" % (x,y))
#root.resizable(width=False, height=False)
# root.attributes("-fullscreen", True)


client_socket = None
current_frame = None
error = Label(current_frame)
error.place()

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


def loading(cycles, canvas):
    center = (canvas.winfo_screenwidth() / 2, canvas.winfo_screenheight() / 1.5)
    while True:
        print('bruh')
        try:
            cycle = next(cycles)
            for i in range(8):
                canvas.create_oval(center[0] + 30 * cos(i * pi / 4) - 10, center[1] + 30 * sin(i * pi / 4) - 10,
                                   center[0] + 30 * cos(i * pi / 4) + 10, center[1] + 30 * sin(i * pi / 4) + 10,
                                   fill=cycle[i], outline='')
            canvas.update()
            time.sleep(0.1)
        except:
            pass

def attempt_connection(start, client_socket, error, error_label):
    global connected
    while connected is not True:
        if start < time.time() - 4:
            error.set(connected)
            error_label.update()
        connected = client_socket.start()

def connect_to_server():
    global client_socket
    global current_frame
    global connected
    if current_frame is not None:
        current_frame.destroy()

    connecting_to_server = Frame(root)
    Label(connecting_to_server, text='Catan', font=('Comic Sans', 22), fg='Crimson').place(x=960)
    error = StringVar()
    canvas = Canvas(connecting_to_server, width=800, height=800)
    canvas.place(x=960, y=100)
    error_label = Label(connecting_to_server, textvariable=error, font=('Comic Sans', 22), fg='Red')
    error_label.place(x=400, y=400)
    current_frame = connecting_to_server
    current_frame.pack(expand=True, fill=BOTH)

    client_socket = Client('127.0.0.1', 1731)
    connected = client_socket.start()
    if connected is not True:
        cycles = loading_cycles()
        start = time.time()
        client_handler = threading.Thread(target=attempt_connection, args=(start, client_socket, error, error_label),daemon=True)
        client_handler.start()
    while connected is not True:
        try:
            cycle = next(cycles)
            for i in range(8):
                canvas.create_oval(100 + 30 * cos(i * pi / 4)- 10, 100 + 30 * sin(i * pi / 4)- 10,
                               100 + 30 * cos(i * pi / 4)+ 10, 100 + 30 * sin(i * pi / 4)+ 10,
                               fill=cycle[i], outline='')
            canvas.update()
            time.sleep(0.1)
        except:
            pass
    log_in_screen()


def register_screen():
    global current_frame
    error.configure(text="")
    if current_frame is not None:
        current_frame.destroy()
    username = StringVar()
    password = StringVar()
    email = StringVar()
    register_frame = Frame(root)
    Entry(register_frame, textvariable=username).pack()
    Entry(register_frame, show='*', textvariable=password).pack()
    Entry(register_frame, textvariable=email).pack()
    Button(register_frame, text='Register',command=lambda : register_user(username.get(), password.get(), email.get())).pack()

    current_frame = register_frame
    current_frame.pack(expand=True, fill=BOTH)

def log_in_screen():
    global current_frame
    error.configure(text="")
    if current_frame is not None:
        current_frame.destroy()
    username = StringVar()
    password = StringVar()
    log_in_frame = Frame(root)
    Entry(log_in_frame, textvariable=username).place(x=900, y=100)
    Entry(log_in_frame, show='*', textvariable=password).place(x=900, y=130)
    Button(log_in_frame, text='Log In', command=lambda : log_in_user(username.get(), password.get())).place(x=935, y=200)
    Button(log_in_frame, text='Create new account', command=register_screen).place(x=900, y=250)
    Label(log_in_frame, text='Username', font=('Comic Sans', 14)).place(x=400, y=400)
    Label(log_in_frame, text='Password', font=('Comic Sans', 14)).place(x=400, y=400)

    current_frame = log_in_frame
    current_frame.pack(expand=True, fill=BOTH)

def main_menu():
    global current_frame
    error.configure(text="")
    if current_frame is not None:
        current_frame.destroy()

    main_menu_frame = Frame(root, width=400, height=400)
    Label(main_menu_frame, text='Welcome To The Main Menu: ' + client_socket.get_username()).pack()

    current_frame = main_menu_frame
    current_frame.pack(expand=True, fill=BOTH)


def get_error(code):
    with open('../Json/error_messages.json') as file:
        return json.load(file)[code]

def confirm_email(code):
    pass

def confirm_email_screen():
    global current_frame
    error.configure(text="")
    if current_frame is not None:
        current_frame.destroy()

    code = StringVar()
    confirm_email_frame = Frame(root, width=400, height=400)
    Label(confirm_email_frame, text='Enter The Code You Got In The Email Here').pack()
    Entry(confirm_email_frame, textvariable=code).pack()
    Button(confirm_email_frame, text='Log In', command=lambda : confirm_email(code.get()).pack())

    current_frame = confirm_email_frame
    current_frame.pack()

def register_user(username, password, email):
    global current_frame
    # Hash password here
    #
    #
    #
    error.configure(text="")
    code = client_socket.register(username, password, email)
    if code[0] == '1':
        print('registered!')
        log_in_user(username, password)
    else:
        error.configure(text=get_error(code))



def log_in_user(username, password):
    print(threading.activeCount())
    code = client_socket.log_in(username, password)
    error.configure(text="")
    if code[0] == '1':
        print('logged in!')
        main_menu()
    else:
        print('error', code)
        error.configure(text=get_error(code))

def main():
    threading.Thread(target=connect_to_server, daemon=True).start()

    mainloop()


if __name__ == '__main__':
    main()