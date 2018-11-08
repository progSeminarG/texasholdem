#! /usr/bin/env python3

import random
import numpy as np
import os
import pandas as pd

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
        self.plusmat=[0]*5
        self.plusmat[0]=np.zeros((9,10))
        self.plusmat[1]=np.zeros((10,10))
        self.plusmat[2]=np.zeros((10,10))
        self.plusmat[3]=np.zeros((10,10))
        self.plusmat[4]=np.zeros((10,3))
        
        self.rtmat=np.zeros((3,1))

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
        (fsc, fbc)=self.dealer.calc_hand_score(self.dealer.field) #arg2
        (msc, mbc)=self.dealer.calc_hand_score(cards) #arg3
        
        fmax=max([fbc[i][1] for i in range(len(fbc))]+[0]) #arg4
        mmax=max([mbc[i][1] for i in range(len(mbc))]+[0]) #arg5
        if fmax==1:
            fmax=14
        if mmax==1:
            mmax=14
        mbet=self.dealer.minimum_bet #arg6
        maxmon=max(self.dealer.list_of_money) #arg7
        args=np.array([self.inimon, self.my_money, fsc, msc, fmax, mmax, mbet, maxmon, len(cards)]) #initial vector
            
        print("args--",args)
        
        if self.ct==0:
            self.ct=1
            self.presc=np.load("presc.npy")
            self.mat=np.load('mat.npy')
            print("pre,now--",self.presc,self.my_money)
            if self.my_money-self.presc<0 and self.presc!=100:
                print("USELESS!!")
                for i in range(len(self.mat)):
                    self.mat[i] -= self.plusmat[i]
        
                for i in range(10): # plusmat
                    for j in range(10):
                        self.plusmat[1][i][j]=self.rand()
                        self.plusmat[2][i][j]=self.rand()
                        self.plusmat[3][i][j]=self.rand()
                        if i < 9:
                            self.plusmat[0][i][j]=self.rand()
                        if j < 3:
                            self.plusmat[4][i][j]=self.rand()
        
            for i in range(len(self.mat)):
                self.mat[i]+=self.plusmat[i]
        
            np.save('mat.npy',self.mat)
            self.presc=np.save("presc.npy",self.my_money)
        
        a1=np.dot(args,self.mat[0])
        a1=self.relu(a1)
        a2=np.dot(a1,self.mat[1])
        a2=self.relu(a2)
        a3=np.dot(a2,self.mat[2])
        a3=self.relu(a3)
        a4=np.dot(a3,self.mat[3])
        a4=self.relu(a3)
        a5=np.dot(a4,self.mat[4])
        self.rtmat=self.relu(a5)
        
        rtvec=self.softmax(self.rtmat)
        print("rtvec--",rtvec)
        
        if max(rtvec)==rtvec[0]:
            rt='call'
        elif max(rtvec)==rtvec[1]:
            rt='fold'
        else:
            rt=int( (self.my_money/0.67)*rtvec[2]-(self.my_money/2) )
        print("rt--",rt)
        return rt

    def relu(self,x):
        rl=np.maximum(0,x)
        return self.softmax(rl)

    def rand(self):
        #rt=50*(np.random.rand()-np.random.rand())
        rt=random.choice([1,0,0,0,-1])
        return rt
    
    def softmax(self,a):
        c=np.max(a)
        return np.exp(a-c)/np.sum(np.exp(a-c))
