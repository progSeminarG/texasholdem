#! /usr/bin/env python3

import argparse
import random
from copy import deepcopy
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from texasholdem_Plot import ReadPlot

from texasholdem_Dealer import Card, Dealer
from texasholdem_Play import Game
from texasholdem_Player import Player
from texasholdem_Kawada import KawadaAI
from texasholdem_Shirai import ShiraiAI
from texasholdem_Takahashi import TakahashiAI
from texasholdem_Human import Human


#  create list of players #
Player1 = ShiraiAI()
Player2 = TakahashiAI()
Player3 = KawadaAI()
Player4 = Player()
###########################

players_list = [Player1, Player2, Player3, Player4 ]
game = Game(players_list)
############WARNING!!!!#############
##Playのshuffleはコメントアウトしてから##
####################################

MAX=10000
n=50
dif = int(MAX/n) 

output='st2.csv'

###MAX回トーナメント###
f=open(output, "w")
f.write("num")
p=''
for i in range(len(players_list)):
    p += ", " + str(players_list[i].__class__.__name__)
p+="\n"
f.write(p)

_i = 0
while _i < MAX: 
    win_list = [0]*len(game.accounts)
    game = Game(players_list)
    label = [i.__class__.__name__ for i in players_list]
    while game.accounts.count(0) != len(players_list)-1: # death match
        game.play()
    for i in range(len(game.accounts)):
        if game.accounts[i] != 0:
            win_list[i] += 1
    p=str(_i)
    for i in range(len(win_list)):
        p+=", "+str(win_list[i])
    p+="\n"
    f.write(p)
    _i += 1
f.close()
######

# make data frame #
df = pd.read_csv(output, header=0, encoding='utf-8')
color=["red","green","blue","black"]

win_list = [0]*len(game.accounts)
num=dif # initial
y=[0]*len(players_list)
while num < MAX:
    j=0
    while j < 100 and j+num < MAX:
        for i in range(len(players_list)):
            print("num,i,j",num,i,j)
            y[i]=df.iloc[j:j+num,i+1].values.tolist()
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
#plt.legend(bbox_to_anchor=(1, 1), loc='upper right', fontsize=7)
plt.show()

