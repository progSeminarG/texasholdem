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

### number of games ###
num_stat = 10
#######################

_i = 0
win_list = [0]*len(game.accounts)
while _i < num_stat: 
    print("===== tournament", _i, "=====")
    game = Game(players_list)
    label = [i.__class__.__name__ for i in players_list]
    while game.accounts.count(0) != len(players_list)-1: # death match
        game.play()
    for i in range(len(game.accounts)):
        if game.accounts[i] != 0:
            win_list[i] += 1
    _i += 1
# plot
plt.pie(win_list, labels = label, startangle=90,)
plt.show()

