import socket


class Client:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = None

    def start(self):
        try:
            print('connecting to ip %s port %s' % (self.ip, self.port))
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.ip, self.port))
            print('connected to server')
            return True
        except socket.error as e:
            return e

    def send(self, x):
        self.server_socket.sendall(x.encode())


    def register(self, username, password, email):
        self.server_socket.sendall(('rgs' + username + '\t' + password + '\t' + email).encode())
        return self.server_socket.recv(3).decode()

    def log_in(self, username, password):
        self.server_socket.sendall(('lgn' + username + '\t' + password).encode())
        return self.server_socket.recv(3).decode()

    def get_username(self):
        self.server_socket.sendall('usr'.encode())
        return self.server_socket.recv(16).decode()