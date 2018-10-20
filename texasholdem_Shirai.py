
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
    def __init__(self):
        self.ct=0

    def respond(self):
        self.ct += 1
        SS = ['S', 'C', 'H', 'D']
        mon=0
        rsp=0
        for i in range(len(self.dealer.list_of_money)):
            mon += self.dealer.list_of_money[i]
        initial_money = mon/len(self.dealer.list_of_money)
        my_money = self.dealer.list_of_money[self.dealer.list_of_players.index('ShiraiAI')]
        num=[]
        suit=[]
        card=[]
        cl=self.cards+self.dealer.field
        (num,suit,card)=self.dealer.choice(cl)
        (num2,suit2,card2)=self.dealer.choice(self.dealer.field)
        lt=[0]*14
        for c in num:
            lt[c]+=1
        # pairs #
        k=num.count(2)
        l=num2.count(2)
        if k>l:
           rsp=my_money/10 * (k-l)
        m=num.count(3)
        n=num2.count(3)
        if k>l:
           rsp=my_money/10 * (m-n)*5
        m=num.count(4)
        n=num2.count(4)
        if k>l:
           rsp=my_money/10 * (m-n)*9
        
        # the others #
        if (lt.count(3)==1 and lt.count(2)>=1) or (lt.count(3)==2):
            rsp=my_money/10 * 8
        (s,li)=self.dealer.stlist(card)
        if s==1:
            rsp=my_money/10 * 6
        for s in SS:
            if suit.count(s)==5:
                rsp=my_money/10 * 7
                break
            if li.count(s)==5:
                rsp=my_money/1.1
                break
        rsp=int(rsp)
        if self.dealer.minimum_bet > my_money/3 and rsp <= my_money/10:
            rsp=self.rdchoice(70)
        if rsp == 0:
            rsp=self.rdchoice(70)
        warn=random.randrange(500)
        if warn == 1:
            rsp=my_money/1.1 # たまにはこういうこともする
        if self.ct < 3: # とりあえずcall
            rsp='call'
        return rsp
    
    def rdchoice(self,prob):
        rsp=0
        n=random.randrange(100)
        if n<=prob:
            rsp='call'
        else:
            rsp='fold'
        return rsp
    
