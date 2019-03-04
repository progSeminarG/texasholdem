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
    def __init__(self):
        self.ct=0
        name=[0]*5
        self.mat=[0]*5
        for i in range(5):
            name[i]="maxmat"+str(i)+".npy"
            self.mat[i]=np.load(name[i])

    def respond(self):
        if self.ct==0:
            self.inimon=\
                sum(self.dealer.list_of_money)/len(self.dealer.list_of_money)
            self.presc=self.inimon
            self.ct=1
        my_money=\
            self.dealer.list_of_money[
            self.dealer.list_of_players.index('ShiraiAI')] #arg1
        
        cards=self.dealer.field+self.cards
        #        (fsc, fbc)=self.dealer.calc_hand_score(self.dealer.field) #arg2
        #        (msc, mbc)=self.dealer.calc_hand_score(cards) #arg3
        _arg2_inst = Porker_Hand(self.dealer.field)
        fsc = _arg2_inst.score
        fbc = _arg2_inst.best_hand
        _arg3_inst = Porker_Hand(cards)
        msc = _arg3_inst.score
        mbc = _arg3_inst.best_hand
        
#        fmax=max([fbc[i][1] for i in range(len(fbc))]+[0]) #arg4
#        mmax=max([mbc[i][1] for i in range(len(mbc))]+[0]) #arg5
        fmax=max([_card.number for _card in fbc]+[0]) #arg4
        mmax=max([_card.number for _card in mbc]+[0]) #arg5
        if fmax==1:
            fmax=14
        if mmax==1:
            mmax=14
        mbet=self.dealer.minimum_bet #arg6
        maxmon=max(self.dealer.list_of_money) #arg7
        rest=sum(self.dealer.active_players_list)
        args=np.array([self.inimon, my_money, 100*fsc, 100*msc, 10*fmax, 10*mmax, mbet, maxmon, 10*len(cards),rest])
        #print("args--",args)
        
        a1=np.dot(args,self.mat[0])
        a1=self.relu(a1)
        a2=np.dot(a1,self.mat[1])
        a2=self.relu(a2)
        #a3=np.dot(a2,self.mat[2])
        #a3=self.relu(a3)
        #a4=np.dot(a3,self.mat[3])
        #a4=self.relu(a3)
        a5=np.dot(a2,self.mat[4])
        rtmat=self.relu(a5)
        
        rtvec=self.softmax(rtmat)
        '''
        if len(cards)==7:
            f=open("rtvec.txt","a")
            f.write(str(args)+"\n")
            f.write(str(rtvec)+"\n")
            f.close()
        '''
        if max(rtvec)==rtvec[0]:
            rt='call'
        elif max(rtvec)==rtvec[1]:
            rt='fold'
        else:
            rt=int( (my_money/0.67)*rtvec[2]-(my_money/2) )
        #print("rt--",rt)
        #print(self.dealer.list_of_money)
        
        self.presc=my_money
        return rt

    def relu(self,x):
        rl=np.maximum(0,x)
        return rl

    def softmax(self,a):
        c=np.min(a)
        return (a)/(np.sum(a)+0.0001)
