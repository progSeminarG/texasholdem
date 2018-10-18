# ! /usr/bin/env python3

import random
import sys
from copy import deepcopy


class Card(object):
    def __init__(self, suit, number):
        if suit not in ("S", "C", "H", "D"):
            # S: spade, C: club, H: heart, D: Diamond
            raise ValueError("ERROR: suit of card is not correct: "
                             + str(suit))
        self.__suit = suit
        if number not in range(1, 14):
            raise ValueError("ERROR: number of card is not correct: "
                             + str(number))
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

class Status(object):
    def __init__(self, money):
        self.__money = money
        self.__bet_money = 0
        if self.__money > 0:
            self.in_game = True
            self.alive = True
        else:
            self.in_game = False
            self.alive = False

    def bet(self, money):
        self.__money -= money
        self.__bet_money += money
        return money

class Dealer(object):
    def __init__(self, game_inst, players_input):
        # FIXED PARAMETERS
        self.__MIN_NUMBER_CARDS = 1  # smallest number of playing cards
        self.__MAX_NUMBER_CARDS = 13  # largest number of playing cards
        self.__SUITE = ['S', 'C', 'H', 'D']  # suit of playing cards
        self.__NUM_HAND = 2  # number of hands
        self.__NUM_MAX_FIELD = 5  # maximum number of field

        self.__game_inst = game_inst
        self.__players = deepcopy(players_input)  # instance of players
        self.__num_players = len(self.__players)  # number of players
        self.__num_handling_cards \
            = self.__NUM_HAND * self.__num_players + self.__NUM_MAX_FIELD
        # player's hand money list
        self.__money_each_player = self.__game_inst.accounts
        # create list of players' status
        self.__list_status = [Status(_money) for _money in self.__game_inst.accounts]
        print(self.__money_each_player)
        # cards list on the field
        self.__field = []
        # get players know dealer's instance
        for player in self.__players:
            player.get_know_dealer(self)
        # DB, SB, BB positioning
        self.__DB = self.__game_inst.DB
        self.__SB = self.__next_alive_player(self.__DB)
        self.__BB = self.__next_alive_player(self.__SB)
        self.__betting_cost = game_inst.minimum_bet  # betting money at first
        # player can raise betting money the multiple of game_inst.minimum_bet
        self.minimum_bet = game_inst.minimum_bet
        self.playercheck = [True]*self.__num_players  # 返答を毎度更新し、降りた時にFalseにする
        self.active_players_list = self.__players  # the list of actionable players
        self.bettingrate = [0]*self.__num_players  # 各々が賭けたお金を記録するリスト
        self.bettingrate[self.__SB] = 1  # small-blined bet 1$ at first
        self.bettingrate[self.__BB] = 2  # big-blined bet 2$ at first
        self.__pot = self.__list_status[self.__SB].bet(self.minimum_bet/2)
        self.__pot = self.__list_status[self.__BB].bet(self.minimum_bet)
        # this flag is used to compair to big-blined position
        self.flag_atfirst = 0
        # this flag is used to check the count of "call" and "fold"
        self.flag = 1
        # list of players respond("call"/"fold"/number of raise)
        self.resplist = []
        for i in range(self.__num_players):
            if self.__money_each_player[i] <= 0:
                self.playercheck[i] = False
                self.__list_status[i].in_game = False
                # player who have no money can't play new game
        # print the player of small-blined position
        print("SB Player", self.__SB)
        # print the player of big-blined position
        print("BB Player", self.__BB)

    # give ith as int, return next player's index who is in the game
    def __next_alive_player(self, ith):
        _i = (ith + 1) % self.__num_players
        while self.__list_status[_i].alive is False:
            _i = (_i + 1) % self.__num_players
        return _i

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

    # number of players who play new game
    def __num_possible_players(self):
        return len([i for i in self.__list_status if i.alive])

#    def SB_kosin(self):  # number of small-blined(0~3)
    def DB_update(self):  # number of small-blined(0~3)
        return self.__next_alive_player(self.__DB)

    # ＜出てくるリストや変数＞
    # self.resplistはplayerの返答をリストにしたもの
    # "call"/"fold"/int() 参加資格が無いあるいは訊き始める条件にはない場合はskipし"----"を格納する
    # self.player_numberはリストの何番目のplayerなのかを表したもの　追加した返答をルールに従うように補正する際関数に渡す
    # self.flag self.flag_atfirstはそれぞれcallかfoldが続いたカウント、1ターン目のBB2ターン目以降のSBまでskipするためのカウンター
    #
    # <関数の構成>
    # playerの番号を得る
    # 必要があればskip("----"格納)してそれ以外はplayerに返答を訊きリストに格納
    # 格納した返答がルールに従ったものになるように修正する
    # 最後にフラグと生きているplayerのリストを更新する
    def get_response_from_one_person(self, player):
        self.player_number = len(self.resplist)  # know the number of player 0~4
        if self.flag >= self.__num_players or len(self.active_players_list) == 1:
            self.resplist.append("----")  # skip players after fill the conditions to move nexat turn
        elif self.flag_atfirst <= self.__BB and self.__BB != self.player_number - 1:
            self.resplist.append("----")  # skip untill BB at first turn
        elif self.playercheck[self.player_number] is False:
            self.resplist.append("----")  # skip the player
        else:
            self.resplist.append(player.respond())  # get response from player
        self.hentounohosei(self.player_number)  # correct response to follow the game rules
        self.flagnokosin(self.player_number)  # move flags
        self.active_players()  # renew active_plyers_list

    def hentounohosei(self, i):
        # while文でflagがプレイヤー数になるという次の工程に移行する条件を定義
        # flagでレイズから次にレイズがあるまでカウントししている
        if self.flag_atfirst <= self.__BB and self.__BB != self.player_number - 1:
            self.flag = self.flag-1
        elif self.resplist[i] == "----":
            pass
        elif self.resplist[i] == "fold":
            self.playercheck[i] = False  # 降りる
            self.__list_status[i].in_game = False
        elif self.__money_each_player[i] <= self.__betting_cost:
            self.resplist[i] = "call"  # 掛け金に満たない場合で降りてないなら必然的にcall
            self.bettingrate[i] = self.__money_each_player[i]
        elif self.resplist[i] == "call" or 0:  # お金あるときのcall
            self.bettingrate[i] = self.__betting_cost
        elif type(self.resplist[i]) is str:
            self.resplist[i] = "call"
            self.bettingrate[i] = self.__betting_cost
        elif self.__betting_cost+self.minimum_bet >= self.__money_each_player[i]:
            self.bettingrate[i] = self.__money_each_player[i]
            self.flag = 0
            self.__betting_cost = self.__betting_cost+self.minimum_bet
        else:
            if self.minimum_bet > self.resplist[i]:
                # minimum_betより小さい金額ならminimum_betに修正
                self.resplist[i] = self.minimum_bet
                self.__betting_cost = self.__betting_cost+self.resplist[i]
                # call金額の更新
                self.bettingrate[i] = self.__betting_cost
            else:
                # minimum_betの整数倍をレイズするように返値を修正
                j = int(self.resplist[i]/self.minimum_bet)
                if self.__money_each_player[i] <= self.__betting_cost+self.minimum_bet*j:
                    j = int((self.__money_each_player[i]-self.__betting_cost)/self.minimum_bet)+1
                self.minimum_bet = self.minimum_bet*j
                self.resplist[i] = self.minimum_bet
                # minimum_betの更新
                self.__betting_cost = self.__betting_cost+self.resplist[i]
                # call金額の更新
                self.bettingrate[i] = self.__betting_cost
            self.flag = 0

    def kakekinhosei(self):
        for i in range(0, self.__num_players):  # 最終的な掛け金の補正
            if self.__money_each_player[i] <= self.bettingrate[i]:
                self.bettingrate[i] = self.__money_each_player[i]

    def flagnokosin(self, i):
        self.flag = self.flag+1
        self.flag_atfirst = self.flag_atfirst+1

    def active_players(self):
        self.active_players_list = []
        for j in range(self.__num_players):  # 降りなかった人をリストで返す
            if self.playercheck[j] is True:
                self.active_players_list.append(self.__players[j])

    def printingdate(self):
        print("next_turn_players_list", [i.__class__.__name__ for i in self.active_players_list])
        # 次のターン参加する人のリスト
        print("betting_rate", self.__betting_cost)  # レイズを繰り返した最終的にcallがそろった時の金額
        print("personal_betting_money", self.bettingrate)
        # 降りた人も含めてこの時点でいくら賭けたかのリスト
        print()
        print()
        if len(self.field) == 5:
            print("--------------------------------------------")
            for i in range(0, self.__num_players):
                self.__money_each_player[i] = self.__money_each_player[i]-self.bettingrate[i]
            print("hanteimae-no-syozikin = ", self.__money_each_player)
            print("syousya-hantei-taisyousya = ", [i.__class__.__name__ for i in self.active_players_list])
            self.pot = sum(self.bettingrate)
            print("pot = ", self.pot)

    def get_responses(self):  # playersから返事を次のターンに進められるまで聞き続ける
        if len(self.field) != 0:
            self.flag = 0
            self.__BB = (self.__SB-1) % self.__num_players
        self.flag_atfirst = 0
        while self.flag < self.__num_players and len(self.active_players_list) != 1:
            # while文でflagがプレイヤー数になるという次の工程に移行する条件を定義
            if len(self.resplist) == self.__num_players:
                self.resplist = []
            # 1人ずつ聞いて補正して反映させる
            self.resp = [
                self.get_response_from_one_person(player) for player in self.__players
                        ]
            self.kakekinhosei()  # 持ち金を超えた掛け金の補正
            print(self.resplist)
        self.printingdate()  # 必要なデータをprint
        # ///////////////////////////////////////////////////////////////////////
        # /////////////////ここまでget_responses()関連////////////////////////////
        # ///////////////////////////////////////////////////////////////////////

    def calc(self):
        self.active_players()
        winner = []
        winner_num = []
        i = 0
        j = 0
        winners_cards_list = []
        winner_score = 0
        roll = []
        for player in self.__players:
            if self.playercheck[i] is True:
                seven_cards = self.__players_cards[self.__players.index(player)] + self.field
                roll.append(self.calc_hand_score(seven_cards)[0])
                if winner_score < roll[j]:
                    winner = [self.active_players_list[j]]
                    winner_num = []
                    winner_num.append(i)
                    winner_score = roll[j]
                    winners_cards_list = [[i, seven_cards]]
                elif winner_score == roll[j]:
                    winner_num.append(i)
                    winner.append(self.active_players_list[j])
                    winners_cards_list.append([i, seven_cards])
                print()
                j = j+1
            i = i+1
        print("--------------------------------------------")
        print([i.__class__.__name__ for i in self.active_players_list], " = ", roll)  # print finalist and their score
        '''
        if  len(winner) != 0:
            winners_cards_list = self.deside_winner_from_highcard(winners_cards_list, winner_score)
            # 同じ役の人たちを比較して新しいwinners_card_kistを返す関数を作成する 引数は[[player番号, カードリスト], [player番号, カードリスト]...], 役のスコア]
        '''
        print("///////////////////////////////////////////////")
        print("/////////////winner", [i.__class__.__name__ for i in winner], "////////////////")  # print winner
        print("///////////////////////////////////////////////")
        winning_money = int(self.pot/len(winner))
        for i in range(len(winner)):
            self.__money_each_player[winners_cards_list[i][0]] = self.__money_each_player[winners_cards_list[i][0]] + winning_money

    # calculate best score from given set of cards
    # 担当：白井．7枚のカードリストを受け取り，役とベストカードを返します．
    def calc_hand_score(self, cards):  # 7カードリストクラスをもらう
        SS = ['S', 'C', 'H', 'D']
        suit_list = [0, 0, 0, 0]
        rtCrads = []

        (num, suit, card_list) = self.choice(cards)  # クラスからnum, suit, cardを抜き出す
        # card_list = sorted(card_list, key = lambda x: x[1]) # # <<DEBUG MODE>>
        # print("card:", card_list)
        pp = self.checkpair(cards)  # Kawadaさんの4cardsとか抜き出してリストにするやつ
        #  # REPLACE 1-->14
        num = self.rpc1(num)
        num.sort()
        nc = self.rpcards1(card_list)
        card_list = nc
        card_list = sorted(card_list, key=lambda x: x[1])  # 2ndでsort

        flash = 0
        straight = 0
        straight_flash = 0
        # for flash:make flash_list
        for SUIT in SS:
            if suit.count(SUIT) >= 5:  # flash
                flash = 1
                flash_list = []
                for i in range(len(card_list)):  # flashの数字だけ取り出す
                    if card_list[6-i][0] == SUIT:
                        flash_list.append(card_list[6-i])
        (straight, straight_list) = self.stlist(card_list)
        if straight == 1 and flash == 1:
            (st, st_list) = self.stlist(flash_list)
            if st == 1:
                score = 8
                straight_flash = 1

        # == JUDGE BELOW ==
        rtCards = []
        # Straight-Flash
        if straight_flash == 1:
            rtCards = st_list
        # 4cards
        elif pp[0] >= 1:
            score = 7
            for i in range(self.__MAX_NUMBER_CARDS):
                if num.count(14-i) == 4:
                    for n in range(len(card_list)):
                        if card_list[6-n][1] == 14-i:
                            rtCards.append(card_list[6-n])
                            card_list.remove(card_list[6-n])
            rtCards.append(card_list[2])
        # Fullhouse
        elif pp[1] == 2:  # 3c *2
            score = 6
            c = 0
            for i in range(self.__MAX_NUMBER_CARDS):
                if num.count(14-i) == 3:
                    num.remove(14-i)
                    num.remove(14-i)
                    num.remove(14-i)
                    for n in range(len(card_list)):
                        if card_list[6-n][1] == (14-i):
                            rtCards.append(card_list[6-n])
                            card_list.remove(card_list[6-n])
                    break
            for i in range(self.__MAX_NUMBER_CARDS):
                if num.count(14-i) == 3:
                    for n in range(len(card_list)):
                        if card_list[n][1] == (14-i):
                            rtCards.append(card_list[3-n])
                            card_list.remove(card_list[3-n])
                            c += 1
                            if c == 2:  # 小さい方の3cは2個だけ取る
                                break
        elif pp[1] == 1 and pp[2] >= 1:  # 3c+pair
            score = 6
            for i in range(self.__MAX_NUMBER_CARDS):
                if num.count(14-i) == 3:
                    num.remove(14-i)
                    num.remove(14-i)
                    num.remove(14-i)
                    for n in range(len(card_list)):
                        if card_list[6-n][1] == (14-i):
                            rtCards.append(card_list[6-n])
                            card_list.remove(card_list[6-n])
                    break
            for i in range(self.__MAX_NUMBER_CARDS):
                if num.count(14-i) == 2:
                    for n in range(len(card_list)):
                        if card_list[3-n][1] == (14-i):
                            rtCards.append(card_list[3-n])
                            card_list.remove(card_list[3-n])
                    break
        # Flash
        elif flash == 1:
            score = 5
            rtCards = flash_list[len(flash_list)-5:len(flash_list)]
        # Straight
        elif straight == 1:
            score = 4
            rtCards = straight_list
        # 3cards
        elif pp[1] == 1:
            score = 3
            for i in range(self.__MAX_NUMBER_CARDS):
                if num.count(14-i) == 3:
                    for n in range(len(card_list)):
                        if card_list[6-n][1] == (14-i):
                            rtCards.append(card_list[6-n])
                            card_list.remove(card_list[6-n])
                    break
            for i in range(2):
                rtCards.append(card_list[3-i])
                card_list.remove(card_list[3-i])
        # 2pairs
        elif pp[2] >= 2:
            score = 2
            c = 0
            for i in range(self.__MAX_NUMBER_CARDS):
                if num.count(14-i) == 2 and c != 2:
                    c += 1
                    num.remove(14-i)
                    num.remove(14-i)
                    for n in range(len(card_list)):
                        if card_list[len(card_list)-1-n][1] == (14-i):
                            rtCards.append(card_list[len(card_list)-1-n])
                            rtCards.append(card_list[len(card_list)-2-n])
                            card_list.remove(card_list[len(card_list)-1-n])  # 可変だからこうなる
                            card_list.remove(card_list[len(card_list)-1-n])
                            break
            rtCards.append(card_list[2])
        # 1pair
        elif pp[2] == 1:
            score = 1
            for i in range(self.__MAX_NUMBER_CARDS):
                if num.count(14-i) == 2:
                    for n in range(len(card_list)):
                        if card_list[6-n][1] == 14-i:
                            rtCards.append(card_list[6-n])
                            card_list.remove(card_list[6-n])
                    break
            for i in range(3):
                rtCards.append(card_list[4-i])
                card_list.remove(card_list[4-i])
        # no pair
        else:
            score = 0
            rtCards = card_list[2:7]

        # RETURN!!
        nc = self.rpcards2(rtCards)
        rtCards = nc
        return (score, rtCards)

    # for: calc_hand_score
    def choice(self, card_list):  # suit, num, cardのみを取り出してリスト化
        SS = ['S', 'C', 'H', 'D']
        suit = [0]*len(card_list)
        num = [0]*len(card_list)
        card = [0]*len(card_list)
        for i in range(len(card_list)):
            num[i] = card_list[i].number
            suit[i] = card_list[i].suit
            card[i] = card_list[i].card
        return (num, suit, card)

    # for straight:make straight_list
    def stlist(self, card_list):
        card_list = sorted(card_list, key=lambda x: x[1])
        num = [0]*len(card_list)
        for i in range(len(card_list)):
            num[i] = card_list[i][1]
        straight_list = []
        straight = 0
        num_list = [0]*15
        for card in num:  # 数字の個数カウント
            num_list[card] += 1
        for i in range(10):
            prod = num_list[14-i]*num_list[self.__MAX_NUMBER_CARDS-i]*num_list[12-i]*num_list[11-i]*num_list[10-i]
            if prod >= 1:
                straight = 1  # st宣言
                k = 0
                for t in range(len(card_list)):
                    if card_list[len(card_list)-1-t][1] == 14-i-k and k < 5:
                        straight_list.append(card_list[len(card_list)-1-t])
                        k += 1
                break
        return (straight, straight_list)

    # Kawadaさんのもの
    def checkpair(self, any_cards):  # ペアの評価方法
        pair = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # A~Kまでの13個のリスト要素を用意
        for i in range(0, len(any_cards)):  # カードの枚数ぶんだけ試行
            pair[any_cards[i].number-1] = pair[any_cards[i].number-1]+1  # カードのnumber要素を参照し先ほどのリストpairの対応要素のカウントを1つ増やす
        pairs = [0, 0, 0]  # pairsは[4カード有無, 3カードの有無, ペアの数]のリスト
        for i in range(0, self.__MAX_NUMBER_CARDS):  # pairの要素A~13すべて順に参照
            if pair[i] == 4:  # lその要素が４枚あるときpairs[0]のカウントを増やす
                pairs[0] = pairs[0]+1
            elif pair[i] == 3:  # 同様に3枚
                pairs[1] = pairs[1]+1
            elif pair[i] == 2:  # 同様に2枚
                pairs[2] = pairs[2]+1
        return pairs  # pairsは[4カード有無, 3カードの有無, ペアの数]のリスト

    def rpc1(self, cards):  # 最初に1-->14にする方 引数はリスト
        rp = []
        for card in cards:
            card = (card+11) % 13 + 2
            rp.append(card)
        return rp

    def rpc2(self, cards):  # 最後に14-->1に戻す方 引数はリスト
        rp = []
        for card in cards:
            card = (card-1) % 13 + 1
            rp.append(card)
        return rp

    def rpcards1(self, cards):  # 最初に1-->14にする方 引数はカードタプルリスト
        nc = []
        for i in range(len(cards)):
            ss = cards[i][0]
            nn = (cards[i][1]+11) % 13 + 2
            nc.append((ss, nn))
        return nc

    def rpcards2(self, cards):  # 最後に14-->1に戻す方 引数はカードタプルリスト
        nc = []
        for i in range(len(cards)):
            ss = cards[i][0]
            nn = (cards[i][1]-1) % 13 + 1
            nc.append((ss, nn))
        return nc

    # == for: calc_hand_score
    def judge_flash(self, cl1, cl2):  # == FLASH判定 shirai
        num1 = []
        num2 = []
        for k in range(5):
            num1.append(cl1[k][1])
            num2.append(cl2[k][1])
        self.rpc1(num1)
        self.rpc1(num2)
        for i in range(5):
            if max(num1) > max(num2):
                sc = 0
                break
            elif max(num1) < max(num2):
                sc = 1
                break
            elif max(num1) == max(num2):
                sc = 2
                num1.remove(max(num1))
                num2.remove(max(num2))
        return sc

    def judge_straight(self, cl1, cl2):  # == STRAIGHT判定 shirai
        num1 = []
        num2 = []
        for i in range(5):
            num1.append(cl1[i][1])
            num2.append(cl2[i][1])
        num1 = self.rpc1(num1)
        num2 = self.rpc1(num2)
        if max(num1) > max(num2):
            sc = 0
        elif max(num1) < max(num2):
            sc = 1
        elif max(num1) == max(num2):
            sc = 2
        return sc

    @property
    def field(self):
        return self.__field

    @property
    def list_of_players(self):
        return [i.__class__.__name__ for i in self.__players]

    @property
    def list_of_money(self):
        return self.__money_each_player

    def get_position(self,_your_inst):
        return self.__players.index(_your_inst)

    @property
    def DB(self):
        return self.__DB

    @property
    def betting_cost(self):
        return self.__betting_cost

    # obsolete #
    @property
    def money(self):
        return self.__betting_cost
