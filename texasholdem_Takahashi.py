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
    def __same_suit(self,_cards):
        _suits = set([_card.suit for _card in _cards])
        if len(_suits) == 1:
            return True
        return False
    def respond(self):
        self.__field = self.__dealer.field
        self.__list_of_money = self.__dealer.list_of_money
        self.__my_money = self.__list_of_money[self.__position]
        self.__minimum_bet = self.__dealer.minimum_bet
        self.__minimum_raise = self.__dealer.minimum_raise
        self.__same_suit(self.__cards)

        _my_hand = self.__field + self.__cards
        _hand_inst = Porker_Hand(_my_hand)
        _score = _hand_inst.score
        _hand = _hand_inst.best_hand
        if len(self.__field) == 0:
            if _score >= 1.0 + 2*10.0/30.0:
                return self.__bet(self.__minimum_raise)
            if self.__minimum_bet <= self.__my_money * 0.05:
                return 'call'
            return 'fold'
        if len(self.__field) > 0:
            if _score > 3.0:
                return self.__bet(self.__my_money)
            if _score > 2.0 + 2*9.0/30.0:
                return 'call'
            if self.__bet_money > self.__my_money * 0.1:
                return 'call'
            if self.__same_suit(_my_hand):
                return 'call'
            if _score > 1.0:
                if self.__minimum_bet <= self.__my_money * 0.05:
                    return 'call'
            return 'fold'

