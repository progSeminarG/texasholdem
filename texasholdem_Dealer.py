#! /usr/bin/env python3

import random
import sys
from copy import deepcopy

class Card(object):
    def __init__(self,suit,number):
        if suit not in ("S","C","H","D"): # S: spade, C: club, H: heart, D: Diamond
            raise ValueError("ERROR: suit of card is not correct: " + str(suit))
        self.__suit = suit
        if number not in range(1,14):
            raise ValueError("ERROR: number of card is not correct: " + str(number))
        self.__number = number

    @property
    def card(self):
        return (self.__suit,self.__number)
    @property
    def suit(self):
        return self.__suit
    @property
    def number(self):
        return self.__number

class Dealer(object):
    def __init__(self,players_input):
        self.__MIN_NUMBER_CARDS = 1 # smallest number of playing cards
        self.__MAX_NUMBER_CARDS = 13 # largest number of playing cards
        self.__SUITE = ['S','C','H','D'] # suit of playing cards
        self.__NUM_HAND = 2 # number of hands
        self.__INITIAL_MONEY = 500 # money each player has in initial
        self.__NUM_MAX_FIELD = 5 # maximum number of field
        self.__players = players_input # instance of players
        self.__num_players = len(self.__players) # number of players
        self.__num_handling_cards = self.__NUM_HAND * self.__num_players + self.__NUM_MAX_FIELD # number of cards that deal with
        self.__money_each_player = [self.__INITIAL_MONEY]*self.__num_players # money list of players
        self.__field = []
        for player in self.__players:
            player.get_know_dealer(self)


    def __create_all_cards_stack(self): # create list of [S1, S2, ..., D13]
        _cards = []
        for inumber in range(self.__MIN_NUMBER_CARDS,self.__MAX_NUMBER_CARDS+1):
            for suit in self.__SUITE:
                _cards.append(Card(suit,inumber))
        return _cards


    def handout_cards(self):
        self.__field = []
        self.__all_cards = self.__create_all_cards_stack()
        self.__handling_cards = random.sample(self.__all_cards,self.__num_handling_cards)
        self.__players_cards = [] # each player's hand
        for player in self.__players:
            self.__players_cards.append([self.__handling_cards.pop(i) for i in range(self.__NUM_HAND)])
            player.get_hand(self.__players_cards[-1])

    def put_field(self):
        self.__field.append(self.__handling_cards.pop(0))

    def get_response(self):
        for player in self.__players:
            self.__respond = player.respond()
        # 各プレイヤーからの返答を聞き、次の field のオープンや、スコア計算の手前まで行う (櫻井くん)

    def calc_hand_score(self):
        pass # 手札の強さを計算するメソッド (白井くん)


    @property
    def field(self):
        return self.__field

