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
    def __init__(self, players_input, players_input2,game_input):
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
        '''self.__money_each_player = [self.__INITIAL_MONEY]*self.__num_players
        # money list of players
        '''
        self.__money_each_player = players_input2

        self.__field = []
        for player in self.__players:
            player.get_know_dealer(self)
        self.smallb = game_input
        while self.__money_each_player[self.smallb] == 0:
            self.smallb = (self.smallb+1)%len(self.__players)
        self.bigb = (self.smallb+1)%len(self.__players)
        while self.__money_each_player[self.bigb]  == 0:
            self.bigb = (self.bigb+1)%len(self.__players)
        self.money = 2
        self.minimum_bet = 2
        self.playercheck = [True]*len(self.__players)  # 返答を毎度更新し、降りた時に０にする
        self.active_plyers_list = []
        self.bettingrate = [0]*len(self.__players)  # 各々が賭けたお金を記録するリスト
        self.bettingrate[self.smallb] = 1
        self.bettingrate[self.bigb] = 2
        self.flag_atfirst = 0
        self.flag = 1
        self.resplist = []
        for i in range(0, len(self.__players)):
            if self.__money_each_player[i] <= 0:
                self.playercheck[i] = False
                # お金が最初からなければ参加できない
        print("small-blined ", self.smallb)
        print(" big -blined ", self.bigb)


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

    # //////////////////////////////////////////////////////////////////////////
    # /////////////////ここから先get_responses関連///////////////////////////////
    # //////////////////////////////////////////////////////////////////////////
    # ask players what they want to do "fold, call, raise"
    def syozikin_kosin(self):
        return self.__money_each_player

    def sanka_kano_ninzu(self):
        ninzu_at_first = 0
        for i in range(len(self.__players)):
            if self.__money_each_player[i] != 0:
                ninzu_at_first = ninzu_at_first+1
        return ninzu_at_first

    def smallb_kosin(self):
        return self.smallb

    def get_response_from_one_person(self, player):
        self.player_number = len(self.resplist)
        if self.flag >= len(self.__players) or len(self.active_plyers_list) == 1:
            self.resplist.append("----")  # レイズから1巡以降無視
        elif self.flag_atfirst <= self.bigb and self.bigb != 3:
            self.resplist.append("----")  # BBや前ターン最終レイズ者までの無視
        elif self.playercheck[self.player_number] is False:
            self.resplist.append("----")  # 降りた人の無視
        else:
            self.resplist.append(player.respond())
        self.hentounohosei(self.player_number)  # 返答をルールに従うように補正して解釈する
        self.flagnokosin(self.player_number)  # 各フラグを1足して条件を満たせば次のターンの目印を更新
        self.active_players()  # active_plyers_listを作成する

    def hentounohosei(self, i):
        # while文でflagがプレイヤー数になるという次の工程に移行する条件を定義
        # flagでレイズから次にレイズがあるまでカウントししている
        if self.flag_atfirst <= self.bigb and self.bigb != 3:
            self.flag = self.flag-1
        elif self.resplist[i] == "----":
            pass
        elif self.resplist[i] == "fold":
            self.playercheck[i] = False  # 降りる
        elif self.__money_each_player[i] <= self.money:
            self.resplist[i] = "call"  # 掛け金に満たない場合で降りてないなら必然的にcall
            self.bettingrate[i] = self.__money_each_player[i]
        elif self.resplist[i] == "call" or 0:  # お金あるときのcall
            self.bettingrate[i] = self.money
        elif self.money+self.minimum_bet >= self.__money_each_player[i]:
            self.bettingrate[i] = self.__money_each_player[i]
            self.flag = 0
            self.money = self.money+self.minimum_bet
        else:
            if self.minimum_bet > self.resplist[i]:
                # minimum_betより小さい金額ならminimum_betに修正
                self.resplist[i] = self.minimum_bet
                self.money = self.money+self.resplist[i]
                # call金額の更新
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
                self.bettingrate[i] = self.money
            self.flag = 0

    def kakekinhosei(self):
        for i in range(0, len(self.__players)):  # 最終的な掛け金の補正
            if self.__money_each_player[i] <= self.bettingrate[i]:
                self.bettingrate[i] = self.__money_each_player[i]

    def flagnokosin(self, i):
        self.flag = self.flag+1
        self.flag_atfirst = self.flag_atfirst+1
        # if self.flag == len(self.__players):
            # self.bigb = i

    def active_players(self):
        self.active_plyers_list = []
        for j in range(0, len(self.__players)):  # 降りなかった人をリストで返す
            if self.playercheck[j] is True:
                self.active_plyers_list.append('Player' + str(j+1))

    def printingdate(self):
        print("next_turn_players_list", [self.active_plyers_list])
        # 次のターン参加する人のリスト
        print("betting_rate", self.money)  # レイズを繰り返した最終的にcallがそろった時の金額
        print("personal_betting_money", self.bettingrate)
        # 降りた人も含めてこの時点でいくら賭けたかのリスト
        print()
        print()
        if len(self.field) == 5:
            print("--------------------------------------------")
            for i in range(0, len(self.__players)):
                self.__money_each_player[i] = self.__money_each_player[i]-self.bettingrate[i]
            print("hanteimae-no-syozikin = ", self.__money_each_player)
            print("syousya-hantei-taisyousya = ", self.active_plyers_list)
            pot = sum(self.bettingrate)
            print("pot = ", pot)

    def get_responses(self):  # playersから返事を次のターンに進められるまで聞き続ける
        if len(self.field) != 0:
            self.flag = 0
            self.bigb = (self.smallb-1)%len(self.__players)
        self.flag_atfirst = 0
        while self.flag < len(self.__players) and len(self.active_plyers_list) != 1:
            # while文でflagがプレイヤー数になるという次の工程に移行する条件を定義
            if len(self.resplist) == 4:
                self.resplist = []
            # 1人ずつ聞いて補正して反映させる
            self.resp = [
                self.get_response_from_one_person(player) for player in self.__players
                        ]
            self.kakekinhosei()  # 持ち金を超えた掛け金の補正
            print(self.resplist)
        self.printingdate()  # 必要なデータをprint
        #///////////////////////////////////////////////////////////////////////
        #/////////////////ここまでget_responses()関連////////////////////////////
        #///////////////////////////////////////////////////////////////////////


    # calculate best score from given set of cards
    #担当：白井．7枚のカードリストを受け取り，役とベストカードを返します．
    def calc_hand_score(self,cards):#7カードリストクラスをもらう
        SS=['S','C','H','D']
        suit_list=[0,0,0,0]
        rtCrads=[]

        (num,suit,card_list)=self.choice(cards)#クラスからnum,suit,cardを抜き出す
        pp=self.checkpair(cards)#Kawadaさんの4cardsとか抜き出してリストにするやつ
        ##REPLACE 1-->14
        num=self.rpc1(num)
        nc=[]
        for i in range(len(card_list)):
            ss=card_list[i][0]
            nn=(card_list[i][1]+11)%13 + 2
            nc.append((ss,nn))
        card_list=nc
        card_list=sorted(card_list, key=lambda x: x[1])#2ndでsort
        print(card_list)

        flash=0
        straight=0
        straight_flash=0
        #for flash:make flash_list
        for SUIT in SS:
            if suit.count(SUIT)>=5:#flash
                flash=1
                flash_list=[]
                for i in range(len(card_list)):#flashの数字だけ取り出す
                    if card_list[6-i][0]==SUIT:
                        flash_list.append(card_list[6-i])

        (straight,straight_list)=self.judge_straight(card_list)

        if straight==1 and flash==1:
            (st,st_list)=self.judge_straight(flash_list)
            if st==1:
                score=8
                straight_flash=1

           ###############
        #####JUDGE BELOW#####
           ###############

        rtCards=[]
        ##Straight-Flash###
        if straight_flash==1:
            rtCards=st_list
        ##4cards##
        elif pp[0]>=1:
            score=7
            for i in range(13):
                if num.count(14-i)==4:
                    for n in range(len(card_list)):
                        if card_list[n][1]==14-i:
                            rtCards.append(card_list[n])
            rtCards.append(card_list[2])
        ##Fullhouse##
        elif pp[1]==2:#3c *2
            score=6
            c=0
            for i in range(13):
                if num.count(14-i)==3:
                    num.remove(14-i)
                    num.remove(14-i)
                    num.remove(14-i)
                    for n in range(len(card_list)):
                        if card_list[6-n][1]==(14-i):
                            rtCards.append(card_list[6-n])
                            card_list.remove(card_list[6-n])
                    break
            for i in range(13):
                if num.count(14-i)==3:
                    for n in range(len(card_list)):
                        if card_list[n][1]==(14-i):
                            rtCards.append(card_list[3-n])
                            card_list.remove(card_list[3-n])
                            c+=1
                            if c==2:#小さい方の3cは2個だけ取る
                                break
        elif pp[1]==1 and pp[2]>=1:#3c+pair
            score=6
            for i in range(13):
                if num.count(14-i)==3:
                    num.remove(14-i)
                    num.remove(14-i)
                    num.remove(14-i)
                    for n in range(len(card_list)):
                        if card_list[6-n][1]==(14-i):
                            rtCards.append(card_list[6-n])
                            card_list.remove(card_list[6-n])
                    break
            for i in range(13):
                if num.count(14-i)==2:
                    for n in range(len(card_list)):
                        if card_list[3-n][1]==(14-i):
                            rtCards.append(card_list[3-n])
                            card_list.remove(card_list[3-n])
                    break
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
                if num.count(14-i)==3:
                    for n in range(len(card_list)):
                        if card_list[6-n][1]==(14-i):
                            rtCards.append(card_list[6-n])
                            card_list.remove(card_list[6-n])
                    break
            for i in range(2):
                rtCards.append(card_list[3-i])
                card_list.remove(card_list[3-i])
        ##2pairs##
        elif pp[2]>=2:
            score=2
            c=0
            for i in range(13):
                if num.count(14-i)==2 and c!=2:
                    c+=1
                    num.remove(14-i)
                    num.remove(14-i)
                    for n in range(len(card_list)):
                        if card_list[len(card_list)-1-n][1]==(14-i):
                            rtCards.append(card_list[len(card_list)-1-n])
                            rtCards.append(card_list[len(card_list)-2-n])
                            card_list.remove(card_list[len(card_list)-1-n])#可変だからこうなる
                            card_list.remove(card_list[len(card_list)-1-n])
                            break
            rtCards.append(card_list[2])
        ##1pair##
        elif pp[2]==1:
            score=1
            for i in range(13):
                if num.count(14-i)==2:
                    for n in range(len(card_list)):
                        if card_list[6-n][1]==14-i:
                            rtCards.append(card_list[6-n])
                            card_list.remove(card_list[6-n])
                    break
            for i in range(3):
                rtCards.append(card_list[4-i])
                card_list.remove(card_list[4-i])
        #no pair#
        else:
            score=0
            rtCards=card_list[2:7]

        ##RETURN!!##
        nc=[]
        for i in range(len(rtCards)):
            ss=rtCards[i][0]
            nn=(rtCards[i][1]-1)%13+1
            nc.append((ss,nn))
        rtCards=nc
        print(rtCards)
        return (score,rtCards)

    def choice(self,card_list):#suit,num,cardのみを取り出してリスト化
        SS=['S','C','H','D']
        suit=[0]*7
        num=[0]*7
        card=[0]*7
        for i in range(len(card_list)):
            num[i]=card_list[i].number
            suit[i]=card_list[i].suit
            card[i]=card_list[i].card
        return (num,suit,card)

    #for straight:make straight_list
    def judge_straight(self,card_list):
        card_list=sorted(card_list, key=lambda x: x[1])
        num=[0]*len(card_list)
        for i in range(len(card_list)):
            num[i]=card_list[i][1]
        straight_list=[]
        straight=0
        num_list = [0]*15
        for card in num:#数字の個数カウント
            num_list[card]+=1
        for i in range(10):
            prod = num_list[14-i]*num_list[13-i]*num_list[12-i]*num_list[11-i]*num_list[10-i]
            if prod >= 1:
                straight=1#st宣言
                k=0
                for t in range(len(card_list)):
                    if card_list[len(card_list)-1-t][1]==14-i-k and k<5:
                        straight_list.append(card_list[len(card_list)-1-t])
                        k+=1
                break
        return (straight,straight_list)


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

    def rpc1(self,cards):#最初に1-->14にする方
        rp=[]
        for card in cards:
            card = (card+11)%13 + 2
            rp.append(card)
        return rp

    def rpc2(self,cards):#最後に14-->1に戻す方
        rp=[]
        for card in cards:
            card=(card-1)%13+1
            rp.append(card)
        return rp

    @property
    def field(self):
        return self.__field
