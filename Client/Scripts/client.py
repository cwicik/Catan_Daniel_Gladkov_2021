import socket
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

class Client:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = None
        self._private_key = None
        self.public_key = None

    def start(self):
        try:
            print('connecting to ip %s port %s' % (self.ip, self.port))
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.ip, self.port))
            self.generate_keys()
            self.server_socket.sendall(self.public_key.public_bytes(
                                    encoding=serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo))
            key = self.server_socket.recv(8192)
            self.public_key_server = serialization.load_pem_public_key(key,
                                                                      backend=default_backend())
            print('connected to server')
            return True
        except socket.error as e:
            return e

    def register(self, username, password, email):
        self.server_socket.sendall(self.encrypt_message(('rgs' + username + '\t' + password + '\t' + email)))
        code = self.decrypt_message(self.server_socket.recv(8192))
        if code[0] == '1':
            self.server_socket.sendall(self.encrypt_message(('cnf' + username + '\t' + password + '\t' + email)))
            return self.decrypt_message(self.server_socket.recv(8192))
        else:
            return code

    def log_in(self, username, password):
        self.server_socket.sendall(self.encrypt_message(('lgn' + username + '\t' + password)))
        return self.decrypt_message(self.server_socket.recv(8192))

    def get_username(self):
        self.server_socket.sendall(self.encrypt_message('usr'))
        return self.decrypt_message(self.server_socket.recv(8192))

    def confirm_code(self, code):
        self.server_socket.sendall(self.encrypt_message(('cod' + code)))
        return self.decrypt_message(self.server_socket.recv(8192))

    def cancel(self):
        self.server_socket.sendall(self.encrypt_message('cnl'))
        self.decrypt_message(self.server_socket.recv(8192))

    def host_game(self):
        self.server_socket.sendall(self.encrypt_message('hst'))
        return self.decrypt_message(self.server_socket.recv(8192))

    def join_game(self, code):
        self.server_socket.sendall(self.encrypt_message(('jin' + code)))
        return self.decrypt_message(self.server_socket.recv(8192))

    def get_players(self, code):
        self.server_socket.sendall(self.encrypt_message(('plr' + code)))
        return self.decrypt_message(self.server_socket.recv(8192))

    def get_player_names(self):
        return self.decrypt_message(self.server_socket.recv(8192))

    def leave_lobby(self):
        self.server_socket.sendall(self.encrypt_message('liv'))

    def log_off(self):
        self.server_socket.sendall(self.encrypt_message('lof'))

    def start_game(self):
        self.server_socket.sendall(self.encrypt_message('srt'))

    def get_board(self):
        return self.decrypt_message(self.server_socket.recv(8192))

    def roll_dice(self):
        self.server_socket.sendall(self.encrypt_message('rol'))

    def build_settlement(self, cords):
        self.server_socket.sendall(self.encrypt_message('bst' + str(cords)))

    def build_road(self, cords):
        self.server_socket.sendall(self.encrypt_message('bro' + str(cords)))

    def finish_turn(self):
        self.server_socket.sendall(self.encrypt_message('fns'))

    def stop(self):
        self.server_socket.sendall(self.encrypt_message('stp'))

    def generate_keys(self):
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self._private_key.public_key()

    def encrypt_message(self, message):
        if type(message) != "bytes":
            message = message.encode()
        return self.public_key_server.encrypt(message,
                                              padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                           algorithm=hashes.SHA256(),
                                                           label=None))

    def decrypt_message(self, encrypted_message):
        return self._private_key.decrypt(encrypted_message,
                                         padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                      algorithm=hashes.SHA256(),
                                                      label=None)).decode()