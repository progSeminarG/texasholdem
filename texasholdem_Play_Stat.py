#! /usr/bin/env python3

import argparse
import random
from copy import deepcopy
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from texasholdem_Plot import ReadPlot

from texasholdem_Dealer import Card, Dealer
from texasholdem_Play import Game
from texasholdem_Player import Player
from texasholdem_Kawada import KawadaAI
from texasholdem_Takahashi import TakahashiAI
from texasholdem_Human import Human
from texasholdem_Shiraiopt import ShiraioptAI
from texasholdem_Shirai import ShiraiAI

#  create list of players #
Player0 = Player()
Player1 = ShiraioptAI()
Player2 = TakahashiAI()
Player3 = KawadaAI()
Player4 = Player()
###########################

def map_rand(n):
    x=random.random()
    if x < n:
        p=0.1
    elif x < n*2:
        p=-0.1
    else:
        p=0
    return p

def make_plus(n):
    plusmat=np.load('plusmat.npy')
    for i in range(10): # plusmat
        for j in range(10):
            plusmat[1][i][j]=map_rand(n)
            plusmat[2][i][j]=map_rand(n)
            plusmat[3][i][j]=map_rand(n)
            if i < 9:
                plusmat[0][i][j]=map_rand(n)
            if j < 3:
                plusmat[4][i][j]=map_rand(n)
    np.save('plusmat.npy',plusmat)


players_list = [Player0, Player1, Player2, Player3, Player4]
color=["yellow","darkgreen","blue","black","red","orange"]

game = Game(players_list)

output='win.csv'

g=open("tour.txt","w")
g.close
f=open("rtvec.txt","w")
f.close
q=open(output,"w")
q.close

MAX=1000
n=20 # the num of stat

dif = int(MAX/n)


###MAX回トーナメント###
f=open(output, "w")
f.write("num, win_perc\n")
f.close()

_i = 0

make_plus(0.05)
mat=np.load('mat.npy')# 0
plusmat=np.load('plusmat.npy')# 0
prewin,maxwin=0

for i in range(len(mat)):
    mat[i] += plusmat[i]
np.save('mat.npy',mat)
while _i < MAX:
    inimon=100 #constant
    label = [i.__class__.__name__ for i in players_list]
    win=[0]*n # for winning percentage
    c=0
    mat=np.load('mat.npy')
    while c < n:
        game = Game(players_list)
        game.play()
        my_money=\
            self.dealer.list_of_money[
            self.dealer.list_of_players.index('ShiraioptAI')]
        if my_money > inimon:
            win[c]=1
            print(win,c)
    win_perc = win.count(1)/len(win)
    if win_perc > maxwin:
        maxwin=win_perc
        np.save('maxmat.npy',mat)
    if win_perc < prewin and _i!=0:
        plusmat=np.load('plusmat.npy')
        for i in range(len(mat)):
            mat[i] -= plusmat[i]
    make_plus(0.05)# remake
    plusmat=np.load('plusmat.npy')
    for i in range(len(mat)):
        mat[i] += plusmat[i]
    np.save('mat.npy',mat)    
    ff=open("tour.txt","a")#回数記録ファイル
    ff.write(str(_i)+"\n")
    ff.close()
    f=open(output,'a')#勝率ログ
    f.write(str(_i)+", "+str(win_perc)+"\n")
    f.close()
    prewin=win_perc
    _i += 1
######


##以下では，トーナメント回数ごとの勝率を計算してグラフ化します．統計のための統計用プログラムです．
df = pd.read_csv(output, header=0, encoding='utf-8')
x=list(range(MAX))
y=df.iloc[0:MAX,1].values.tolist()
plt.scatter(x, y, s=10, c='red')
plt.show()
'''
while num < _i:
    j=0
    while j < 10 and num+j < MAX and num-delta>=0:#試料数
        for i in range(len(players_list)):
            print("num,i,j",num,i,j)
            y[i]=df.iloc[num+j-delta:num+j,i+1].values.tolist()
            win_list[i]=sum(y[i])
        tot=sum(win_list)
        for i in range(len(win_list)):
            win_list[i]=win_list[i]/tot
        print("---",win_list)
        x=[num]
        for i in range(len(win_list)):
            plt.scatter(x, win_list[i], s=10, c=color[i], alpha=0.2) # label=players_list[i].__class__.__name__)
        j+=1
    num+=dif
plt.show()
'''



