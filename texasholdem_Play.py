#! /usr/bin/env python3

import argparse
import random
from copy import deepcopy
import sys

from texasholdem_Dealer import Card, Dealer
from texasholdem_Player import Player
from texasholdem_Kawada import KawadaAI
from texasholdem_Human import Human




class Game(object):
    def __init__(self, players_list):
        self.__players = players_list
        self.__INITIAL_MONEY = 500  # money each player has in initial
        self.__accounts = [self.__INITIAL_MONEY]*len(self.__players)  # player's money at first
        self.__DBTN = 0  # position of Dealer BuTtoN
#        self.__smallb = 0  # number of small-blined at first

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
        self.__accounts = self.__dealer.syozikin_kosin()
        self.__DBTN = self.__dealer.DBTN_update()
#        self.smallb = (self.__dealer.smallb_kosin()+1)%len(self.__players)

    def ninzu_kakunin(self):  # if the numer of players who can play new game is 1 return True
        if self.__dealer.sanka_kano_ninzu() == 1:
            return True
        else:
            return False

    @property
    def accounts(self):
        return self.__accounts

    @property
    def DBTN(self):  # position of Dealer BuTtoN
        return self.__DBTN

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

    parser.add_argument('--players', type=str, default=['Kawada','Human','Player','Player'],
                        nargs='+', help='set list of players')
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
        if player == 'Kawada':
            players_list.append(KawadaAI())
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
    print("players:",game.names_of_players())

    # play games #
    for i in range(args.numgames[0]):
        print("===== game", i, "=====")
        game.play()

    '''
    game = Game(players_list)
    nl = []
    for i in range(0,len(players_list)):
        nl.append(players_list[i].__class__.__name__)
    print("players;", nl)
    game_end = False
    i = 0
    while game_end == False:
        print("===== game", i, "=====")
        game.play()
        game_end = game.ninzu_kakunin()
        i = i+1
        print()
        print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print(game.syozikin)
    print("players;", nl)  # すみません毎回リストがシャッフルされて自分のAIが見づらいので書き足しました
    '''
