#! /usr/bin/env python3

import random
import sys
from copy import deepcopy


class Card(object):
    def __init__(self, suit, number):
        if suit not in ("S", "C", "H", "D"):
            # S: spade, C: club, H: heart, D: Diamond
            raise ValueError("ERROR: suit of card is not correct: " + str(suit))
        self.__suit = suit
        if number not in range(1, 14):
            raise ValueError("ERROR: number of card is not correct: " + str(number))
        self.__number = number

    @property
    def card(self):
        return (self.__suit, self.__number)

    @property
    def suit(self):
        return self.__suit

    @property
    def number(self):
        return self.__number


class Dealer(object):
    def __init__(self, players_input):
        self.__MIN_NUMBER_CARDS = 1  # smallest number of playing cards
        self.__MAX_NUMBER_CARDS = 13  # largest number of playing cards
        self.__SUITE = ['S', 'C', 'H', 'D']  # suit of playing cards
        self.__NUM_HAND = 2  # number of hands
        self.__INITIAL_MONEY = 500  # money each player has in initial
        self.__NUM_MAX_FIELD = 5  # maximum number of field
        self.__players = players_input  # instance of players
        self.__num_players = len(self.__players)  # number of players
        self.__num_handling_cards = self.__NUM_HAND * self.__num_players + self.__NUM_MAX_FIELD
        # number of cards that deal with
        self.__money_each_player = [self.__INITIAL_MONEY]*self.__num_players
        # money list of players
        self.__field = []
        for player in self.__players:
            player.get_know_dealer(self)
        self.smallb = 0
        self.bigb = 1
        self.money = 2
        self.minimum_bet = 2
        self.playercheck = [True]*len(self.__players)  # 返答を毎度更新し、降りた時に０にする
        self.active_plyers_list = []
        self.bettingrate = [0]*len(self.__players)  # 各々が賭けたお金を記録するリスト
        self.bettingrate[self.smallb] = 1
        self.bettingrate[self.bigb] = 2
        self.flag_atfirst = 0
        self.flag = 1
        for i in range(0,len(self.__players)):
            if self.__money_each_player[i] <= 0:
                self.playercheck = False  # お金が最初からなければ参加できない

    # create a deck
    def __create_all_cards_stack(self):  # create list of [S1, S2, ..., D13]
        _cards = []
        for inumber in range(self.__MIN_NUMBER_CARDS, self.__MAX_NUMBER_CARDS+1):
            for suit in self.__SUITE:
                _cards.append(Card(suit, inumber))
        return _cards

    # handout cards to each player
    def handout_cards(self):
        self.__field = []
        self.__all_cards = self.__create_all_cards_stack()
        self.__handling_cards = random.sample(self.__all_cards, self.__num_handling_cards)
        self.__players_cards = []  # each player's hand
        for player in self.__players:
            self.__players_cards.append(
                    [self.__handling_cards.pop(i) for i in range(self.__NUM_HAND)]
                    )
            player.get_hand(self.__players_cards[-1])

    # open one card to a table
    def put_field(self):
        self.__field.append(self.__handling_cards.pop(0))

    # ask players what they want to do "fold, call, raise"
    def get_response(self):
        self.flag = 0
        self.flag_atfirst = 0
        while self.flag < len(self.__players) and len(self.active_plyers_list) != 1:
            # while文でflagがプレイヤー数になるという次の工程に移行する条件を定義
            self.resplist = []
            self.active_plyers_list = []
            self.__resp = [
                    self.resplist.append(player.respond()) for player in self.__players
                    ]
            for i in range(0, len(self.__players)):
                # flagでレイズから次にレイズがあるまでカウントししている
                if self.flag >= len(self.__players) or len(self.active_plyers_list) == 1:
                    self.resplist[i] = "----"
                    self.flag = self.flag+1  #レイズから1巡以降無視
                elif self.flag_atfirst <= self.bigb and self.bigb != 3:
                    self.resplist[i] = "----"  # BBや前ターン最終レイズ者までの無視
                elif self.playercheck[i] is False:
                    self.resplist[i] = "----"
                    self.flag = self.flag+1  # 降りた人の無視
                elif self.resplist[i] == "fold":
                    self.playercheck[i] = False
                    self.flag = self.flag+1  # 降りる
                elif self.__money_each_player[i] <= self.money:
                    self.resplist[i] = "call"
                    self.flag = self.flag+1  # 掛け金に満たない場合で降りてないなら必然的にcall
                    self.bettingrate[i] = self.__money_each_player[i]
                elif self.resplist[i] == "call" or 0:
                    self.flag = self.flag+1  # お金あるときのcall
                    self.bettingrate[i] = self.money
                elif self.money+self.minimum_bet >= self.__money_each_player[i]:
                    self.bettingrate[i] = self.__money_each_player[i]
                    self.flag = 0
                    self.money = self.money+self.minimum_bet
                else:
                    if self.minimum_bet > self.resplist[i]:
                        # minimum_betより小さい金額ならminimum_betに修正
                        self.resplist[i] = self.minimum_bet
                        # もうお金が無くてALL_INしたい場合を追加予定
                        self.money = self.money+self.resplist[i]
                        # call金額の更新
                        self.flag = 0
                        self.bettingrate[i] = self.money
                    else:
                        # minimum_betの整数倍をレイズするように返値を修正
                        j = int(self.resplist[i]/self.minimum_bet)
                        if self.__money_each_player[i] <= self.money+self.minimum_bet*j:
                            j = int((self.__money_each_player[i]-self.money)/self.minimum_bet)+1
                        self.minimum_bet = self.minimum_bet*j
                        self.resplist[i] = self.minimum_bet
                            # minimum_betの更新
                        self.money = self.money+self.resplist[i]
                        # call金額の更新
                        self.flag = 0
                        self.bettingrate[i] = self.money
                    self.flag = self.flag+1
                if self.flag == len(self.__players):
                    self.bigb = i
                self.active_plyers_list = []
                for i in range(0, len(self.__players)):  # 降りなかった人をリストで返す
                    if self.playercheck[i] is True:
                        self.active_plyers_list.append('Player' + str(i+1))
                self.flag_atfirst = self.flag_atfirst + 1
            print(self.resplist, self.minimum_bet)
            print(self.bettingrate)

        print("next_turn_players_list", [self.active_plyers_list])
        # 次のターン参加する人のリスト
        print("betting_rate", self.money)  # レイズを繰り返した最終的にcallがそろった時の金額
        print("personal_betting_money", self.bettingrate)
        # 降りた人も含めてこの時点でいくら賭けたかのリスト
        print()
        # 各プレイヤーからの返答を聞き、次の field のオープンや、スコア計算の手前まで行う (櫻井くん)
        '''kokokaranisemono'''
        if len(self.field) == 5:
            for i in range(0,len(self.__players)):
                if self.__money_each_player[i] <= self.bettingrate[i]:
                    self.bettingrate[i] = self.__money_each_player[i]
                self.__money_each_player[i] = self.__money_each_player[i]-self.bettingrate[i]
            print(self.__money_each_player)
        print()
        print()
        '''kokomadenisemono'''

    # calculate best score from given set of cards
    def calc_hand_score(self):
        pass  # 手札の強さを計算するメソッド (白井くん)

    @property
    def field(self):
        return self.__field
