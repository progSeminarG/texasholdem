#! /usr/bin/env python3

import random
import sys

from texasholdem_Dealer import Porker_Hand

class TakahashiAI(object):
    def get_know_dealer(self,dealer_input):
        self.__dealer = dealer_input
        self.__players = self.__dealer.list_of_players
        self.__position = self.__dealer.get_position(self)
    def get_hand(self,list_of_cards):
        self.__cards = list_of_cards
        self.__bet_money = 0
    def __bet(self,_money):
        self.__bet_money += int(_money)
        return int(_money)
    def respond(self):
        self.__field = self.__dealer.field
        self.__list_of_money = self.__dealer.list_of_money
        self.__my_money = self.__list_of_money[self.__position]
        self.__minimum_bet = self.__dealer.minimum_bet
        self.__minimum_raise = self.__dealer.minimum_raise

        _my_hand = self.__field + self.__cards
        _hand_inst = Porker_Hand(_my_hand)
        _score = _hand_inst.score
        _hand = _hand_inst.best_hand
        if len(self.__field) == 0:
            if _score > 1.0:
                return self.__bet(self.__minimum_raise)
            if self.__minimum_bet <= self.__my_money * 0.05:
                return 'call'
            return 'fold'
        if len(self.__field) > 0:
            if _score > 5.0:
                return self.__bet(self.__minimum_bet * _score)
            if _score > 3.0:
                return self.__minimum_bet
            if _score > 1.0:
                if self.__minimum_bet <= self.__my_money * 0.05:
                    return 'call'
            return 'fold'

