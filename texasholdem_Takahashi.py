#! /usr/bin/env python3

import random
import sys

from texasholdem_Dealer import Dealer

class TakahashiAI(object):
    def get_know_dealer(self,dealer_input):
        self.__dealer = dealer_input
        self.__players = self.__dealer.list_of_players
        self.__position = self.__dealer.get_position(self)
    def get_hand(self,list_of_cards):
        self.cards = list_of_cards
    def respond(self):
        self.__field = self.__dealer.field
        self.__list_of_money = self.__dealer.list_of_money
        self.__my_money = self.__list_of_money[self.__position]
        self.__minimum_bet = self.__dealer.minimum_bet


        return random.choice(['call',30,30,40,50,60,70,100])
        if self.__minimum_bet < self.__my_money:
            return random.choice(['call', int(30)])
        elif len(self.__field) > 4:
            return 'call'
        else:
            return 'fold'
