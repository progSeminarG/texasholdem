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
        self.__MIN_NUMBER_CARDS = 1
        self.__MAX_NUMBER_CARDS = 13
        self.__SUITE = ['S','C','H','D']
        self.__NUM_HAND = 2 # number of hands
        self.__INITIAL_MONEY = 500 # money each player has in initial
        self.__NUM_MAX_FIELD = 5 # maximum number of field
        self.__players = players_input # instance of players
        self.__num_players = len(self.__players)
        self.__num_handling_cards = self.__NUM_HAND * self.__num_players + self.__NUM_MAX_FIELD
        self.__playing_players = deepcopy(self.__players) # number of plyaers in game

        self.__handout_cards()

    def __create_all_cards_stack(self): # create list of [S1, S2, ..., D13]
        _cards = []
        for inumber in range(self.__MIN_NUMBER_CARDS,self.__MAX_NUMBER_CARDS+1):
            for suit in self.__SUITE:
                _cards.append(Card(suit,inumber))
        return _cards


    def __handout_cards(self):
        self.__all_cards = self.__create_all_cards_stack()
        self.__handling_cards = random.sample(self.__all_cards,self.__num_handling_cards)
        for player in self.__playing_players:
            player.get_hand([self.__handling_cards.pop(i) for i in range(self.__NUM_HAND)])
        for card in self.__handling_cards:
            print(card.card)

    def __put_field(self):
        try:
            self.__field.append(self.__handling_cards.pop(0))
        except:
            self.__field = [self.__handling_cards.pop(0)]
