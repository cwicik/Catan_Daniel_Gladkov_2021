"""
Student Name: Daniel Gladkov
Date: 21/5/2021
"""

import socket

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


class Client:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = None
        self._private_key = None
        self.public_key = None
        self.public_key_server = None

    def start(self):
        try:
            print('Connecting To IP %s Port %s' % (self.ip, self.port))
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.ip, self.port))
            self.generate_keys()
            self.server_socket.sendall(self.public_key.public_bytes(
                                    encoding=serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo))
            key = self.server_socket.recv(8192)
            self.public_key_server = serialization.load_pem_public_key(key, backend=default_backend())
            print('Connected To Server Successfully')
            return True
        except socket.error:
            return False

    def register(self, username, password, email):
        if len(username) > 12:
            return '201'
        if len(password) > 32:
            return '202'
        if len(email) > 32:
            return '205'
        self.server_socket.sendall(self.encrypt_message(('rgs' + username + '\t' + password + '\t' + email)))
        code = self.decrypt_message(self.server_socket.recv(8192))
        if code[0] == '1':
            self.server_socket.sendall(self.encrypt_message(('cnf' + username + '\t' + password + '\t' + email)))
            return self.decrypt_message(self.server_socket.recv(8192))
        else:
            return code

    def log_in(self, username, password):
        if len(username) > 12:
            return '201'
        if len(password) > 32:
            return '202'
        self.server_socket.sendall(self.encrypt_message(('lgn' + username + '\t' + password)))
        return self.decrypt_message(self.server_socket.recv(8192))

    def get_username(self):
        self.server_socket.sendall(self.encrypt_message('usr'))
        return self.decrypt_message(self.server_socket.recv(8192))

    def confirm_code(self, code):
        if len(code) > 6:
            return '208'
        self.server_socket.sendall(self.encrypt_message(('cod' + code)))
        return self.decrypt_message(self.server_socket.recv(8192))

    def cancel(self):
        self.server_socket.sendall(self.encrypt_message('cnl'))
        self.decrypt_message(self.server_socket.recv(8192))

    def host_game(self):
        self.server_socket.sendall(self.encrypt_message('hst'))
        return self.decrypt_message(self.server_socket.recv(8192))

    def join_game(self, code):
        if len(code) > 6:
            return '212'
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
        self.server_socket.sendall(self.encrypt_message('nod' + str(cords)))

    def build_road(self, cords):
        self.server_socket.sendall(self.encrypt_message('edg' + str(cords)))

    def finish_turn(self):
        self.server_socket.sendall(self.encrypt_message('fns'))

    def stop(self):
        self.server_socket.sendall(self.encrypt_message('stp'))

    def start_trade(self): # Trade Info
        self.server_socket.sendall(self.encrypt_message('tri'))

    def offer_trade(self, trade_info): # Trade Offer
        self.server_socket.sendall(self.encrypt_message('tro' + trade_info))

    def accept_offer(self): # Confirm Trade
        self.server_socket.sendall(self.encrypt_message('acp'))

    def decline_offer(self): # Confirm Trade
        self.server_socket.sendall(self.encrypt_message('dcl'))

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

    def quit(self):
        self.server_socket.close()