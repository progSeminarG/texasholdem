#! /usr/bin/env python3

import random
import sys

from texasholdem_Dealer import Card
from texasholdem_Dealer import Porker_Hand

class TakahashiAI(object):
    def __init__(self):
        self.__MAX_SS = 14.0
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
    def bool_all_in(self,list_bet,list_money):
        _list_bool_all_in = []
        for i in range(len(list_money)):
            if list_bet[i] == list_money[i]:
                _list_bool_all_in.append(True)
            else:
                _list_bool_all_in.append(False)
        return _list_bool_all_in
    def get_result(self, _result):
        pass

    def respond(self):
        self.__field = self.__dealer.field
        self.__list_of_money = self.__dealer.list_of_money
        self.__my_money = self.__list_of_money[self.__position]
        self.__minimum_bet = self.__dealer.minimum_bet
        self.__minimum_raise = self.__dealer.minimum_raise
        self.__same_suit(self.__cards)
        self.__response_list = self.__dealer.response_list
        self.__list_of_money = self.__dealer.list_of_money
        self.__all_in = self.bool_all_in(self.__response_list, self.__list_of_money)
        self.__all_in_exist = sum(self.__all_in)

        _my_hand = self.__field + self.__cards
        _hand_inst = Porker_Hand(_my_hand)
        _score = _hand_inst.score
        _hand = _hand_inst.best_hand
        if self.__all_in_exist == 0:
            if len(self.__field) == 0:
                if _score >= 1.0 + 2*10.0/30.0:
                    return self.__bet(self.__minimum_raise)
                if self.__minimum_bet <= self.__my_money * 0.05:
                    return 'call'
                return 'fold'
            if len(self.__field) > 0:
                if _score > 3.0:
                    return self.__my_money
#                    return self.__bet(self.__my_money)
#                if _score > 2.0 + 2*9.0/30.0:
#                    return 'call'
#                if self.__bet_money > self.__my_money * 0.1:
#                    return 'call'
#                if self.__same_suit(_my_hand):
#                    return 'call'
#                if _score > 1.0:
#                    if self.__minimum_bet <= self.__my_money * 0.05:
#                        return 'call'
                return 'fold'
        if self.__all_in_exist <= 3:
            if len(self.__field) <= 2:
                if _score >= 1.0 + 9.0/self.__MAX_SS:
                    return 'call'
                return 'fold'
            if len(self.__field) > 2:
                return 'call'
        if self.__all_in_exist > 3:
            if len(self.__field) <= 2:
                if _score >= 1.0 + 7.0/self.__MAX_SS:
                    return 'call'
                return 'fold'
            if len(self.__field) > 2:
                return 'call'


