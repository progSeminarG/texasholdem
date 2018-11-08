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
        self.mat=[ np.array([[  0.,  -5.,  -5.,   3.,   7.,  -7.,   3.,   6.,  -1.,  -6.],
       [ -2.,  -3.,  -9.,   4.,   9.,  -2.,  -8.,   1.,   8.,  -7.],
       [  4.,   5.,  -2.,   5.,   4.,   4.,  -9., -13.,  -8.,   5.],
       [  5.,  -6.,  -2.,  -5.,  -8.,  -4.,  -2.,  -2.,   2., -10.],
       [-15.,   1.,  -4.,  -5.,   0.,  -7.,  -5.,   2.,   0.,   6.],
       [ -4.,   3., -12.,  -7.,  10.,   0.,   7.,  -7.,   9.,   3.],
       [  0.,   8., -14.,   3.,  -6.,  15.,  -2.,  -3.,  -2.,   2.],
       [  1.,  -1.,  -2.,   4.,  -7.,   0.,   1.,   1.,  -7.,  -1.],
       [  3.,  -1.,   4.,   6.,   4., -10., -12.,   0.,  -2.,   8.]]),
 np.array([[ -5.,  -8.,   2.,   0.,   1.,   4.,  -7.,  -3.,   2.,   9.],
       [ -6.,  -2.,   3.,  -4.,   2.,  -5.,  -5.,  10.,  -4.,   3.],
       [  1.,  -8.,  15.,   2.,   1.,  10.,   0.,  -8.,  -4.,   1.],
       [ -8.,  -9.,   1.,  10.,  -1.,  10.,  -7., -13.,   1.,   1.],
       [ -2.,   2.,  -2.,  -9.,  -9.,  -1.,  -1.,   0.,   7.,  -2.],
       [ -3.,  -2.,  -1., -15.,   6., -13.,  -3.,   0.,  -2.,  -1.],
       [ -1.,  -1.,   1., -13.,   3.,   3.,   6.,  -3.,   6.,   3.],
       [  0.,   4.,  -5.,  -3.,  -8.,   5.,  -6.,   1.,   2.,   0.],
       [ -7.,  -2.,   0.,   1.,  -4.,   6.,   7.,  10.,   2.,   5.],
       [ -6., -10.,  -3.,   1.,  -5.,  27.,   1.,  -4.,   6.,   0.]]),
 np.array([[ -2.,   3.,   2.,  -6.,   8.,  -3.,   6.,  11.,  -7.,   1.],
       [  2.,  -3.,  -4., -12.,   8.,  -2.,  12.,  16.,   5.,  -3.],
       [  8.,   4.,   0.,   0.,   1.,  -7.,   2.,  10.,  -3.,  -4.],
       [ -5.,  13.,   2., -15.,  -1.,  -1.,   7.,   2.,   0., -10.],
       [  1.,   5., -13.,  -5.,  -1.,  -4.,   4.,   5.,   0.,   3.],
       [ -1.,  12.,   2., -11.,  -2.,   7.,   2.,  -7.,   2.,  -5.],
       [  3.,  -9.,   0.,   2.,  -4.,   3.,   2.,   8.,   4.,  -7.],
       [  1.,   4.,   5.,  11.,  -3.,  12.,  -5., -14.,  -3.,   4.],
       [ -7.,   5.,   1.,  -5., -18.,   6.,  -4.,   6.,  -4.,  -9.],
       [ 10.,  -4.,  -2.,   6.,   9.,  11.,  -4.,   3.,  -4.,   3.]]),
 np.array([[  2.,   3.,   6., -11.,  -8.,   4.,  -9.,   6.,   6., -11.],
       [  6.,  -8.,   6.,   0.,   0.,   3.,  -4.,  -3., -13.,   2.],
       [  2.,  -2., -18.,  -7.,  13.,  -6.,   4.,   5.,  -2.,   4.],
       [  6.,   6.,  -1.,   2.,  -2.,  -1.,   5.,  -2.,  -9.,  -3.],
       [  0.,  -2.,   4.,  -3.,   3.,   4.,  -2.,   1.,  -6.,   7.],
       [  6.,   5.,   1.,   9.,  -4.,  -5.,  -2.,   3.,  -6.,  -2.],
       [ 11.,  -4.,   6.,   2.,   2.,  -9.,   2.,   9.,  -2.,  -6.],
       [  0.,  13.,   2.,   1.,   3.,  -5.,   5.,   5.,   2.,   1.],
       [  6.,  -4.,   2.,   3.,  -5.,   2.,  -6.,   2.,  -1.,  -2.],
       [ 14.,   3.,   0.,   4.,  13.,   0.,   2.,   6.,   5.,  -9.]]),
 np.array([[ -2., -13.,   9.],
       [ -5.,   0.,   3.],
       [  3.,   6.,  -2.],
       [ -6.,  -9.,  -6.],
       [  0.,   5., -11.],
       [  5.,   8.,   8.],
       [  4.,   2.,   2.],
       [ -3.,   2.,  -7.],
       [ -8.,  -1.,  -2.],
       [  0., -12.,   6.]])]

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
