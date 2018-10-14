
#! /usr/bin/env python3

import random

class Player(object):
    def get_know_dealer(self,dealer_input):
        self.dealer = dealer_input
    def get_hand(self,list_of_cards):
        self.cards = list_of_cards
    def open_cards(self):
        return self.cards
    def respond(self):
        return random.choice([ 'call', 'fold', int(10)])

class Human(Player):
    def respond(self):
        cl=[]
        for i in range(len(self.cards)):
            cl.append(self.cards[i].card)
        print("cards:",cl)
        print("Please input:'call','fold',or money[int]-->")
        res = input()
        return res
