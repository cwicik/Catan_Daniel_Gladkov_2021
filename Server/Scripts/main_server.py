import socket
from pymongo import MongoClient
import threading
from pyisemail import is_email
from random import randint
from time import sleep
import smtplib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

class UserConnection:

    def __init__(self, socket, cluster, operations, check_connection):
        self.socket = socket
        self.public_key_user = None
        self.cluster = cluster
        self.operations = operations
        self.check_connection = check_connection
        self.user = None
        self._private_key = None
        self.public_key = None

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
        return self.public_key_user.encrypt(message,
                                       padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                    algorithm=hashes.SHA256(),
                                                    label=None))

    def decrypt_message(self, encrypted_message):
        return self._private_key.decrypt(encrypted_message,
                                         padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                      algorithm=hashes.SHA256(),
                                                      label=None)).decode()

    def get_socket(self):
        return self.socket

    def get_username(self):
        return self.user

    def set_username(self, username):
        self.user = username

    def handle_client(self):
        try:
            self.generate_keys()
            key = self.socket.recv(8192)
            self.public_key_user = serialization.load_pem_public_key(key,
                                                                      backend=default_backend())
            self.socket.sendall(self.public_key.public_bytes(
                                encoding=serialization.Encoding.PEM,
                                format=serialization.PublicFormat.SubjectPublicKeyInfo))

            while True:
                request = self.decrypt_message(self.socket.recv(8192))
                print(request)
                self.check_connection()
                print('command:', request[:3])
                try:
                    self.socket.sendall(self.encrypt_message(self.operations[request[:3]](request[3:], self)))
                except BaseException as e:
                    self.socket.sendall(self.encrypt_message('300'))
                    print('error:' , e)
                if request != '':
                    print('Received {}'.format(request))
        except socket.error as e:
            print(e)
            print('shutting down')
            self.socket.close()
            self.socket = None

class Server:

    def __init__(self, ip, port, mongo_conection):
        self.ip = ip
        self.port = port
        self.socket = None
        self.operations = None
        self.users = []
        self.cluster = MongoClient(mongo_conection)['Catan']


    def start(self):
        try:
            print('server starts up on ip %s port %s' % (self.ip, self.port))
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.ip, self.port))
            self.socket.listen(1)
            self.operations = {'rgs': self.register_user,
                               'lgn': self.log_in_user,
                               'usr': self.get_username}
            while True:
                client_socket, client_address = self.socket.accept()
                self.handle_client(client_socket)

        except socket.error as e:
            print(e)


    def handle_client(self, client_socket):
        print("Handling Client Number", len(self.users))
        user = UserConnection(client_socket, self.cluster, self.operations, self.check_online_users)
        self.users.append(user)
        client_handler = threading.Thread(target=user.handle_client, args=())
        client_handler.start()

    @staticmethod
    def is_username_valid(username):
        return 4 < len(username) < 16

    @staticmethod
    def is_password_valid(password):
        digit = False
        for character in password:
            if character.isdigit():
                digit = True
        return 6 < len(password) < 32 and not password.islower() and not password.isupper() and digit

    @staticmethod
    def is_email_valid(email):
        return is_email(email)

    def register_user(self, *args):
        register_info = args[0]
        username = register_info[:register_info.find('\t')]
        password = register_info[register_info.find('\t') + 1: register_info.rfind('\t')]
        email = register_info[register_info.rfind('\t') + 1:]
        if not self.is_password_valid(password):
            return '202'
        if self.is_email_valid(email) is False:
            return '205'
        if not self.is_username_valid(username):
            return '201'
        if self.cluster['Users'].find_one({'username': username}) is None:
            self.cluster['Users'].insert_one({'username': username, 'password': password, 'email': email})
            return '101'
        return '204'


    def check_online_users(self):
        usernames = []
        for user in self.users:
            if user.socket == None:
                self.users.remove(user)
            else:
                usernames.append(user.get_username())
        return usernames

    def log_in_user(self, *args):
        log_in_info = args[0]
        user = args[1]
        username = log_in_info[:log_in_info.find('\t')]
        password = log_in_info[log_in_info.find('\t') + 1:]
        print('log in username:', username)
        print('log in password:', password)
        try:
            print('user:', self.cluster['Users'].find_one({'username': username, 'password': password}))
        except BaseException as e:
            print(e)
        if self.cluster['Users'].find_one({'username': username, 'password': password}) is not None\
                  and username not in self.check_online_users():
            self.confirm_log_in(user, str(randint(100000, 999999)), username, self.cluster['Users'].find_one({'username': username, 'password': password})['email'])
            return '102'
        return '203'

    @staticmethod
    def get_username(*args):
        return args[1].get_username()

    def send_email(self, email, code):
        print('sending email...')
        code_of_gmail = "cobhzmweebeajsfz"

        sender = "daniel.gladkov@gmail.com"
        receivers = [email]
        message = """From: From Person <daniel.gladkov@gmail.com>
        To: {}
        Subject: Confirmation Code For Catan

        Please enter the following code to confirm your email: {}
        If this 
        """.format(email, code)

        try:
            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpObj.starttls()
            smtpObj.login("daniel.gladkov@gmail.com", code_of_gmail)
            smtpObj.sendmail(sender, receivers, message)
            print("Successfully sent email")
        except BaseException as e:
            print(e)

    def confirm_log_in(self, *args):
        print('confirming log in...')
        user = args[0]
        code = args[1]
        username = args[2]
        email = args[3]
        self.send_email(email, code)
        input = user.get_socket().recv(1024).decode()
        # Input doesnt work atm
        count = 0
        while code != input:
            count += 1
            if count == 3:
                sleep(60)
            elif count == 4:
                sleep(120)
            elif count == 5:
                sleep(180)
            elif count >= 6:
                sleep(300)
            input = user.get_socket().recv(1024).decode()
        user.set_username(username)
        return '103'

if __name__ == '__main__':
    pymongo = "mongodb+srv://cwicik:yB5^V7Q4Es2Mc^@server-database.nqwtm.mongodb.net/Catan?retryWrites=true&w=majority"
    server = Server('0.0.0.0', 1731, pymongo)
    server.start()
