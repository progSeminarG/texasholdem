#! /usr/bin/env python3

import random

class Player(object):
    def get_know_dealer(self,dealer_input):
        self.dealer = dealer_input
    def get_hand(self,list_of_cards):
        self.cards = list_of_cards
    def respond(self):
        return random.choice([ 'call', 'fold', int(10)])
