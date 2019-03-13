#! /usr/bin/env python3

import random
import numpy as np
import os
from texasholdem_Dealer import Porker_Hand

class Player(object):
    def get_know_dealer(self,dealer_input):
        self.dealer = dealer_input
    def get_hand(self,list_of_cards):
        self.cards = list_of_cards
    def open_cards(self):
        return self.cards
    def respond(self):
        return random.choice([ 'call', 'fold', int(10)])

class ShiraiAI(Player):
    def respond(self):
        my_money=\
            self.dealer.list_of_money[
            self.dealer.list_of_players.index('ShiraiAI')] #arg1
        return my_money
