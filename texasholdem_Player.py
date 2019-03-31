#! /usr/bin/env python3

import random

class Player(object):
    def get_know_dealer(self,dealer_input):  # necessary
        self.dealer = dealer_input
    def get_hand(self,list_of_cards):  # necessary
        self.cards = list_of_cards
    def respond(self):  # necessary
        return random.choice([ 'call', 'fold', int(10)])
    def get_result(self,result):  # called when 1 game finished
        pass
        # print(result)
