#! /usr/bin/env python3

import argparse
import random
from copy import deepcopy

from texasholdem_Dealer import Card, Dealer
from texasholdem_Player import Player
from texasholdem_Kawada import KawadaAI


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.MetavarTypeHelpFormatter):
    pass


parser = argparse.ArgumentParser(description="play Texas Hold'em.",
                                 formatter_class=CustomFormatter)

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


class Game(object):
    def __init__(self, players_list):
        self.__players = players_list
        self.syozikin = [500]*len(self.__players)
        self.smallb = 0

    def play(self):
        self.__dealer = Dealer(deepcopy(self.__players), deepcopy(self.syozikin), deepcopy(self.smallb))
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
        # self.__dealer.calc_hand_score()
        self.syozikin = self.__dealer.syozikin_kosin()
        self.smallb = (self.__dealer.smallb_kosin()+1)%len(self.__players)

    def ninzu_kakunin(self):
        if self.__dealer.sanka_kano_ninzu() == 1:
            return True
        else:
            return False


# === create players ===
player1 = KawadaAI()
player2 = Player()
player3 = Player()
player4 = Player()

players_list = [player1, player2, player3, player4]
random.shuffle(players_list)
'''
game = Game(players_list)
NUM_GAME = 1
for i in range(0,len(players_list)):
    print(players_list[i])  # すみません毎回リストがシャッフルされて自分のAIが見づらいので書き足しました
for i in range(NUM_GAME):
    print("===== game", i, "=====")
    game.play()'''


game = Game(players_list)
for i in range(0,len(players_list)):
    print(players_list[i])  # すみません毎回リストがシャッフルされて自分のAIが見づらいので書き足しました
game_end = False
i = 0
while game_end == False:
    print("===== game", i, "=====")
    game.play()
    game_end = game.ninzu_kakunin()
    i = i+1
    print()
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
for i in range(0, len(players_list)):
    print(players_list[i])  # すみません毎回リストがシャッフルされて自分のAIが見づらいので書き足しました
