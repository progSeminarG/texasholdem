#! /usr/bin/env python3

import random
import numpy as np
import os
import pandas as pd
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

class ShiraioptAI(Player):
    def __init__(self):
        self.ct=0
        self.score=0
        

    def respond(self):
        if self.ct==0:
            self.inimon=\
                sum(self.dealer.list_of_money)/len(self.dealer.list_of_money)
                #arg0
        self.my_money=\
            self.dealer.list_of_money[
            self.dealer.list_of_players.index('ShiraioptAI')]
            #arg1
        
        cards=self.dealer.field+self.cards
        _arg2_inst = Porker_Hand(self.dealer.field)
        fsc = _arg2_inst.score # arg2
        fbc = _arg2_inst.best_hand
        _arg3_inst = Porker_Hand(cards)
        msc = _arg3_inst.score # arg3
        mbc = _arg3_inst.best_hand
        
        fmax=max([_card.number for _card in fbc]+[0]) #arg4
        mmax=max([_card.number for _card in mbc]+[0]) #arg5
        if fmax==1:
            fmax=14
        if mmax==1:
            mmax=14
        mbet=self.dealer.minimum_bet #arg6
        maxmon=max(self.dealer.list_of_money) #arg7
        rest=sum(self.active_players_list) #arg8
        args=np.array([self.inimon, self.my_money, 100*fsc, 100*msc, 10*fmax, 10*mmax, mbet, maxmon, 10*len(cards),rest]) #initial vector
        
        print("args--",args)
        print("money--",self.dealer.list_of_money)
        '''
        # mutation
        x=random.random()
        if x < 0.00-1:
            self.make_plus(0.2)
            mat=np.load('mat.npy')
            plusmat=np.load('plusmat.npy')
            for i in range(len(mat)):
                mat[i] += plusmat[i]
            np.save('mat.npy',mat)
        '''
        # caluculation!
        self.mat=np.load('mat.npy')
        a1=np.dot(args,self.mat[0])
        #a1=self.relu(a1)
        a2=np.dot(a1,self.mat[1])
        a2=self.relu(a2)
        a3=np.dot(a2,self.mat[2])
        #a3=self.relu(a3)
        self.softmax(a3)
        a4=np.dot(a3,self.mat[3])
        a4=self.relu(a3)
        a5=np.dot(a4,self.mat[4])
        rtmat=self.relu(a5)

        rtvec=self.softmax(rtmat)
        print("rtmat--",rtmat)
        print("rtvec--",rtvec)
        
        f=open("rtvec.txt","a")
        f.write(str(rtvec)+"\n")
        f.close

        if max(rtvec)==rtvec[0]:
            rt='call'
        elif max(rtvec)==rtvec[1]:
            rt='fold'
        else:
            rt=int( (self.my_money/0.67)*rtvec[2]-(self.my_money/2) )
        print("#####rt--",rt)
        return rt

    def relu(self,x):
        rl=np.maximum(0,x)
        return rl
    
    def softmax(self,a):
        return (a)/(np.sum(a)+0.00001)
        
    def map_rand(self,n):
        x=random.random()
        if x < n:
            p=0.1
        elif x < n*2:
            p=-0.1
        else:
            p=0
        return p

    def make_plus(self,n):
        plusmat=np.load('plusmat.npy')
        for i in range(10): # plusmat
            for j in range(10):
                plusmat[1][i][j]=self.map_rand(n)
                plusmat[2][i][j]=self.map_rand(n)
                plusmat[3][i][j]=self.map_rand(n)
                if i < 9:
                    plusmat[0][i][j]=self.map_rand(n)
                if j < 3:
                    plusmat[4][i][j]=self.map_rand(n)
        np.save('plusmat.npy',plusmat)
