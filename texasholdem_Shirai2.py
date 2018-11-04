#! /usr/bin/env python3

import random
import numpy as np
import os

class Player(object):
    def get_know_dealer(self,dealer_input):
        self.dealer = dealer_input
    def get_hand(self,list_of_cards):
        self.cards = list_of_cards
    def open_cards(self):
        return self.cards
    def respond(self):
        return random.choice([ 'call', 'fold', int(10)])

class Shirai2AI(Player):
    def __init__(self):
        self.ct=0
        self.mat=[ np.array([[ 17.,   3.,  -2.,   3., -23.,  11.,  12., -17.,   2.,   9.],
       [ -9., -14., -12.,  -5., -35.,  16.,   0.,  -4., -10., -31.],
       [ 38., -10., -11.,  18., -39., -13.,  66.,  32.,  -8., -18.],
       [ -5.,  -3.,  -2., -43.,   6.,   9., -14.,  38., -40.,  38.],
       [ 20.,  15.,  -6.,  20.,   4.,  -9., -28.,   8.,  -6.,  -9.],
       [  5.,  25.,  19., -24.,   6., -14.,  14.,  -6.,  -6.,  36.],
       [-35.,  -3.,  29., -41., -35.,   7., -16.,  55.,   1.,  -1.],
       [  2., -52., -16.,  -5.,  19.,  18.,   5.,  25., -25.,   3.],
       [-41., -10., -51.,   5.,   3.,  -3.,  22.,  20.,  29., -31.]]),
 np.array([[ -8.,   6., -19., -23.,  44.,   2., -45.,  25.,   7.,   5.],
       [ 11.,  -7.,  20., -36.,  -8.,   6.,  21.,  -7.,  -8.,   2.],
       [ -2.,  -7.,  11., -41., -22., -14.,   0.,  19.,  -5., -45.],
       [ -2.,   1., -51., -25.,   4.,  14.,  -6., -22.,   7., -26.],
       [ -5., -12., -56.,  25.,  12., -10., -13.,  15.,   8.,  -3.],
       [-30.,  -1., -23.,  17.,   2.,   0.,  31.,  23.,   1.,  27.],
       [-25., -40.,  25.,  19., -11.,   7., -16.,  33., -26.,  36.],
       [ 23., -19.,  19.,  -8., -12.,  11.,  -5.,  -6.,  15., -51.],
       [ 13.,  30.,  20.,  13.,  13.,   9.,  41.,   8.,   6.,  15.],
       [  2., -24.,  -8., -19.,   1., -41.,  33.,  40., -24.,   3.]]),
 np.array([[-30.,  -3.,  15.,   5.,  -8., -20.,  24., -34.,  27.,  -6.],
       [-22.,  22., -23.,   3.,  44.,  10.,   5.,  -7.,   2.,  13.],
       [ -3.,   8., -14., -14., -13., -41.,  24.,   2., -61., -10.],
       [ -9.,  23.,  -4.,  -6.,  20.,  10.,   3., -36., -18.,  -3.],
       [-14.,  33.,  -9.,  -8.,  -7.,  20., -10., -35.,  15., -16.],
       [ 13., -34., -10.,  20.,   0., -45.,  17., -18.,   6., -11.],
       [ 13., -23., -16.,   1., -15., -21.,  20., -30.,  19., -10.],
       [ 10.,  37.,  15., -13.,  -7.,  23.,  32.,  29.,  38.,   4.],
       [ 30.,   5.,   7.,  31.,  30., -27.,  22.,  -6.,  15.,  -4.],
       [-15.,  -9.,  31., -17., -12., -31.,  -3.,  16.,   9.,  -4.]]),
 np.array([[ 22.,  -2.,  -2.,   7., -34.,   2., -39.,   1.,  54.,  10.],
       [  4., -32.,  -8.,  21.,  16.,  21.,   9.,   8.,  -1.,  37.],
       [  1., -16.,  29., -27.,  -2.,  -4., -25., -10.,  20.,   6.],
       [-16.,  -3., -13.,  -4., -21.,   7., -10.,  24., -10., -38.],
       [ 17., -22.,  21.,   2.,   3.,  18., -16.,  15.,  41., -24.],
       [ 53., -44.,   8.,   0., -23.,   6.,   5., -34., -37.,  19.],
       [ 24., -15., -12.,   4.,  -1.,   7.,  15.,  14.,  20.,   1.],
       [ 34., -38.,  -1.,  26.,  23.,  -3., -35.,  -5.,  25.,   5.],
       [ 46., -16., -11.,   9.,  -4.,  52.,  55.,   0.,  11.,  17.],
       [-32.,  -1.,  32.,  30.,  16.,   2.,  32.,  19.,  -9.,  -3.]]),
 np.array([[-18.,  20., -27.],
       [ 36.,  23.,  17.],
       [ 26.,   8.,  17.],
       [ -7., -31., -20.],
       [-41.,  23.,  14.],
       [-18.,  -1.,  33.],
       [-10., -19.,  -4.],
       [-25.,   4.,  28.],
       [ 42., -19.,  16.],
       [ -6.,   6.,  13.]])]


    def respond(self):
        if self.ct==0:
            self.inimon=\
                sum(self.dealer.list_of_money)/len(self.dealer.list_of_money)
            self.presc=self.inimon
            self.ct=1
        my_money=\
            self.dealer.list_of_money[
            self.dealer.list_of_players.index('Shirai2AI')] #arg1
        
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
        args=np.array([self.inimon, my_money, fsc, msc, fmax, mmax, mbet, maxmon, len(cards)]) #initial vector
        print("args--",args)
        
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
            rt=int( (my_money/0.67)*rtvec[2]-(my_money/2) )
        print("rt--",rt)
        
        self.presc=my_money
        return rt

    def relu(self,x):
        rl=np.maximum(0,x)
        return self.softmax(rl)

    
    def softmax(self,a):
        c=np.max(a)
        return np.exp(a-c)/np.sum(np.exp(a-c))
