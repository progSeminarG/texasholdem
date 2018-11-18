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
from texasholdem_Shirai2 import Shirai2AI
from texasholdem_Takahashi import TakahashiAI
from texasholdem_Human import Human
from texasholdem_Shiraiopt import ShiraioptAI
from texasholdem_Shirai import ShiraiAI

#  create list of players #
Player0 = Player()
Player1 = Player()
Player2 = TakahashiAI()
Player3 = KawadaAI()
Player4 = ShiraioptAI()
###########################

players_list = [Player0, Player1, Player2, Player3, Player4]
color=["yellow","darkgreen","blue","black","red","orange"]

game = Game(players_list)

output='st3.csv'

g=open("tour.txt","w")
g.close
f=open("rtvec.txt","w")
f.close
h=open("win.txt","w")
h.close
q=open(output,"w")
q.close

MAX=10000
n=100
dif = int(MAX/n)


###MAX回トーナメント###
f=open(output, "w")
f.write("num")
p=''
for i in range(len(players_list)):
    p += ", " + str(players_list[i].__class__.__name__)
p+="\n"
f.write(p)
f.close()

_i = 0
win=0
while _i < MAX: 
    f=open(output, "a")
    win_list = [0]*len(game.accounts)
    game = Game(players_list)
    label = [i.__class__.__name__ for i in players_list]
    c=0
    while game.accounts.count(0) < len(players_list)-1: #残り人数の設定
        game.play()
        c+=1
    win_list[game.accounts.index(max(game.accounts))] += 1
    ff=open("tour.txt","a")#回数記録ファイル
    ff.write(str(_i)+"\n")
    ff.close()
    q=str(_i)
    for i in range(len(win_list)):
        q+=", "+str(win_list[i])
    q+="\n"
    f.write(q)
    f.close()
    if _i-100>=0:
        df = pd.read_csv(output, header=0, encoding='utf-8')
        y=df.iloc[_i-100:_i,len(players_list)].values.tolist()
        win=sum(y)/100
        if win>0.55:#勝率がこれ以上なら終わりにする
            break
        gg=open("win.txt","a")
        gg.write(str(win)+"\n")
        gg.close()
    _i += 1
######


##以下では，トーナメント回数ごとの勝率を計算してグラフ化します．統計のための統計用プログラムです．
df = pd.read_csv(output, header=0, encoding='utf-8')

win_list = [0]*len(game.accounts)
num=dif # initial
y=[0]*len(players_list)
delta=100
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

