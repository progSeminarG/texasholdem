#! /usr/bin/env python3

from texasholdem_Dealer import Card, Dealer
from texasholdem_Player import Player


player1 = Player()
player2 = Player()
player3 = Player()
player4 = Player()

player_list = [player1, player2, player3, player4]

mydealer = Dealer(player_list)
