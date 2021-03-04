import socket
from pymongo import MongoClient
import threading
from pyisemail import is_email
from random import randint, shuffle
import smtplib
import bcrypt
from time import time, sleep
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization



class Road:
    def __init__(self, neighboring_roads):
        self.owner = None
        self.building = '0'  # 0 = none, 1 = road
        self.can_build = []
        self.neighboring_roads = neighboring_roads

    def compact(self):
        if self.building != '0':
            return self.owner + '\t' + self.building
        return ""

class Building:
    def __init__(self, neighboring_tiles):
        self.owner = None
        self.building = '0'  # 0 = none, 1 = settlement, 2 = city
        self.neighboring_tiles = neighboring_tiles

    def get_owner(self):
        return self.owner

    def set_owner(self, owner):
        self.owner = owner

    def get_resources(self):
        resources = []
        for tile in self.neighboring_tiles:
            resources.append((tile.get_type(), tile.get_number()))
        return resources

    def compact(self):
        if self.building != '0':
            return self.owner + '\t' + str(self.building)
        return ""


class Tile:
    def __init__(self, type, number):
        self.type = type
        self.number = number

    def get_type(self):
        return self.type

    def get_number(self):
        return self.number

    def compact(self):
        return str(self.type) + '\t' + str(self.number)


class Board:
    def __init__(self):
        self.tiles = [None for _ in range(154)]
        self.nodes = [None for _ in range(187)]
        self.edges = [None for _ in range(177)]

        self.used_tiles = (0x11, 0x13, 0x15, 0x31, 0x51,
                           0x33, 0x35, 0x37, 0x53, 0x73,
                           0x55, 0x57, 0x59, 0x75, 0x95,
                           0x77, 0x79, 0x97, 0x99)

        self.used_nodes = (0x1, 0x3, 0x5, 0x10, 0x12, 0x14, 0x16,
                           0x21, 0x23, 0x25, 0x27,
                           0x30, 0x32, 0x34, 0x36, 0x38,
                           0x41, 0x43, 0x45, 0x47, 0x49,
                           0x50, 0x52, 0x54, 0x56, 0x58, 0x5A,
                           0x61, 0x63, 0x65, 0x67, 0x69, 0x6B,
                           0x72, 0x74, 0x76, 0x78, 0x7A,
                           0x83, 0x85, 0x87, 0x89, 0x8B,
                           0x94, 0x96, 0x98, 0x9A,
                           0xA5, 0xA7, 0xA9, 0xAB,
                           0xB6, 0xB8, 0xBA)

        self.used_edges = (0x0, 0x2, 0x3, 0x4, 0x5,
                           0x10, 0x20, 0x30, 0x40, 0x50,
                           0x12, 0x14, 0x16, 0x21, 0x41, 0x61,
                           0x22, 0x23, 0x24, 0x25, 0x26, 0x27,
                           0x32, 0x42, 0x52, 0x62, 0x72,
                           0x32, 0x36, 0x38, 0x43, 0x63, 0x83,
                           0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x54, 0x64, 0x74, 0x84, 0x94,
                           0x56, 0x58, 0x5A, 0x65, 0x85, 0xA5,
                           0x66, 0x67, 0x68, 0x69, 0x6A, 0x76, 0x86, 0x96, 0xA6,
                           0x78, 0x7A, 0x87, 0xA7,
                           0x88, 0x89, 0x8A, 0x98, 0xA8,
                           0x9A, 0xA9, 0xAA)

        self.initialize_board()

    def initialize_board(self):
        types = [0, 0, 0, 0,
                 1, 1, 1, 1,
                 2, 2, 2, 2,
                 3, 3, 3,
                 4, 4, 4]
        shuffle(types)

        numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        shuffle(numbers)

        desert_tile = randint(0, 18)

        for i in range(len(self.used_tiles)):
            if i == desert_tile:
                self.tiles[self.used_tiles[i]] = Tile(5, " ")
            else:
                self.tiles[self.used_tiles[i]] = Tile(types.pop(), numbers.pop())

        for num in self.used_edges:
            self.edges[num] = Road(0)

        for num in self.used_nodes:
            _tile_even_offsets = (-0x10, 0x10, -0x12)
            _tile_odd_offsets = (-0x01, 0x01, -0x21)
            tiles = []
            if num % 2:
                _tile_node_offsets = _tile_even_offsets
            else:
                _tile_node_offsets = _tile_odd_offsets
            for offset in _tile_node_offsets:
                try:
                    tile = self.tiles[num + offset]
                    if tile is not None:
                        tiles.append(tile)
                except IndexError:
                    pass
            self.nodes[num] = Building(tiles)

    def get_tiles(self):
        tiles = ""
        for index in self.used_tiles:
            tiles += '\t' + self.tiles[index].compact()
        return tiles

    def get_nodes(self):
        nodes = ""
        for index in self.used_nodes:
            node = self.nodes[index].compact()
            if node != "":
                nodes += '\t' + node
        return nodes

    def get_edges(self):
        edges = ""
        for index in self.used_edges:
            edge = self.edges[index].compact()
            if edge != "":
                edges += '\t' + edge
        return edges

    def get_board(self):
        return self.get_tiles() + '\tn' +self.get_nodes() + '\te' + self.get_edges()


class Player:
    resources_dict = {0: 'sheep',
                      1: 'wood',
                      2: 'wheat',
                      3: 'brick',
                      4: 'stone',}
    color_dict = {0: 'red',
                  1: 'green',
                  2: 'blue',
                  3: 'white'}
    def __init__(self, user, color):
        self.user = user
        self.color = color
        self.points = 0
        self.resources = [1, 1, 1, 1, 1]
        self.gains = ([],[],[],[],
                      [],[],[],[],
                      [],[],[],[],[])

    def gain(self, num):
        for resource in self.gains[num]:
            self.resources[resource] += 1

    def get_gains(self):
        return self.gains

    def can_afford(self, building):
        if building == 1: # settlement
            return self.resources[0] >= 1 and self.resources[1] >= 1 and self.resources[2] >= 1 and self.resources[3] >= 1
        if building == 2:  # city
            return self.resources[2] >= 2 and self.resources[4] >= 3
        if building == 3:  # road
            return self.resources[1] >= 1 and self.resources[3] >= 1

    def get_resources(self):
        return self.resources

    def get_user(self):
        return self.user

    def gain_point(self):
        self.points += 1

    def get_points(self):
        return self.points

class GameLobby:
    def __init__(self, host):
        self.players = [Player(host, 0)]
        host.set_lobby(self)
        self.board = Board()
        self.current_player = None
        self.started = False
        self.starting_game = True

    def add_player(self, user):
        if len(self.players) > 3:
            return '211'
        self.players.append(Player(user, len(self.players)))
        user.set_lobby(self)
        for player in self.players:
            if player.get_user() != user:
                player.get_user().send_players(self.players)
        return '105'

    def remove_player(self, user):
        to_delete = -1
        for i in range(len(self.players)):
            if self.players[i].get_user() == user:
                to_delete = i
        if to_delete > -1:
            del self.players[to_delete]
        for player in self.players:
            player.get_user().send_players(self.players)

    def get_players(self):
        return self.players

    def send_board(self):
        for player in self.players:
            info = 'brd' + '\t' + str(player.get_points())
            for resource in player.get_resources():
                info += '\t' + str(resource)
            info += self.board.get_board()
            player.get_user().send_board(info)

    """
    to check nodes near a given road:
    check positions at:
    self, +1, +10, +11  
    """

    """
    to check roads near a given road
    check positions at:
    -10, -1, -11, self
    """

    """
    to check roads near other roads
    +- 10, +- 1
    """

    def roll_dice(self):
        roll = randint(2,12)
        for player in self.players:
            player.gain(roll)

    def build_settlement(self, player, cords):
        building_plot = self.board.get_nodes()[cords]
        if building_plot.get_owner() is not None:
            return '400'
        if not self.starting_game:
            if self.can_build_settlement(player, cords):
                if player.can_afford(1):
                    player_resources = player.get_resources()
                    player_resources[0] -= 1
                    player_resources[1] -= 1
                    player_resources[2] -= 1
                    player_resources[3] -= 1

                return '402'
            return '401'
        building_plot.set_owner(player)
        building_plot.set_building(1)
        new_resources = building_plot.get_resources()
        player_gains = player.get_gains()
        for resource in new_resources:
            player_gains[resource[1]].append(resource[0])
        return '500'

    def can_build_settlement(self, player, cords):
        _node_to_edge_offsets = (-0x10, -1, -0x11, 0)
        _edge_to_edge_offsets = (-0x10, -1, 0x10, 1)

        edges = self.board.get_edges()
        for node_offset in _node_to_edge_offsets:
            try:
                if edges[cords + node_offset] is not None:
                    if edges[cords + node_offset].get_owner() == player:
                        for edge_offset in _edge_to_edge_offsets:
                            if edges[cords + node_offset + edge_offset] is not None and edges[cords + node_offset+ edge_offset].get_owner() == player:
                                return True
            except IndexError:
                pass
        return False

    def start_game(self):
        for player in self.players:
            player.get_user().send_starting()
        print('yes')
        while True:
            #pre-game

            if self.starting_game:
            #game
                self.send_board()
                self.starting_game = False
                pass
            if self.started:
                pass


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
        self.lobby = None

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

    def set_lobby(self, lobby):
        self.lobby = lobby

    def get_lobby(self):
        return self.lobby

    def get_socket(self):
        return self.socket

    def send_players(self, players):
        players_str = 'plr'
        for player in players:
            players_str += '\t' + player.get_user().get_username()
        self.socket.sendall(self.encrypt_message(players_str))

    def send_board(self, board):
        print(board)
        self.socket.sendall(self.encrypt_message(board))

    def send_starting(self):
        self.socket.sendall(self.encrypt_message('srt'))

    def get_code(self):
        return self.decrypt_message(self.socket.recv(8192))

    def send_confirm(self):
        self.socket.sendall(self.encrypt_message('104'))

    def wrong_code(self, num):
        if num == 0:
            self.socket.sendall(self.encrypt_message('208'))
        else:
            self.socket.sendall(self.encrypt_message('210'))

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
                self.check_connection()
                print('Starting {}'.format(request))
                try:
                    self.socket.sendall(self.encrypt_message(self.operations[request[:3]](request[3:], self)))
                except BaseException as e:
                    self.socket.sendall(self.encrypt_message('300'))
                    print('error:' , e)
                if request != '':
                    print('Ending {}'.format(request))
        except BaseException as e:
            print(e)
            print('shutting down')
            try:
                self.operations['liv'](request[3:], self)
            except:
                pass
            self.socket.close()
            self.user = None
            self.socket = None


class Server:

    def __init__(self, ip, port, mongo_conection):
        self.ip = ip
        self.port = port
        self.socket = None
        self.operations = None
        self.users = []
        self.cluster = MongoClient(mongo_conection)['Catan']
        self.smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        try:
            self.smtpObj.starttls()
            self.smtpObj.login("catanonlinegame@gmail.com", "jksukzezlqomtvdy")
        except BaseException as e:
            print("Email Error:", e)



    def start(self):
        try:
            print('server starts up on ip %s port %s' % (self.ip, self.port))
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.ip, self.port))
            self.socket.listen(1)
            self.operations = {'rgs': self.register_user,
                               'lgn': self.log_in_user,
                               'usr': self.get_username,
                               'cnf': self.confirm_log_in,
                               'lof': self.log_off,
                               'hst': self.host_game,
                               'jin': self.join_game,
                               'liv': self.leave_game,
                               'plr': self.get_players,
                               'srt': self.start_game}
            self.codes = ['111111', '222222'] # all lobby codes available
            self.games = {}
            while True:
                client_socket, client_address = self.socket.accept()
                self.handle_client(client_socket)

        except socket.error as e:
            print(e)

    def get_key(self, val):
        for key, value in self.games.items():
            if val == value:
                return key

        return None

    def host_game(self, *args):
        try:
            code = self.codes.pop()
            self.games[code] = GameLobby(args[1])
            return '105' + code
        except IndexError:
            return '213'

    def leave_game(self, *args):
        user =  args[1]
        lobby = user.get_lobby()
        lobby.remove_player(user)
        user.set_lobby(None)
        if len(lobby.get_players()) == 0:
            code = self.get_key(lobby)
            self.codes.append(code)
            del self.games[code]
        return '1000'

    def join_game(self, *args):
        try:
            return self.games[args[0]].add_player(args[1])
        except KeyError:
            return '212'

    @staticmethod
    def start_game(*args):
        args[1].get_lobby().start_game()

    def log_off(self, *args):
        user =  args[1]
        del self.users[self.users.index(user)]
        user.set_username(None)

    def get_players(self, *args):
        players = self.games[args[0]].get_players()
        str = 'plr'
        for player in players:
            str += '\t' + player.get_user().get_username()
        return str

    def handle_client(self, client_socket):
        print("Handling Client Number", len(self.users))
        user = UserConnection(client_socket, self.cluster, self.operations, self.check_online_users)
        self.users.append(user)
        client_handler = threading.Thread(target=user.handle_client, args=())
        client_handler.start()

    @staticmethod
    def is_username_valid(username):
        return 4 < len(username) < 13

    @staticmethod
    def is_password_valid(password):
        digit = False
        letter = False
        for character in password:
            if character.isdigit():
                digit = True
            if character.isalpha():
                letter = True

        return digit and letter and 6 < len(password) < 32 and not password.islower() and not password.isupper()

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
            return '103'
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
        if password == '' or username == '':
            return '203'
        if not self.is_password_valid(password) or not self.is_username_valid(username):
            return '203'
        if self.cluster['Users'].find_one({'username': username}) is not None:
            stored_hash = self.cluster['Users'].find_one({'username': username})['password']
            if bcrypt.hashpw(password.encode(), stored_hash) == stored_hash:
                if username in self.check_online_users():
                    return '209'
            user.set_username(username)
            return '102'
        return '203'

    @staticmethod
    def get_username(*args):
        return args[1].get_username()

    def send_email(self, email, code):
        print('sending email...')
        print('code', code)
        sender = "catanonlinegame@gmail.com"
        receiver = email
        message = """From: Catan Game <catanonlinegame@gmail.com>\n\
To: {}\n\
Subject: Confirmation Code For Catan\n\

Please enter the following code to confirm your email: {}\n\
If you haven't expected this email, please ignore it.""".format(email, code)

        try:
            self.smtpObj.sendmail(sender, receiver, message)
            print("Successfully sent email")
        except BaseException as e:
            print(e)

    def confirm_log_in(self, *args):
        print('confirming log in...')
        register_info = args[0]
        username = register_info[:register_info.find('\t')]
        password = register_info[register_info.find('\t') + 1: register_info.rfind('\t')]
        email = register_info[register_info.rfind('\t') + 1:]
        user = args[1]
        code = str(randint(100000, 999999))
        self.send_email(email, code)
        user.send_confirm()
        input = user.get_code()
        count = 0
        while code != input[3:]:
            if input[:3] != 'cod':
                return '207'
            count += 1
            if count > 3:
                start = time()
                print(time())
                while start > time() - 60:
                    user.wrong_code(1)
                    input = user.get_code()
            else:
                user.wrong_code(0)
                input = user.get_code()
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.cluster['Users'].insert_one({'username': username, 'password': password, 'email': email})
        return '101'

if __name__ == '__main__':
    pymongo = "mongodb+srv://cwicik:yB5^V7Q4Es2Mc^@server-database.nqwtm.mongodb.net/Catan?retryWrites=true&w=majority"
    server = Server('0.0.0.0', 1731, pymongo)
    server.start()
