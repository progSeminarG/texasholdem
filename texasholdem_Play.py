#! /usr/bin/env python3

import argparse
from texasholdem_Dealer import Card, Dealer
from texasholdem_Player import Player

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,argparse.MetavarTypeHelpFormatter):
    pass

parser = argparse.ArgumentParser(description="play Texas Hold'em.", formatter_class=CustomFormatter)

#parser.add_argument('--num', type=int, dest='num_game', nargs='?', default=1, help="number of game")
#parser.add_argument('--out', type=str, dest='outfile', nargs='?', default='stat.csv', help="output file")
#parser.add_argument('--fig', type=str, dest='figfile', nargs='?', default='stat.png', help="output figure file (png)")
#parser.add_argument('-q', '--quiet', action="store_true", help='reduce print sequence')
#parser.add_argument('--upload', type=str, dest='token', nargs=1, help='upoad figure. parse token.')
#args = parser.parse_args()


class Game(object):
    def __init__(self,dealer):
        self.__dealer = dealer

    def play(self):
        self.__dealer.handout_cards()
        for i in range(3):
            self.__dealer.put_field()
        print("field:",[card.card for card in self.__dealer.field])
        self.__dealer.get_response()
        self.__dealer.put_field()
        print("field:",[card.card for card in self.__dealer.field])
        self.__dealer.get_response()
        self.__dealer.put_field()
        print("field:",[card.card for card in self.__dealer.field])
        self.__dealer.get_response()
        self.__dealer.calc_hand_score()


from texasholdem_Dealer import Dealer
from texasholdem_Takahashi import TakahashiAI

### create players ###
player1 = TakahashiAI()
player2 = Player()
player3 = Player()
player4 = Player()

players_list = [player1, player2, player3, player4]

mydealer = Dealer(players_list)

game = Game(mydealer)
NUM_GAME = 10
for i in range(NUM_GAME):
    print("===== game",i,"=====")
    game.play()
