"""
Student Name: Daniel Gladkov
Date: 21/5/2021
"""

#Install all dependencies
import subprocess
print('Installing dependencies...')
subprocess.call(['Install_dependencies_server.bat'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
print('All dependencies installed!')

import socket
import threading

from smtplib import SMTP, SMTPException
from re import search, compile
from bcrypt import hashpw, gensalt
from random import randint, shuffle
from time import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from pyisemail import is_email
from pymongo import MongoClient



class Road:
    """
       A class used to represent a Road in the board.

       Attributes
       ----------
       owner : Player object
           the player that owns the road, if no player owns the road, it is set to None

       Methods
       -------
       get_owner()
           returns the owner of the Road

       set_owner(owner)
           receives an owner and sets it as the current owner of the Road
    """

    def __init__(self):
        """Creates a Road object without an owner."""
        self.owner = None

    def get_owner(self):
        """Return the Road owner."""
        return self.owner

    def set_owner(self, owner):
        """Changes the Road owner to the received one."""
        self.owner = owner


class Settlement:
    """
       A class used to represent a Settlement in the board.

       Attributes
       ----------
       owner : Player object
           the player that owns the road, if no player owns the road, it is set to None

       resources : Array of Tuples
                  an array representing all adjacent tiles to the Settlement, which will yield resources to the owner
       Methods
       -------
       get_owner()
           returns the owner of the Settlement

       set_owner(owner)
           receives an owner and sets it as the current owner of the Settlement

       get_resources()
            return the Array of resources
    """

    def __init__(self, neighboring_tiles):
        """Creates a Settlement without an owner and with the resources it borders."""
        self.owner = None
        self.resources = []
        for tile in neighboring_tiles:
            self.resources.append((tile.get_resource(), tile.get_number()))

    def get_owner(self):
        """Returns the Settlement owner."""
        return self.owner

    def set_owner(self, owner):
        """Changes the Settlement owner to the received one."""
        self.owner = owner

    def get_resources(self):
        """Returns the Settlement resources."""
        return self.resources


class Tile:
    """
       A class used to represent a Resource Tile in the board.

       Attributes
       ----------
       resource : Integer
            represents the resource type the Tile is holding

       number : Integer
            the number that needs to be rolled in order for the Tile to yield its resource

       Methods
       -------
       get_resource()
           returns the resource type of the Tile

       get_number()
           returns the number of the Tile

       compact()
            return a string describing the Tile
    """

    def __init__(self, resource, number):
        """Creates a Tile with given resource type and number."""
        self.resource = resource
        self.number = number

    def get_resource(self):
        """Returns the Tile resource type."""
        return self.resource

    def get_number(self):
        """Returns the Tile number."""
        return self.number

    def compact(self):
        """Returns a compacted string version which represents the Tile."""
        return str(self.resource) + '\t' + str(self.number)


class Board:
    """
       A class used to represent the Board.
       In order to calculate easily the neighbors of each tile/node/edge to each other I am using a hexadecimal
       representation: https://github.com/rosshamish/hexgrid
       which simplifies the finding, but is heavier on the memory (most of the Array is None)
       Attributes
       ----------
       tiles : Array of Tile objects
            an array of the tiles in the Board, most places are None

       nodes : Array of Settlement objects
            an array of the nodes in the Board, most places are None

       edges : Array of Road objects
            an array of the edges in the Board, most places are None

       used_tiles : Array of Integer
            an array of indexes that are being used by the Board for the Tiles

       used_nodes : Array of Integer
            an array of indexes that are being used by the Board for the Settlements

       used_edges : Array of Integer
            an array of indexes that are being used by the Board for the Roads

       Methods
       -------
       initialize_board()
           creates all objects (Tiles, Roads and Settlements) and fills them into the corresponding Array

       get_tiles()
           returns a string of all Tiles after they are compacted

       get_nodes()
           returns the nodes Array

      get_edges()
           returns the edges Array
    """

    used_tiles = (0x15, 0x13, 0x11, 0x31, 0x51,
                  0x73, 0x95, 0x97, 0x99, 0x79,
                  0x59, 0x37, 0x35, 0x33, 0x53,
                  0x75, 0x77, 0x57, 0x55)

    used_nodes = (0x1, 0x3, 0x5, 0x10, 0x12, 0x14, 0x16,
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

    used_edges = (0x0, 0x1, 0x2, 0x3, 0x4, 0x5,
                  0x10, 0x12, 0x14, 0x16,
                  0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27,
                  0x30, 0x32, 0x34, 0x36, 0x38,
                  0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49,
                  0x50, 0x52, 0x54, 0x56, 0x58, 0x5A,
                  0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A,
                  0x72, 0x74, 0x76, 0x78, 0x7A,
                  0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8A,
                  0x94, 0x96, 0x98, 0x9A,
                  0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA)

    def __init__(self):
        """Creates the Board with all initialized Arrays that represent the Board pieces."""
        self.tiles = [None for _ in range(154)]
        self.nodes = [None for _ in range(187)]
        self.edges = [None for _ in range(177)]

        self.initialize_board()

    def initialize_board(self):
        """Fills the Board in all of the Arrays with objects."""
        types = [1, 2, 0, 4,
                 1, 0, 1, 3,
                 2, 0, 4, 2,
                 2, 3, 1,
                 4, 0, 3]
        shuffle(types)

        numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        shuffle(numbers)

        desert_tile = randint(0, 18)

        for i in range(len(Board.used_tiles)):
            if i == desert_tile:
                self.tiles[Board.used_tiles[i]] = Tile(5, 0)
            else:
                self.tiles[Board.used_tiles[i]] = Tile(types.pop(), numbers.pop())

        for num in Board.used_edges:
            self.edges[num] = Road()

        for num in Board.used_nodes:
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
            self.nodes[num] = Settlement(tiles)

    def get_tiles(self):
        """Returns a string of all Tiles in a compacted form."""
        tiles = ""
        for index in Board.used_tiles:
            tiles += '\t' + self.tiles[index].compact()
        return tiles

    def get_nodes(self):
        """Returns the Array of nodes of the Board."""
        return self.nodes

    def get_edges(self):
        """Returns the Array of edges of the Board."""
        return self.edges


class Player:
    """
       A class used to represent a Player.
       Each Player starts the game with 0 of each resource, and the color of the Player depends on their position in
       the game. First Player: Red, Second Player: Blue, Third Player: Purple, Fourth Player: Orange.
       ----------
       user : UserConnection object
            the User which corresponds to the Player

       color : Integer
            a number representing the Player's color

       settlements : Array of Settlements objects
            an array of the owned Settlements by the Player

       roads : Array of Road objects
            an array of the owned Roads by the Player

       resources : Array of Integer
            an array of currently owned resources

       gains : Array of Integer
            an array of the resources gained by the Player with each different roll result

       built_settlement : Integer
            the cords of built a Settlement in the current turn if the Player has built, else 0,
            only relevant for the opening turns

       built_road : bool
            if the Player has built a Road in the current turn, only relevant for the opening turns

       rolled : bool
            if the Player has built rolled in the current turn

       Methods
       -------
       gain(roll)
            gives the Player the resources from a given roll result

       get_gains()
           returns the Array of the Player's gains

       can_afford(building_type)
           returns True if the Player can afford to build the specified building type, else False

       set_built_settlement(cords)
           sets the built_settlement to the cords of the settlement, only relevant in opening turns

       set_built_road(Boolean)
           sets built Road in first rounds to given Boolean value.

       get_resources()
           returns the resources of the Player as an Integer Array

       get_user()
           returns the UserConnection that is related to the Player

       add_settlement(cords)
           adds cords of the built Settlement by the Player to its Settlement cords Array

       add_road(cords)
           adds cords of the built Road by the Player to its Road cords Array.

       get_points()
           returns the points of the Player

       get_color()
           returns the color of the Player

       has_rolled()
           returns if the Player has rolled this turn already

       set_rolled(Boolean)
           changes if the Player has rolled or not this turn
    """

    def __init__(self, user, color):
        self.user = user
        self.color = color
        self.settlements = []
        self.roads = []
        self.resources = [0, 0, 0, 0, 0]
        self.gains = ([], [], [], [],
                      [], [], [], [],
                      [], [], [], [], [])
        self.built_settlement = False
        self.built_road = False
        self.rolled = False

    def gain(self, num):
        """
           Gains resources according to the roll.

           Parameters:
           num (int): The roll result
        """
        for resource in self.gains[int(num)]:
            self.resources[int(resource)] += 1

    def get_gains(self):
        """Returns the gains array."""
        return self.gains

    def can_afford(self, building_type):
        """
           Checks if the Player can afford to build the given building type

           Parameters:
           building_type (int): 1 represents Settlement, 2 represents Road

           Returns:
           Boolean: True if the Player can afford, else False
        """
        if building_type == 1:
            return self.resources[0] >= 1 and self.resources[1] >= 1 and self.resources[2] >= 1 and self.resources[4] >= 1
        if building_type == 2:
            return self.resources[1] >= 1 and self.resources[3] >= 1

    def set_built_settlement(self, cords):
        """Sets built Settlement in first rounds to given cords."""
        self.built_settlement = cords

    def set_built_road(self, Boolean):
        """Sets built Road in first rounds."""
        self.built_road = Boolean

    def get_resources(self):
        """Returns the resources of the Player."""
        return self.resources

    def get_user(self):
        """Returns the UserConnection that is related to the Player."""
        return self.user

    def add_settlement(self, cords):
        """Adds cords of the built Settlement by the Player to its Settlement cords Array."""
        self.settlements.append(cords)

    def add_road(self, cords):
        """Adds cords of the built Road by the Player to its Road cords Array."""
        self.roads.append(cords)

    def get_points(self):
        """Returns the points of the Player."""
        return len(self.settlements)

    def get_color(self):
        """Returns the color of the Player."""
        return str(self.color)

    def has_rolled(self):
        """Returns if the Player has rolled this turn already."""
        return self.rolled

    def set_rolled(self, Boolean):
        """Changes if the Player has rolled or not this turn."""
        self.rolled = Boolean


class GameLobby:
    """
           A class used to represent a Game Lobby.
           The Game Lobby can host up to 4 players, each Lobby has its unique Board.
           ----------
           players : Players object Array
                an Array of all Players that are in the GameLobby

           board : Board object
                the Board of the GameLobby

           current_player : Player object
                the Player which the turn is currently his

           started : Boolean
                if the game has started

           starting_game : Boolean
                if the game is in the starting game turns

           roll : Integer
                the latest roll, represented as first dice result in the ones, and the second dice result in the tens

           current_trade : String
                the string is equal to the name of the Player which is being offered the trade, if no trade is going on,
                the string is empty.

           Methods
           -------
           add_player(user)
                creates a Player object connected to the UserConnection and adds it to the players Array

           remove_player(user)
                removes the Player object which connected to the UserConnection and removes it from the players Array

           get_players()
                returns the players Array

           next_turn()
               changes the turn to the next Player

           check_valid_trade()
               checks if the trade offer is valid according to the game rules

           send_board(command='brd', extra_data='')
               sends the board with any additional information to the player/s, command and extra_data change depending
               on what action the player has taken

           user_to_player(user)
               converts a UserConnection object to the correlated Player object

           roll_dice()
               rolls two separate dices and changes the self.roll to the result of both dice
               
           build_settlement(user, cords)
               attempts to build a Settlement

           can_build_settlement(player, cords)
               returns if the Player has resources the resources to build Settlement and is able to build at given cords

           build_road(user, cords)
               attempts to build a Road

           can_build_road(player, cords)
               Returns if the Player has resources the resources to build Road and is able to build at given cords

           start_game()
               starts the game
        """
    def __init__(self, host):
        self.players = [Player(host, 0)]
        host.set_lobby(self)
        self.board = Board()
        self.current_player = None
        self.started = False
        self.starting_game = False
        self.roll = 0
        self.current_trade = ''

    def add_player(self, user):
        """creates a Player object connected to the UserConnection and adds it to the players Array"""
        if len(self.players) > 3:
            return '211'
        if self.started:
            return '214'
        self.players.append(Player(user, len(self.players)))
        for i, player in enumerate(self.players):
            player.color = i
            print(player.user.username, player.color)
        user.set_lobby(self)
        for player in self.players:
            if player.get_user() != user:
                player.get_user().send_players(self.players)
        return '105'

    def remove_player(self, user):
        """removes the Player object which connected to the UserConnection and removes it from the players Array"""
        to_delete = -1
        nodes = self.board.nodes
        edges = self.board.edges

        player = self.user_to_player(user)
        if self.started:
            deleted_buildings = str(player.get_color()) + player.get_user().get_username() + '\tN\t'
            for node in player.settlements:
                deleted_buildings += str(node) + '\t'
                nodes[node].set_owner(None)
            deleted_buildings += 'E'
            for edge in player.roads:
                deleted_buildings += '\t' + str(edge)
                edges[edge].set_owner(None)
            if self.current_player is player:
                self.next_turn()

        for i in range(len(self.players)):
            if self.players[i] is player:
                to_delete = i
        if to_delete > -1:
            del self.players[to_delete]

        for i, player in enumerate(self.players):
            player.color = i
            print(player.user.username, player.color)

        if not self.started:
            for player in self.players:
                player.get_user().send_players(self.players)
        else:
            self.send_board('del', deleted_buildings)

    def get_players(self):
        """returns the players Array"""
        return self.players

    def next_turn(self):
        """changes the turn to the next Player"""
        if self.starting_game:
            self.current_player.set_built_road(False)
            self.current_player.set_built_settlement(False)
            if self.players[len(self.players) - 1].get_points() >= 2:
                self.starting_game = False
                for player in self.players:
                    for i in range(2, 13):
                        player.gain(i)
        self.current_player = self.players[((self.players.index(self.current_player) + 1) % len(self.players))]
        self.current_player.set_rolled(False)

    def check_valid_trade(self):
        """checks if the trade offer is valid according to the game rules"""
        trade_info = self.current_trade[:-1]
        giving_anything = False
        receiving_anything = False
        trading_duplicate = False
        for i in range(len(trade_info) // 2):
            if int(trade_info[i]) > 0:
                giving_anything = True
                if int(trade_info[i + 5]) > 0:
                    trading_duplicate = True
                    break
            else:
                if int(trade_info[i + 5]) > 0:
                    receiving_anything = True
        return receiving_anything and giving_anything and not trading_duplicate

    def send_board(self, command='brd', extra_data=''):
        """sends the board with any additional information to the player/s, command and extra_data change depending
           on what action the player has taken.
           possible commands are:
           'win' - declare the current player as winner
           'srt' - sends the Tile information
           'nod' - sends the information of the newly built Settlement
           'edg' - sends the information of the newly built Road
           'del' - deletes all Settlements and Roads of the player who left
           'liv' - indicates a Player has left the Lobby mid-game
           'tri' - sends relevant trading information to the player
           'tro' - sends a trade offer to a given player
           'inv' - for the trade offer is against the game rules
           'cnt' - for auto-rejecting trade offers that are unable to be accepted by the other player
           'acp' - accepts the offered trade
           'dcl' - declines the offered trade
           'rol' - indicates the start of a new turn
           '4XX' - an error message sent to the user"""
        if self.current_player.get_points() == 5:
            command = 'win'
            extra_data = self.current_player.get_user().get_username()
        if command[0] == '4':
            self.current_player.get_user().send_error(command)
        elif command == 'srt':
            for player in self.players:
                info = command + '\t' + self.current_player.get_color() + self.current_player.get_user().get_username() + '\t' + str(player.get_color()) + '\t' + str(player.get_points())
                for resource in player.get_resources():
                    info += '\t' + str(resource)
                info += self.board.get_tiles()
                player.get_user().send_board(info)
        elif command == 'nod':
            if self.starting_game and not self.current_player.built_road:
                command = 'srt'
            for player in self.players:
                info = command + '\t' + self.current_player.get_color() + self.current_player.get_user().get_username() + '\t' + str(self.roll) + '\t' + str(player.get_points())
                for resource in player.get_resources():
                    info += '\t' + str(resource)
                info += '\tn\t' + extra_data + '\te' + '\tx'
                player.get_user().send_board(info)
        elif command == 'edg':
            if self.starting_game and not self.current_player.built_road:
                command = 'srt'
            for player in self.players:
                info = command + '\t' + self.current_player.get_color() + self.current_player.get_user().get_username() + '\t' + str(self.roll) + '\t' + str(player.get_points())
                for resource in player.get_resources():
                    info += '\t' + str(resource)
                info += '\tn' + '\te\t' + extra_data + '\tx'
                player.get_user().send_board(info)
        elif command == 'win' or command == 'del':
            if command == 'del' and self.starting_game and not self.current_player.built_road:
                command = 'liv'
            if extra_data[0] == self.current_player.get_color():
                self.current_trade = ''
            for player in self.players:
                info = command + '\t' + self.current_player.get_color() + self.current_player.get_user().get_username() + '\t' + str(self.roll) + '\t' + str(player.get_points())
                for resource in player.get_resources():
                    info += '\t' + str(resource)
                info += '\tn' + '\te' + '\tx\t' + extra_data
                player.get_user().send_board(info)
        elif command == 'tri':
            info = command + '\t' + self.current_player.get_color() + self.current_player.get_user().get_username() +\
                   '\t' + str(self.roll) + '\t' + str(self.current_player.get_points())
            for resource in self.current_player.get_resources():
                info += '\t' + str(resource)
            for player in self.players:
                if player is not self.current_player:
                    extra_data += '\t' + player.get_color() + player.get_user().get_username()
            info += '\tn' + '\te' + '\tx' + extra_data
            self.current_player.get_user().send_board(info)
        elif command == 'tro':
            trade_info = extra_data.split('\t')
            receive = trade_info[:5]
            give = trade_info[5:10]
            send_to_player = trade_info[10]
            self.current_trade = trade_info
            player = None
            print(trade_info)
            print(receive)
            print(give)
            print(send_to_player)
            for player_option in self.players:
                if send_to_player[0] == player_option.get_color():
                    player = player_option
            if player is None:
                player = self.current_player
                command='cnt'
            elif not self.check_valid_trade():
                player = self.current_player
                command = 'inv'
            else:
                for i, resource in enumerate(player.get_resources()):
                    if resource < int(give[i]):
                        command = 'cnt'
            info = command + '\t' + self.current_player.get_color() + self.current_player.get_user().get_username() +\
                             '\t' + str(self.roll) + '\t' + str(player.get_points())
            for resource in player.get_resources():
                info += '\t' + str(resource)
            info += '\tn' + '\te' + '\tx'
            for resource in receive + give:
                info += '\t' + resource
                self.current_trade += '\t' + resource
            player.get_user().send_board(info)
        elif command == 'acp' or command == 'dcl':
            for player_color in self.players:
                if player_color.get_color() == self.current_trade[10][0]:
                    player = player_color
            if command == 'acp':
                receive = self.current_trade[:5]
                give = self.current_trade[5:10]
                p1_resources = self.current_player.get_resources()
                p2_resources = player.get_resources()
                for i, resources in enumerate(receive):
                    p1_resources[i] -= int(resources)
                    p2_resources[i] += int(resources)
                for i, resources in enumerate(give):
                    p1_resources[i] += int(resources)
                    p2_resources[i] -= int(resources)
            self.current_trade = ''
            info = command + '\t' + self.current_player.get_color() + self.current_player.get_user().get_username() +\
                   '\t' + str(self.roll) + '\t' + str(self.current_player.get_points())
            for resource in self.current_player.get_resources():
                info += '\t' + str(resource)
            info += '\tn' + '\te' + '\tx'
            self.current_player.get_user().send_board(info)
            info = command + '\t' + self.current_player.get_color() + self.current_player.get_user().get_username() +\
                   '\t' + str(self.roll) + '\t' + str(player.get_points())
            for resource in player.get_resources():
                info += '\t' + str(resource)
            info += '\tn' + '\te' + '\tx'
            player.get_user().send_board(info)
        else:
            if self.starting_game and not self.current_player.built_road:
                command = 'srt'
            if not self.starting_game and not self.current_player.has_rolled():
                command = 'rol'
            for player in self.players:
                info = command + '\t' + self.current_player.get_color() + self.current_player.get_user().get_username() + '\t' + str(self.roll) + '\t' + str(
                    player.get_points())
                for resource in player.get_resources():
                    info += '\t' + str(resource)
                info += '\tn' + '\te' + '\tx'
                player.get_user().send_board(info)

    def user_to_player(self, user):
        """Converts a UserConnection object to the correlated Player object.
        :param user: UserConnection
        :return: Player
        """
        for player in self.players:
            if player.get_user() == user:
                return player
        return None

    def roll_dice(self):
        """"Rolls two separate dices and changes the self.roll to the result of both dice."""
        self.current_player.set_rolled(True)
        roll1 = randint(1, 6)
        roll2 = randint(1, 6)
        for player in self.players:
            player.gain(roll1 + roll2)
        self.roll = roll1 * 10 + roll2

    def build_settlement(self, user, cords):
        """
        Attempts to build a Settlement
        :param user: the User which wishes to build
        :param cords: the position where the Player wants to build
        """
        player = self.user_to_player(user)
        building_plot = self.board.get_nodes()[cords]

        if building_plot.get_owner() is not None:
            return '400', ''

        if player.built_settlement:
            return '403', ''

        if self.can_build_settlement(player, cords):
            if not self.starting_game:
                if not player.can_afford(1):
                    return '402', ''
                player_resources = player.get_resources()
                player_resources[0] -= 1
                player_resources[1] -= 1
                player_resources[2] -= 1
                player_resources[4] -= 1
            else:
                player.set_built_settlement(cords)
            building_plot.set_owner(player)
            new_resources = building_plot.get_resources()
            player_gains = player.get_gains()
            for resource in new_resources:
                player_gains[resource[1]].append(resource[0])
            player.add_settlement(cords)
            return 'nod', player.get_color() + '\t' + str(cords)
        return '401', ''

    def can_build_settlement(self, player, cords):
        """
        Returns if the Player has resources the resources to build Settlement and is able to build at given cords
        :param player: the Player which wishes to build
        :param cords: the position where the Player wants to build
        :return: Boolean
        """
        _node_to_edge_offsets = (-0x10, -1, -0x11, 0)
        edges = self.board.get_edges()
        nodes = self.board.get_nodes()

        check_neighbor = []
        adjacent_edges = []
        adjacent_nodes = []

        for edge_offset in _node_to_edge_offsets:
            if cords + edge_offset in self.board.used_edges:
                check_neighbor.append(cords + edge_offset)
                if edges[cords + edge_offset].get_owner() is player:
                    adjacent_edges.append(cords + edge_offset)
        for edge in check_neighbor:
            for node_offset in _node_to_edge_offsets:
                if edge - node_offset in self.board.used_nodes:
                    if nodes[edge - node_offset].get_owner() is not None:
                        return False

        if not self.starting_game:
            for available_edge in adjacent_edges:
                for node_offset in _node_to_edge_offsets:
                    if available_edge - node_offset != cords:
                        if available_edge - node_offset in self.board.used_nodes:
                            if nodes[available_edge - node_offset].get_owner() is None:
                                adjacent_nodes.append(available_edge - node_offset)

            for available_node in adjacent_nodes:
                for edge_offset in _node_to_edge_offsets:
                    if available_node + edge_offset not in adjacent_edges:
                        if available_node + edge_offset in self.board.used_edges:
                            if edges[available_node + edge_offset].get_owner() is player:
                                return True

        return self.starting_game

    def build_road(self, user, cords):
        """
        Attempts to build a Road.
        :param user: the User which wishes to build
        :param cords: the position where the Player wants to build
        """
        _edge_to_node_offsets = (0x10, 1, 0x11, 0)

        player = self.user_to_player(user)
        building_plot = self.board.get_edges()[cords]

        if building_plot.get_owner() is not None:
            return '400', ''

        if player.built_road:
            return '404', ''

        if self.can_build_road(player, cords):
            if not self.starting_game:
                if not player.can_afford(2):
                    return '406', ''
                player_resources = player.get_resources()
                player_resources[1] -= 1
                player_resources[3] -= 1
            else:
                can_build = False
                for node_offset in _edge_to_node_offsets:
                    if cords + node_offset == player.built_settlement:
                        can_build = True
                if not can_build:
                    return '405', ''
                player.set_built_road(True)
            player.add_road(cords)
            building_plot.set_owner(player)
            return 'edg', player.get_color() + '\t' + str(cords)
        return '401', ''

    def can_build_road(self, player, cords):
        """
        Returns if the Player has resources the resources to build Road and is able to build at given cords.
        :param player: the Player which wishes to build
        :param cords: the position where the Player wants to build
        :return: Boolean
        """
        _edge_to_node_offsets = (0x10, 1, 0x11, 0)
        _edge_to_edge_offsets = (-0x10, -0x11, 0x10, 0x11, 1, -1)
        edges = self.board.get_edges()
        nodes = self.board.get_nodes()

        for node_offset in _edge_to_node_offsets:
            if cords + node_offset in self.board.used_nodes:
                if nodes[cords + node_offset].get_owner() is player:
                    return True

        for edge_offset in _edge_to_edge_offsets:
            if cords + edge_offset in self.board.used_edges:
                if edges[cords + edge_offset].get_owner() is player:
                    return True

        return False

    def start_game(self):
        """Starts the game."""
        self.started = True
        self.starting_game = True
        self.current_player = self.players[0]
        for player in self.players:
            player.get_user().send_starting()
        self.send_board('srt')


class UserConnection:
    """
       A class used for managing the communication between the server and the client.
       ----------
       socket : Socket object
            the socket of the user

       public_key_user : Public Key object
            the public key of the user, used to encrypt messages before sending them

       cluster : MongoClient object
            the connection to the database - MongoDB, used for queries

       operations : String:Function Dictionary
            a dictionary where 3 letter codes are the keys and functions corresponding to the code are the values

       check_connection : Function
            a function used to check the currently online users, used to make sure a user cant be connected twice

       user : String
            the username of the user, the value is None until signing in

       _private_key : Private Key object
            a private key used to de-cypher messages received from the user

       public_key : Public Key object
            a public key sent to the client used to encrypt messages before they are sent

       lobby : GameLobby object
            the GameLobby the user is currently in, starts as None

       Methods
       -------
       generate_keys()
            generates random private and public keys

       encrypt_message(message)
           encrypts the message with the user's public key

       decrypt_message(encrypted_message)
           decrypts the received message using the private key

       set_lobby(lobby)
           changes the current GameLobby of the user

       get_lobby()
           returns the current GameLobby the user is in

       get_socket()
           returns the socket of the current connection

       send_players(players)
           sends the player color and names of all current players in the GameLobby

       send_board(board)
           sends the current board status to the user

       send_starting()
           sends starting message to the user to notify the start of the game

       send_error(error_code)
           sends error code to the user

       get_code()
           returns receives the confirmation code sent by user

       send_confirm()
           Sends confirmation that code has been successfully entered and the user my proceed

       wrong_code(too_many_attempts)
           sends wrong code error for the user which has failed an incorrect lobby code

       get_username()
           returns the username of the user

       set_username(username)
           sets the username after log in

       handle_client()
           handles all requests from the client, processing all commands and sends a positive or negative answer back
    """
    def __init__(self, socket, cluster, operations, check_connection):
        self.socket = socket
        self.public_key_user = None
        self.cluster = cluster
        self.operations = operations
        self.check_connection = check_connection
        self.username = None
        self._private_key = None
        self.public_key = None
        self.lobby = None

    def generate_keys(self):
        """Generates random private and public keys."""
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self._private_key.public_key()

    def encrypt_message(self, message):
        """Encrypts the message with the user's public key.
        :param message: the message that needs encryption
        :return: the encrypted message
        """

        if type(message) != 'bytes':
            message = message.encode()
        return self.public_key_user.encrypt(message,
                                       padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                    algorithm=hashes.SHA256(),
                                                    label=None))

    def decrypt_message(self, encrypted_message):
        """Decrypts the message with the server's private key.
        :param message: the message that needs decryption
        :return: the decrypted message
        """
        return self._private_key.decrypt(encrypted_message,
                                         padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                      algorithm=hashes.SHA256(),
                                                      label=None)).decode()

    def set_lobby(self, lobby):
        """Changes the current GameLobby of the user.
        :param lobby: GameLobby object
        """
        self.lobby = lobby

    def get_lobby(self):
        """Returns the current GameLobby the user is in."""
        return self.lobby

    def get_socket(self):
        """Returns the socket of the current connection."""
        return self.socket

    def send_players(self, players):
        """Sends the player color and names of all current players in the GameLobby.
        :param players: a Player Array of all Players in the current GameLobby
        """
        players_str = 'plr'
        for i, player in enumerate(players):
            players_str += '\t' + str(i) + player.get_user().get_username()
        self.socket.sendall(self.encrypt_message(players_str))

    def send_board(self, board):
        """Sends the current board status to the user.
        :param board: a string representing the changes made to the board last command
        """
        self.socket.sendall(self.encrypt_message(board))

    def send_starting(self):
        """Sends starting message to the user to notify the start of the game."""
        self.socket.sendall(self.encrypt_message('srt'))

    def send_error(self, error_code):
        """Sends error code to the user.
        :param error_code: an error code of 3 characters
        """
        self.socket.sendall(self.encrypt_message(error_code + '\t'))

    def get_code(self):
        """Returns receives the confirmation code sent by user."""
        return self.decrypt_message(self.socket.recv(8192))

    def send_confirm(self):
        """Sends confirmation that code has been successfully entered and the user my proceed"""
        self.socket.sendall(self.encrypt_message('104'))

    def wrong_code(self, too_many_attempts):
        """
        Sends wrong code error for the user which has failed an incorrect lobby code.
        :param too_many_attempts: indicates if the maximum amount of attempts has passed
        """
        if too_many_attempts:
            self.socket.sendall(self.encrypt_message('210'))
        else:
            self.socket.sendall(self.encrypt_message('208'))

    def get_username(self):
        """Returns the username of the user."""
        return self.username

    def set_username(self, username):
        """Sets the username after log in.
        :param username: the username of the user that have logged in
        """
        self.username = username

    def handle_client(self):
        """Handles all requests from the client, processing all commands and sends a positive or negative answer back"""
        try:
            self.generate_keys()
            key = self.socket.recv(8192)
            self.public_key_user = serialization.load_pem_public_key(key, backend=default_backend())
            self.socket.sendall(self.public_key.public_bytes(
                                encoding=serialization.Encoding.PEM,
                                format=serialization.PublicFormat.SubjectPublicKeyInfo))
            request = ''
            while True:
                request = self.decrypt_message(self.socket.recv(8192))
                self.check_connection()
                print('Starting {}'.format(request))
                try:
                    answer = self.operations[request[:3]](request[3:], self)
                    if answer is not None:
                        self.socket.sendall(self.encrypt_message(answer))
                except BaseException as error:
                    self.socket.sendall(self.encrypt_message('300'))
                    print('Command Error:', error)
                if request != '':
                    print('Ending {}'.format(request))
        except BaseException as server_error:
            print('Server Error:', server_error)
            print('Shutting Down Connection With User...')
            try:
                self.operations['liv'](request[3:], self)
            except AttributeError:
                pass
            self.socket.close()
            self.username = None
            self.socket = None


class Server:
    """
       A class for running and managing the server.
       ----------
       ip : String
            the IP the server is listening to (0.0.0.0)

       port : String
            the port the server is listening to

       socket : Socket object
            the socket of the server

       operations : String:Function Dictionary
            a dictionary where 3 letter codes are the keys and functions corresponding to the code are the values

       users : UserConnection Array
            an array of all clients that are currently connected to the server

       cluster : MongoClient object
            the connection to the database - MongoDB, used for queries

       email_connection : SMTP object
            the connection to the gmail service, allows sending emails used as 2 factor authentication

       codes : String Array
            all available codes that can be tied to GameLobby objects

       games : String:GameLobby Dictionary
            a dictionary where the key is the Lobby code and the value is the GameLobby object corresponding to the code

       Methods
       -------
       start()
            starts and initializes the server

       ---- GENERAL USER OPERATIONS ----

       handle_client(client_socket)
            starts a thread and UserConnection to manage the communication with the new client

       register_user(*args)
            Checks if the user is able to register with the given register info

       check_online_users()
            updates the users list to all currently still online UserConnections

       send_email(email, code)
            sends an email with confirmation code, part of the 2 factor authentication used in the system

       confirm_register(*args)
            confirms the code sent via email to the user, part of the 2 factor authentication

       log_in_user(*args)
            logs in the user

       ---- GAME RELATED OPERATIONS ----

       get_lobby_code(lobby)
           returns the code corresponding to the given GameLobby

       host_game(*args)
           creates a game where and adds the user to the GameLobby if there are free game codes for use

       leave_game(*args)
           properly leaves the GameLobby, deleting the lobby if its empty and removing the Player from the ongoing game

       join_game(*args)
           returns the current GameLobby the user is in

       get_players(*args)
           returns all Players in the GameLobby of the given code

       ---- STATIC METHODS ----

       get_username(*args)
           returns the user's username

       stop(*args)
           returns '000' code to stop ongoing processes

       start_game(*args)
           starts the hosted GameLobby game

       roll_dice(*args)
           Preforms the rolling dice action in the game

       build_settlement(*args)
           builds a settlement in the game

       build_road(*args)
           builds a road in the game

       next_turn(*args)
           passes the turn to the next Player

       start_trade(*args)
           starts the trading for the Player

       offer_trade(*args)
           offer a given player a trade offer

       decline_offer(*args)
            Declines the given offer

       accept_offer(*args)
           accepts the given offer

       log_off(*args)
           logs off the user
    """

    def __init__(self, ip, port, mongo_conection):
        self.ip = ip
        self.port = port
        self.socket = None
        self.operations = None
        self.users = []
        self.cluster = MongoClient(mongo_conection)['Catan']
        self.email_connection = SMTP('smtp.gmail.com', 587)
        self.codes = ['181327', '947482', '732178', '392857', '735393', '806739', '591087', '962764']
        shuffle(self.codes)
        self.games = {}
        with open('../Text/email.txt') as file:
            email_code = file.readline()
        try:
            self.email_connection.starttls()
            self.email_connection.login('catanonlinegame@gmail.com', email_code)
        except BaseException as email_error:
            print('Email Error:', email_error)

    def start(self):
        """Starts and initializes the server."""
        try:
            print('Server Starts Up On IP %s Port %s' % (self.ip, self.port))
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.ip, self.port))
            self.socket.listen(1)
            self.operations = {'rgs': self.register_user,
                               'lgn': self.log_in_user,
                               'usr': self.get_username,
                               'cnf': self.confirm_register,
                               'lof': self.log_off,
                               'hst': self.host_game,
                               'jin': self.join_game,
                               'liv': self.leave_game,
                               'plr': self.get_players,
                               'srt': self.start_game,
                               'rol': self.roll_dice,
                               'nod': self.build_settlement,
                               'edg': self.build_road,
                               'fns': self.next_turn,
                               'stp': self.stop,
                               'tri': self.start_trade,
                               'tro': self.offer_trade,
                               'acp': self.accept_offer,
                               'dcl': self.decline_offer}

            while True:
                client_socket, client_address = self.socket.accept()
                self.handle_client(client_socket)

        except socket.error as socket_error:
            print('Socket Error:', socket_error)

    def handle_client(self, client_socket):
        """
        Starts a thread and UserConnection to manage the communication with the new client.
        :param client_socket: the socket of the new client
        """
        print('Handling Client Number', len(self.users))
        user = UserConnection(client_socket, self.cluster, self.operations, self.check_online_users)
        self.users.append(user)
        client_handler = threading.Thread(target=user.handle_client, args=())
        client_handler.start()

    def register_user(self, *args):
        """
        Checks if the user is able to register with the given register info.
        :param args[0]: the register info username + password + email
        :return: corresponding success/error code
        """
        register_info = args[0]
        username = register_info[:register_info.find('\t')]
        password = register_info[register_info.find('\t') + 1: register_info.rfind('\t')]
        email = register_info[register_info.rfind('\t') + 1:]
        if not search(compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!#%*?&]{6,32}"), password):
            return '202'
        if not is_email(email):
            return '205'
        if not 4 < len(username) < 13:
            return '201'
        if self.cluster['Users'].find_one({'email': email}) is not None:
            return '215'
        if self.cluster['Users'].find_one({'username': username}) is not None:
            return '204'
        return '103'

    def check_online_users(self):
        """updates the users list to all currently still online UserConnections"""
        usernames = []
        for user in self.users:
            if user.socket is None:
                self.users.remove(user)
            else:
                usernames.append(user.get_username())
        return usernames

    def send_email(self, email, code):
        """Sends an email with confirmation code, part of the 2 factor authentication used in the system.
        :param email: the given email of the user
        :param code: the randomly generated code the user will need to type in order to confirm registration
        """
        print('Sending Email...')
        print('Code:', code)
        sender = 'catanonlinegame@gmail.com'
        receiver = email
        message = """From: Catan Game <catanonlinegame@gmail.com>\n\
To: {}\n\
Subject: Confirmation Code For Catan\n\

Please enter the following code to confirm your email: {}\n\
If you haven't expected this email, please ignore it.""".format(email, code)
        try:
            self.email_connection.sendmail(sender, receiver, message)
            print('Successfully Sent Email')
        except SMTPException as email_error:
            print('Email Error:', email_error)

    def confirm_register(self, *args):
        """
        Confirms the code sent via email to the user, part of the 2 factor authentication.
        :param args[0]: the register info of the user
        :param args[1]: the UserConnection of the user
        :return: corresponding success/error code
        """
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
                while start > time() - 60:
                    user.wrong_code(True)
                    input = user.get_code()
            else:
                user.wrong_code(False)
                input = user.get_code()
        password = hashpw(password.encode(), gensalt())
        if self.cluster['Users'].find_one({'email': email}) is not None:
            return '215'
        if self.cluster['Users'].find_one({'username': username}) is not None:
            return '204'
        self.cluster['Users'].insert_one({'username': username, 'password': password, 'email': email})
        return '101'

    def log_in_user(self, *args):
        """
        Logs in the user.
        :param args[0]: the log in info of the user
        :param args[1]: the UserConnection of the user
        :return: corresponding success/error code
        """
        log_in_info = args[0]
        user = args[1]
        username = log_in_info[:log_in_info.find('\t')]
        password = log_in_info[log_in_info.find('\t') + 1:]
        if password == '' or username == '':
            return '203'
        if not search(compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!#%*?&]{6,32}"), password) or not 4 < len(
                username) < 13:
            return '203'
        if self.cluster['Users'].find_one({'username': username}) is not None:
            stored_hash = self.cluster['Users'].find_one({'username': username})['password']
            if hashpw(password.encode(), stored_hash) == stored_hash:
                if username in self.check_online_users():
                    return '209'
            user.set_username(username)
            return '102'
        return '203'

    def get_lobby_code(self, lobby):
        """
        Returns the code corresponding to the given GameLobby.
        :param lobby: the GameLobby object
        :return: the code corresponding to the given GameLobby object
        """
        for code, game_lobby in self.games.items():
            if lobby == game_lobby:
                return code

    def host_game(self, *args):
        """
        creates a game where and adds the user to the GameLobby if there are free game codes for use
        :param args[1]: the UserConnection used to create a Player object in the GameLobby
        :return: corresponding success/error code
        """
        try:
            code = self.codes.pop()
            self.games[code] = GameLobby(args[1])
            return '105' + code
        except IndexError:
            return '213'

    def leave_game(self, *args):
        """
        Properly leaves the GameLobby, deleting the lobby if its empty and removing the Player from the ongoing game.
        :param args[1]: the UserConnection of the leaving Player in the GameLobby
        """
        user = args[1]
        lobby = user.get_lobby()
        lobby.remove_player(user)
        user.set_lobby(None)
        if len(lobby.get_players()) == 0:
            code = self.get_lobby_code(lobby)
            self.codes.append(code)
            del self.games[code]

    def join_game(self, *args):
        """
        Joins the GameLobby if the given code exists.
        :param args[0]: the code of the GameLobby
        :param args[1]: the UserConnection of the leaving Player in the GameLobby
        :return: corresponding success/error code
        """
        try:
            return self.games[args[0]].add_player(args[1])
        except KeyError:
            return '212'

    def get_players(self, *args):
        """
        Returns all Players in the GameLobby of the given code.
        :param args[0]: the code of the GameLobby
        :return: a string of all player's colors and usernames
        """
        players = self.games[args[0]].get_players()
        string = 'plr'
        for i, player in enumerate(players):
            string += '\t' + str(i) + player.get_user().get_username()
        return string

    @staticmethod
    def get_username(*args):
        """Returns the user's username.
        :param args[1]: the UserConnection of the user
        :return: the username
        """
        return args[1].get_username()

    @staticmethod
    def stop(*args):
        """Returns '000' code to stop ongoing processes."""
        return '000'

    @staticmethod
    def start_game(*args):
        """Starts the hosted GameLobby game.
        :param args[1]: the UserConnection of the user
        """
        args[1].get_lobby().start_game()

    @staticmethod
    def roll_dice(*args):
        """Preforms the rolling dice action in the game.
        :param args[1]: the UserConnection of the user
        """
        args[1].get_lobby().roll_dice()
        args[1].get_lobby().send_board()

    @staticmethod
    def build_settlement(*args):
        """Builds a settlement in the game.
        :param args[0]: the building coordinates of the settlement
        :param args[1]: the UserConnection of the user
        """
        answer = args[1].get_lobby().build_settlement(args[1], int(args[0]))
        args[1].get_lobby().send_board(answer[0], answer[1])

    @staticmethod
    def build_road(*args):
        """Builds a road in the game.
        :param args[0]: the building coordinates of the road
        :param args[1]: the UserConnection of the user
        """
        answer = args[1].get_lobby().build_road(args[1], int(args[0]))
        args[1].get_lobby().send_board(answer[0], answer[1])

    @staticmethod
    def next_turn(*args):
        """Passes the turn to the next Player.
        :param args[1]: the UserConnection of the user
        """
        args[1].get_lobby().next_turn()
        args[1].get_lobby().send_board()

    @staticmethod
    def start_trade(*args):
        """Starts the trading for the Player.
        :param args[1]: the UserConnection of the user
        """
        args[1].get_lobby().send_board('tri')

    @staticmethod
    def offer_trade(*args):
        """Offer a given player a trade offer.
        :param args[0]: trading information, what will be given to each Player, and which Player the offer is aimed at
        :param args[1]: the UserConnection of the user
        """
        args[1].get_lobby().send_board('tro', args[0])

    @staticmethod
    def decline_offer(*args):
        """Declines the given offer.
        :param args[1]: the UserConnection of the user
        """
        args[1].get_lobby().send_board('dcl', args[0])

    @staticmethod
    def accept_offer(*args):
        """Accepts the given offer.
        :param args[1]: the UserConnection of the user
        """
        args[1].get_lobby().send_board('acp', args[0])

    @staticmethod
    def log_off(*args):
        """Logs off the user.
        :param args[1]: the UserConnection of the user
        """
        user = args[1]
        user.set_username(None)


if __name__ == '__main__':
    with open('../Text/mongodb.txt') as file:
        pymongo = file.readline()
    server = Server('0.0.0.0', 1731, pymongo)
    server.start()
