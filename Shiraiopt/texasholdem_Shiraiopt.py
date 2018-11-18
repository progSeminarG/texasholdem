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

        self.rtmat=np.zeros((3,1))
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
        args=np.array([self.inimon, self.my_money, 100*fsc, 100*msc, 10*fmax, 10*mmax, mbet, maxmon, 10*len(cards)]) #initial vector
        
        print("args--",args)
        
        if self.ct==0:
            self.ct=1
            self.presc=np.load("presc.npy")
            self.mat=np.load('mat.npy')
            self.plusmat=np.load('plusmat.npy')
            print("pre,now--",self.presc,self.my_money)
            self.score=[self.presc,self.my_money]
            if self.my_money-self.presc<0 and self.presc!=100:#ダメなら作り直し
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
            np.save('plusmat.npy',self.plusmat)
        
        a1=np.dot(args,self.mat[0])
        a1=self.relu(a1)
        a2=np.dot(a1,self.mat[1])
        a2=self.relu(a2)
        a3=np.dot(a2,self.mat[2])
        a3=self.relu(a3)
        a4=np.dot(a3,self.mat[3])
        a4=self.relu(a3)
        a5=np.dot(a2,self.mat[4])
        rtmat=self.relu(a5)
        
        rtvec=self.softmax(rtmat)
        print("rtvec--",rtvec)

        self.presc=np.save("presc.npy",self.my_money)
        
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

    def rand(self):
        #rt=50*(np.random.rand()-np.random.rand())
        rt=random.choice([0,0,0,0,0.01,-0.01])
        return rt
    
    def softmax(self,a):
        return (a)/(np.sum(a)+0.00001)
