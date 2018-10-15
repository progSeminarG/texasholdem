
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

class ShiraiAI(Player):
    def respond(self):
        num=[]
        suit=[]
        card=[]
        cl=self.cards+self.dealer.field
        (num,suit,card)=self.dealer.choice(cl)
        lt=[0]*14
        for c in num:
            lt[c]+=1
        rsp=10*(max(lt)-1)
        if rsp == 0:
            rsp='call'
        print("rsp---",rsp)
        return rsp
    
    
