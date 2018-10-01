#! /usr/bin/env python3

import random
import sys
from copy import deepcopy
from 


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
        for i in range(0, len(self.__players)):
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
        if len(self.field) != 0:
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
                    self.flag = self.flag+1  # レイズから1巡以降無視
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
            for i in range(0, len(self.__players)):
                if self.__money_each_player[i] <= self.bettingrate[i]:
                    self.bettingrate[i] = self.__money_each_player[i]
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
            for i in range(0, len(self.__players)):
                self.__money_each_player[i] = self.__money_each_player[i]-self.bettingrate[i]
            print(self.__money_each_player)
        print()
        print()
        '''kokomadenisemono'''

    # calculate best score from given set of cards
    #担当：白井．カードを受け取り，役とベストカードを返します．
    def calc_hand_score(self,cards):#7カードリストをもらう
        cards.sort()
        SS=['S','C','H','D']
        num_list=[0]*14
        suit_list=[0,0,0,0]
        rtCrads=[]
        
        (num,suit)=self.choice(cards)#num,suitのみを抜き出す
        pp=self.checkpairs(cards)#Kawadaさんの4cardsとか抜き出してリストにするやつ
        rpc1(cards)##REPLACE 1-->14
        
        #for flash:make flash_list
        for SUIT in SS:
            if suit.count(SUIT)>=5:#flash
                flash=1
                flash_list=[]
                for i in range(len(card_list)):#flashの数字だけ取り出す
                    if cards[14-i].suit==SUIT:
                        flash_list.append(cards[14-i].number)
        #for straightmake straight_list
        num_list=[0]*13
        for card in cards:#数字の個数カウント
            num_list[card-2]+=1
        for i in range(11):
            prod=num_list[14-i]*num_list[13-i]*num_list[12-i]*num_list[11-i]*num_list[10-i]
            if prod>=1:
                straight=1
                straight_list=list(range(10-i,15-i))
        
           ###############
        #####JUDGE BELOW#####
           ###############
        
        ##Straight-Flash###
        if straight==1:
            for SUIT in SS:
               if straight_list.count(SUIT)==5:#flash
                   score=8
                   rtCards=straight_list
        ##4cards##
        elif pp[0]>=1:
            score=7
            for i in range(13):
                if cards.count(14-i)==4:
                    rtCards=cards.pop(14-i)
                    rtCards.append(max(cards))
        ##Fullhouse##
        elif pp[1]==2:#3c *2
            score=6
            for i in range(13):
                if cards.count(14-i)==3:
                    rtCards=[14-i]*3
                    cards.remove(14-i)
                    break
            for i in range(13):
                if cards.count(14-i)==3:
                    rtCards+=[14-i]*2
                    cards.remove(14-i)
                    score=6
        elif pp[1]==1 and pp[2]>=1:#3c+pair
            score=6
            for i in range(13):
                if cards.count(14-i)==3:
                    rtCards=[14-i]*3
                    cards.remove(14-i)
                    break
            for i in range(13):
                if cards.count(14-i)==2:
                    rtCards+=[14-i]*2
                    cards.remove(14-i)
        ##Flash##
        elif flash==1:
            score=5
            rtCards=flash_list[len(flash_list)-5:len(flash_list)]
        ##Straight##
        elif straight==1:
            score=4
            rtCards=straight_list
        ##3cards##
        elif pp[1]==1:
            score=3
            for i in range(13):
                if cards.count(14-i)==3:
                    rtCards+=[14-i]*3
                    cards.remove(14-i)
            for i in range(2):
                rtCards.pop(max(cards))
        ##2pairs##
        elif pp[2]>=2:
            score=2
            for i in range(13):
                if cards.count(14-i)==2:
                    rtCards+=[14-i]*2
                    cards.remove(14-i)
                    break
            for i in range(13):
                if cards.count(14-i)==2:
                    rtCards+=[14-i]*2
                    cards.remove(14-i)
                    break
            for i in range(1):
                rtCards.pop(max(cards))
        ##1pair##
        elif pp[2]==1:
            score=1
            for i in range(13):
                if cards.count(14-i)==2:
                    rtCards+=[14-i]*2
                    cards.remove(14-i)
                    break
            for i in range(3):
                rtCards.pop(max(cards))
        #no pair :-@#
        else:
            score=0
            for i in range(5):
                rtCards.pop(max(cards))
        rpc2(rtCards)
        return (score,rtCards)

    def choice(self,card_list):#suit,numのみを取り出してリスト化
        SS=['S','C','H','D']
        suit=[0]*7
        num=[0]*7
        for i in range(len(card_list)):
            num[i]=card_list[i][0]
            suit[i]=card_list[i][1]
        return (num,suit)


    def judge_flash(self,cl1,cl2):###FLASH判定###
        rpc1(cl1)
        rpc1(cl2)
        (num1,suit1)=choice(cl1)
        (num2,suit2)=choice(cl2)
        for i in range(5):
            if max(num1)>max(num2):
                sc=0
            elif max(num1)>max(num2):
                sc=1
            elif max(num1)==max(num2):
                sc=2
        return sc

    def judge_straight(self,cl1,cl2):###STRAIGHT判定###
        rpc1(cl1)
        rpc1(cl2)
        if max(cl1)>max(cl2):
            sc=0
        elif max(cl1)<max(cl2):
            sc=1
        elif max(cl1)==max(cl2):
            sc=2
        return sc

    #Kawadaさんのもの
    def checkpair(self,any_cards):#ペアの評価方法
        pair=[0,0,0,0,0,0,0,0,0,0,0,0,0]#A~Kまでの13個のリスト要素を用意
        for i in range (0,len(any_cards)):#カードの枚数ぶんだけ試行
            pair[any_cards[i].number-1]=pair[any_cards[i].number-1]+1#カードのnumber要素を参照し先ほどのリストpairの対応要素のカウントを1つ増やす
        pairs=[0,0,0]#pairsは[4カード有無,3カードの有無,ペアの数]のリスト
        for i in range (0,13):#pairの要素A~13すべて順に参照
            if pair[i]==4:#その要素が４枚あるときpairs[0]のカウントを増やす
                pairs[0]=pairs[0]+1
            elif pair[i]==3:#同様に3枚
                pairs[1]=pairs[1]+1
            elif pair[i]==2:#同様に2枚
                pairs[2]=pairs[2]+1
        return pairs#pairsは[4カード有無,3カードの有無,ペアの数]のリスト

    def rpc1(cards):#最初に1-->14にする方
        for card in cards:
            card = (card+11)%13 + 2
        return cards
            
    def rpc2(cards):#最後に14-->1に戻す方
        for card in cards:
            card=(card-1)%13+1
        return cards

    @property
    def field(self):
        return self.__field
