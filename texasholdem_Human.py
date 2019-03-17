
#! /usr/bin/env python3

import random
import sys
from texasholdem_Player import Player

class Human(Player):
    def respond(self):
        print("cards:",[card.card for card in self.cards])
        while True:
            res = input("Please input 'call','fold',or money[int]: ")
            res = res.strip().replace("\'","").replace("\"","")
            if res == 'call' or res == 'fold':
                return res
            try:
                res = int(res)
                return res
            except:
                print("ERROR: bad input:",res)
