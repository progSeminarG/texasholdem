#! /usr/bin/env python3

import argparse
import random
from copy import deepcopy
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


from texasholdem_Dealer import Card, Dealer
from texasholdem_Player import Player
from texasholdem_Kawada import KawadaAI
from texasholdem_Shirai import ShiraiAI
from texasholdem_Human import Human


class Game(object):
    def __init__(self, players_list):
        self.__INITIAL_MONEY = 10  # money each player has in initial
        self.__players = players_list
        self.__num_players = len(self.__players)
        self.__total_money = self.__INITIAL_MONEY * self.__num_players
        # player's money at first
        self.__accounts = [self.__INITIAL_MONEY]*self.__num_players
        self.__DB = 0  # position of Dealer Button

    def play(self):
        self.__dealer = Dealer(self, self.__players)
        self.__dealer.handout_cards()
        self.__dealer.get_responses()
        for i in range(3):
            self.__dealer.put_field()
        print("field:", [card.card for card in self.__dealer.field])
        self.__dealer.get_responses()
        self.__dealer.put_field()
        print("field:", [card.card for card in self.__dealer.field])
        self.__dealer.get_responses()
        self.__dealer.put_field()
        print("field:", [card.card for card in self.__dealer.field])
        self.__dealer.get_responses()
        print()
        print("open cards && calculate score")
        self.__dealer.calc()
        self.__accounts = self.__dealer.list_of_money
        self.__DB = self.__dealer.DB_update()

    def plot(self,_i):
        if _i == 0:
            pp = str(0)
            for k in range(len(self.__accounts)):
                pp += "," + str(self.__accounts[k])
            pp += "\n"
            f.write(pp)
        game.play()
        pp = str(_i+1)
        for k in range(len(self.__accounts)):
            pp += "," + str(self.__accounts[k])
        pp += "\n"
        f.write(pp)

    @property
    def accounts(self):
        return self.__accounts

    @property
    def total_money(self):
        return self.__total_money

    @property
    def DB(self):  # position of Dealer BuTtoN
        return self.__DB

    @property
    def num_players(self):
        return self.__num_players

    def names_of_players(self):
        return [i.__class__.__name__ for i in players_list]


if __name__ == '__main__':
    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.MetavarTypeHelpFormatter):
        pass

    parser = argparse.ArgumentParser(description="play Texas Hold'em.",
                                     formatter_class=CustomFormatter)

    parser.add_argument('--noshuffle', action='store_false', dest='shuffle',
                        help='do not shuffle players')

    parser.add_argument('--numgames', type=int, default=[5], nargs=1,
                        help='set number of games')

    parser.add_argument('--players', type=str,
                        default=['Kawada', 'Shirai', 'Player', 'Player', 'Player', 'Player', 'Player', 'Player'],
                        nargs='+', help='set list of players')

    parser.add_argument('--tournament', action='store_true',
                        help='play untile one has all money')
                        
    parser.add_argument('--numtournament', type=int, nargs=1, default=[1],
                        help='number of player for tournament winner')
    '''
    parser.add_argument('--num', type=int, dest='num_game', nargs='?',
    default=1, help="number of game")
    parser.add_argument('--out', type=str, dest='outfile', nargs='?',
    default='stat.csv', help="output file")
    parser.add_argument('--fig', type=str, dest='figfile', nargs='?',
    default='stat.png', help="output figure file (png)")
    parser.add_argument('-q', '--quiet', action="store_true",
    help='reduce print sequence')
    parser.add_argument('--upload', type=str, dest='token', nargs=1,
    help='upoad figure. parse token.')
    '''
    args = parser.parse_args()

    #  create list of players #
    players_list = []
    for player in args.players:
        if player in {'Kawada', 'KawadaAI'}:
            players_list.append(KawadaAI())
        elif player in {'Shirai', 'ShiraiAI'}:
            players_list.append(ShiraiAI())
        elif player == 'Human':
            players_list.append(Human())
        elif player == 'Player':
            players_list.append(Player())
        else:
            raise ValueError("ERROR! No such an AI!")

    # shuffle players #
    if args.shuffle:
        random.shuffle(players_list)

    # create game #
    game = Game(players_list)
    print("players:", game.names_of_players())

    # play games #
    output = "stat.csv" # ログファイル
    f = open(output,"w")
    pp = "num"
    for k in range(len( game.names_of_players() )):
            pp += "," + str(game.names_of_players()[k])
    pp += "\n"
    f.write(pp) # header
    
    if args.tournament:
        _i = 0
        while game.accounts.count(0) != game.num_players-args.numtournament[0]:
            print("===== game", _i, "=====")
            game.plot(_i)
            _i += 1
        numgg = _i
    else:
        numgg = args.numgames[0]
        for _i in range(args.numgames[0]):
            print("===== game", _i, "=====")
            game.plot(_i)
    f.close()


#plot
df = pd.read_csv(output,header = 0,encoding = 'utf-8')
color = ["red", "green", "blue", "yellow", "violet", "goldenrod", "crimson", "aqua", "black"]
l = [0]*(len(players_list) + 1)
for k in range(len(players_list) + 1):
    l[k] = df.iloc[0:numgg+1, k].values.tolist()
for k in range(1, len(players_list) + 1):
    plt.plot(l[0], l[k], color[k-1])
plt.show()
    
