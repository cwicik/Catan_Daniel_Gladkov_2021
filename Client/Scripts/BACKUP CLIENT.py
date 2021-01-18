from tkinter import *
from PIL import ImageTk, Image
import socket
import threading
import time
from client import Client


root = Tk()

root.title("Catan")
# x = root.winfo_screenwidth()
# y = root.winfo_screenheight() 
x = 400
y = 400
root.geometry("%dx%d" % (x,y))
# root.attributes("-fullscreen", True)


client_socket = None





   # register_screen = Frame(root, width=400, height=400, bg='blue')

def connect_to_server():
    global client_socket

    connecting_to_server = Frame(root, width=400, height=400)
    Label(connecting_to_server, text='Catan', font=('Comic Sans', 22), fg='Crimson').pack()

    connecting_to_server.pack()
    client_socket = Client('127.0.0.1', 1731)
    start = time.time()
    connected = client_socket.start()
    while connected is not True:
        connected = client_socket.start()
        # if time.time() > start + 4:
           # active_message_codes.append('200')
        time.sleep(1)
    connecting_to_server.destroy()
    log_in_screen()




def log_in_screen():
    username = StringVar()
    password = StringVar()
    log_in_screen = Frame(root, width=400, height=400)
    Entry(log_in_screen, textvariable=username).pack()
    Entry(log_in_screen, textvariable=password).pack()
    Button(log_in_screen, text='Log In', command=lambda : log_in_user(username, password)).pack()
    Button(log_in_screen, text='Register', command=register_user).pack()

    log_in_screen.pack()



def check_username(username):
    if 4 < len(username) < 16:
        return True
    return False


def check_password(password):
    digit = False
    for character in password:
        if character.isdigit():
            digit = True
   # if password_must_contain in active_message_codes:
        # active_message_codes.remove(password_must_contain)
    if 6 < len(password) < 32 and not password.islower() and not password.isupper() and digit:
        return True
    return False


def register_user(username, password):
    usr = check_username(username)
    psw = check_password(password)
    if usr and psw:
        # Hash password here
        #
        #
        #
        if client_socket.register(username, password):
            # if username_already_taken in active_message_codes:
                # active_message_codes.remove(username_already_taken)
            print('registered!')
            # main_menu()
        else:
            pass
            # active_message_codes.append(username_already_taken)


def log_in_user(username, password):
    username = username.get()
    password = password.get()
    print(username)
    print(password)

    if client_socket.log_in(username, password)[0] == '1':
        # if incorrect_log_in_info in active_message_codes:
             # active_message_codes.remove(incorrect_log_in_info)
        print('logged in!')
        # main_menu()
    else:
        pass
        # active_message_codes.append(incorrect_log_in_info)
    print('loggin ended')

def main():
    threading.Thread(target=connect_to_server).start()

    mainloop()

if __name__ == '__main__':
    main()