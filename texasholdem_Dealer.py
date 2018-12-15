# ! /usr/bin/env python3

import random
import sys
from copy import deepcopy
import collections
from itertools import cycle
from collections import Counter
from scipy.stats import rankdata
from math import ceil


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
    def __init__(self, index, money):
        self.__index = index
        self.__money = money
        self.__bet_money = 0  # already bet money
        self.__pot_rank = 0  # rank of pot to get money after wining
        if self.__money > 0:
            self.in_game = True
        else:
            self.in_game = False

    def set_cards(self, cards):
        self.__cards = cards

    # <money> is removed from __money and added to __bet_money
    # if <money> is too big, all __money goes to __bet_money
    def bet(self, money):
        if money <= self.__money:
            self.__bet_money += money
            self.__money -= money
            return True
        else:
            self.__bet_money += self.__money
            self.__money = 0
            return False

    # move bet_money from status:
    # return T/F (all moved/still remain) and moved money
    def move_to_pot(self, money):
        # case can put enough money
        if money < self.__bet_money:
            self.__bet_money -= money
            return False, money
        # case can NOT put enough money
        else:
            _pot = self.__bet_money
            self.__bet_money = 0
            return True, _pot

    # increase __money:
    # called when money is distributed at last
    def add_money(self, money):
        self.__money += money

    @property
    def index(self):
        return self.__index

    @property
    def money(self):
        return self.__money

    @property
    def bet_money(self):
        return self.__bet_money

    @property
    def cards(self):
        return self.__cards

    @property
    def pot_rank(self):
        return self.__pot_rank

    @pot_rank.setter
    def pot_rank(self, pot_rank):
        self.__pot_rank = pot_rank


class Dealer(object):
    def __init__(self, game_inst, players_input):
        # FIXED PARAMETERS
        self.__MIN_NUMBER_CARDS = 1  # smallest number of playing cards
        self.__MAX_NUMBER_CARDS = 13  # largest number of playing cards
        self.__NUM_CARDS = self.__MAX_NUMBER_CARDS - self.__MIN_NUMBER_CARDS +1  # = 13
        self.__SUITS = ['S', 'C', 'H', 'D']  # suit of playing cards
        self.__NUM_HAND = 2  # number of hands
        self.__NUM_PORKER_HAND = 5  # comparing hands
        self.__NUM_MAX_FIELD = 5  # maximum number of field
        # import instances and other parameters
        self.__game_inst = game_inst
        self.__players = players_input  # instance of players
        self.__num_players = len(self.__players)  # number of players
        self.__num_handling_cards \
            = self.__NUM_HAND * self.__num_players + self.__NUM_MAX_FIELD
        # create list of players' status
        self.__list_status = [
                Status(_index, _money) for _index, _money
                in enumerate(self.__game_inst.accounts)]
        # card list on the field
        self.__field = []
        # get players know dealer's instance
        for player in self.__players:
            player.get_know_dealer(self)
        # DB, SB, BB positioning
        self.__DB = self.__game_inst.DB
        self.__SB = self.__next_alive_player(self.__DB)
        self.__BB = self.__next_alive_player(self.__SB)
        # initial starter is alive player next to BB
        self.__starter = self.__next_alive_player(self.__BB)
        self.__unit_bet = game_inst.minimum_bet  # initial niminum_bet (FIX)
        self.__minimum_bet = self.__unit_bet  # current betting cost
        self.__minimum_raise = self.__unit_bet  # current raising cost

    # handout cards to each player
    def handout_cards(self):
        self.__all_cards = self.__create_all_cards_stack()
        self.__handling_cards = random.sample(self.__all_cards,
                                              self.__num_handling_cards)
        for _status in self.__list_status:  # save cards in status
            _status.set_cards(
                    [self.__handling_cards.pop(i)
                        for i in range(self.__NUM_HAND)])
            self.__players[_status.index].get_hand(_status.cards)

    # create list of [S1, S2, ..., D13]: whole deck
    def __create_all_cards_stack(self):
        _cards = []
        for inumber in range(self.__MIN_NUMBER_CARDS,
                             self.__MAX_NUMBER_CARDS+1):
            for suit in self.__SUITS:
                _cards.append(Card(suit, inumber))
        return _cards

    # open one card to a table
    def put_field(self):
        #self.__field.append(self.__handling_cards.pop(0))
        if len(self.__field) == 0:
            self.__field.append(Card('S',1))
            return
        _max = max([i.number for i in self.__field])
        self.__field.append(Card('S',_max+1))

    # give player index 'ith' as int,
    # return next player's index who is in the game
    def __next_alive_player(self, ith):
        for _i in range(ith+1,self.__num_players):
            if self.__list_status[_i].in_game:
                return _i
        for _i in range(ith):
            if self.__list_status[_i].in_game:
                return _i
        return ith

    # MAIN PLAYING METHOD
    # get responses from all players from starter
    # when all players answered after any raise, this method finishs
    def get_responses(self):
        # create list of status with sequence order
        _cycle_status = self.__shift_list(self.__list_status, self.__starter)
        # loop for getting responses until everybody set
        for _status in cycle(_cycle_status):  # infinite loop of status
            if _status.in_game:
                _response = self.__players[_status.index].respond()
                self.__handle_response(_status, _response)
            if (_status.index + 1) % self.__num_players == self.__starter:
                break

    def __shift_list(self, _list, _ishift):
        return _list[_ishift:] + _list[:_ishift]

    # handle response depending on each player's status
    def __handle_response(self, _status, _response):
        if _response is 'call':
            # bet minimum money otherwise put all (all-in)
            self.__bet_minimum(_status)
        elif _response is 'fold':
            _status.in_game = False
        elif _response >= 0:
            _raise = _response
            # bet minimum money and raise if True is returned
            if self.__bet_minimum(_status):  # True if betting minimum success
                if _raise > _status.money:  # all-in case
                    _raise = _status.money
                # update minimum_bet and minimum_raise
                if self.__handle_raise(_raise):  # True if updated
                    # bet raise cost otherwise put all (all-in)
                    _status.bet(self.__minimum_raise)
                    # update starter
                    self.__starter = _status.index
        else:
            raise ValueError("respond 'call', 'fold', or raise money <int>")

    # bet minimum cost (self.__minimum_bet)
    def __bet_minimum(self, _status):
        _diff = self.__minimum_bet - _status.bet_money
        return _status.bet(_diff)  # bet method in status class

    # optimize raising money
    # raising money has to be multiply of previous rasing rate
    # otherwise return little less or minimum raising rate
    def __handle_raise(self, _raise):
        _factor = ceil(_raise / self.__minimum_raise)
        if _factor > 0:  # update minimum_raise, minimum_bet
            self.__minimum_raise = _factor * self.__minimum_raise
            self.__minimum_bet += self.__minimum_raise
            return True

    # DISTRIBUTE MONEY to WINNERS
    # create pot
    # calculate each hands
    # check winner and put ranking in each status
    # distribute money to winners
    def calc(self):
        # usually pots are created during the game, but here create at the last
        self.__create_pot()
        self.__calc_scores()
        self.__max_rank = self.calc_ranking()
        self.__distribute_money()

    # create list of pot
    def __create_pot(self):
        _list_bet_money = sorted(
                set([i.bet_money for i in self.__list_status if i.in_game]))
        self.__pot = [0] * len(_list_bet_money)
        for _status in self.__list_status:  # loop for status
            for _i, _limit in enumerate(_list_bet_money):
                _all_moved, _money = _status.move_to_pot(_limit)
                self.__pot[_i] += _money
                if _all_moved:  # if bet_money is 0 (empty)
                    _status.pot_rank = _i
                    break

    def __calc_scores(self):
        # calculate strength of each hands and save in each status
        for _status in self.__list_status:
            if _status.in_game:
                _seven_cards = _status.cards + self.field
                _status.score = self.calc_hand_score(_seven_cards)[0]
            else:  # scores for fold players are set to -1
                _status.score = -1

    def calc_ranking(self):
        # ranking of each player based on calculated hands
        _ranking = rankdata(
                [-_status.score for _status in self.__list_status],
                method='dense')
        # save ranking data in each status
        for _i, _status in enumerate(self.__list_status):
            _status.ranking = _ranking[_i]
        return max(_ranking)

    def __distribute_money(self):
        # re-order list of status with playing order: first to last player
        _ordered_status = self.__shift_list(self.__list_status, self.__SB)
        for _ranking in range(1, self.__max_rank):  # distribute from top winner
            for _ipot in range(len(self.__pot)):  # distribute from left pot
                _list = [
                        i for i in _ordered_status
                        if i.ranking == _ranking and i.pot_rank >= _ipot]
                _num = len(_list)
                if _num > 0:
                    # fraction is given to latter player
                    _extra = self.__pot[_ipot] % _num  # fraction
                    _list[-1].add_money(_extra)  # latter player
                    self.__pot[_ipot] -= _extra
                    _payout = int(self.__pot[_ipot]/_num)
                    for _status in _list:  # distribute money
                        _status.add_money(_payout)
                        self.__pot[_ipot] -= _payout
            if sum(self.__pot) == 0:
                break  # whole loop finished

    # calculate best score from given set of cards
    # 担当：白井．n 枚のカードリストを受け取り，役とベストカードを返します．

    # calculate statistics
    # return:
    #     _suit_stat: {'S':<num>, 'C':<num>, ...}
    #     _num_stat: {1:<num>, 2:<num>, ...}
    def __cards_stat(self, card_list):
        _suit_stat = {}
        for _suit in self.__SUITS:
            print("suit:",_suit)
            print([_card.suit for _card in card_list])
            _suit_stat[_suit] = sum(1 for _card in card_list if _card.suit == _suit)
        _num_stat = {}
        for _num in range(1,self.__NUM_CARDS+1):
            _num_stat[_num] = sum(1 for _card in card_list if _card.number == _num + 1)
        _num_stat[self.__MAX_NUMBER_CARDS+1] = _num_stat[1]
        return _suit_stat, _num_stat

    # check card_list has flash or not
    # flash:
    #     return True and member of flash hand
    # not flash:
    #     return False and None
    def __check_flash(self,suit_stat,cards):
        for _suit in self.__SUITS:
            if suit_stat[_suit] >= self.__NUM_PORKER_HAND:
                _flash_members = [_card for _card in cards if _card.suit == _suit]
                return True, _flash_members
        return False, None

    # check card_list has straight or not
    # straight:
    #     return True and member of straight hand
    # not straight:
    #     return False and None
    def __check_straight(self,num_straight,num_stat,cards):
        for _i in range(self.__MAX_NUMBER_CARDS+1,num_straight-1,-1):  # 14, 13, ..., 5
            _prod = num_stat[_i] \
                    * num_stat[_i-1] \
                    * num_stat[_i-2] \
                    * num_stat[_i-3] \
                    * num_stat[_i-4]
            if _prod > 0:
                _straight_members = []
                for _k in range(_i,_i-5,-1):
                    for _card in cards:
                        if _card.number == _k:
                            _straight_members.append(_card)
                            break
                return True, _straight_members
        return False, None

    # return best set of cards (max: 5)
    # best: 4-cards, Full-House, 3-cards, 2-pairs, 1-pair, high-card
    def __best_set(self,num_stat,cards):
        print(num_stat)
        print(type(num_stat))
        print('cards:',[i.card for i in cards])
        print([_i[1] for _i in num_stat.items()])
        _sorted_num_stat = sorted(num_stat.items(), key=lambda x: (-x[1],-x[0]))
        _best_set_members = []
        _num_set = min(self.__NUM_PORKER_HAND,len(cards))
        print("_num_set:",_num_set)
        for _num, _stat in _sorted_num_stat:
            for _card in cards:
                if _card.number == _num:
                    _best_set_members.append(_card)
                    if len(_best_set_members) == _num_set:
                        return _best_set_members



    def calc_hand_score(self, cards):
        if len(cards) == 0:
            return 0, cards
        _suit_stat, _num_stat = self.__cards_stat(cards)

        # flash and straight-flash
        _flash, _flash_hand = self.__check_flash(_suit_stat,cards)
        if _flash:
            _suit_stat_flash, _num_stat_flash = self.__cards_stat(cards)
            _straight, _straight_hand = self.__check_straight(5,_num_stat_flash,_flash_hand)
            if _straight:  # straight-flash
                return 8, _straight_hand
            else:  # flash
                return 5, _flash_hand

        # calculate best set which is also used later
        print("cards:",cards)
        _best_set = self.__best_set(_num_stat,cards)
        print("###???###")
        print(_best_set)
        # statistics of best set
        _suit_stat_best, _num_stat_best = self.__cards_stat(_best_set)

        # 4-cards
        if 4 in _num_stat_best:
            return 7, _best_set

        # Full-House
        if 3 in _num_stat_best and 2 in _num_stat_best:
            return 6, _best_set

        # straight
        _straight, _straight_hand = self.__check_straight(5,_num_stat,cards)
        if _straight:
            return 4, _straight_hand

        # 3-cards
        if 3 in _num_stat_best:
            return 3, _best_set

        # 2-pairs
        if 2 == _num_stat_best.values().count(2):
            return 2, _best_set

        # 1-pair
        if 2 in _num_stat_best:
            return 1, _best_set

        return 0, _best_set


    # for: calc_hand_score
    def choice(self, card_list):  # suit, num, cardのみを取り出してリスト化
        suit = [0]*len(card_list)
        num = [0]*len(card_list)
        card = [0]*len(card_list)
        for i in range(len(card_list)):
            num[i] = card_list[i].number
            suit[i] = card_list[i].suit
            card[i] = card_list[i].card
        return (num, suit, card)

    # for straight: make straight_list
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
            prod = num_list[14-i]*num_list[13-i] *\
                num_list[12-i]*num_list[11-i]*num_list[10-i]
            if prod >= 1:
                straight = 1  # st 宣言
                straight_list = num_list[10-i:14-i]
#                k = 0
#                for t in range(len(card_list)):
#                    if card_list[len(card_list)-1-t][1] == 14-i-k and k < 5:
#                        straight_list.append(card_list[len(card_list)-1-t])
#                        k += 1
                break
        return (straight, straight_list)

    # Kawadaさんのもの
    def checkpair(self, any_cards):  # ペアの評価方法
        pair = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # A~Kまでの13個のリスト要素を用意
        for i in range(0, len(any_cards)):  # カードの枚数ぶんだけ試行
            # カードのnumber要素を参照し先ほどのリストpairの対応要素のカウントを1つ増やす
            pair[any_cards[i].number-1] = \
                pair[any_cards[i].number-1]+1
        pairs = [0, 0, 0]  # pairsは[4カード有無, 3カードの有無, ペアの数]のリスト
        for i in range(self.__MAX_NUMBER_CARDS):  # pairの要素A~13すべて順に参照
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
    def compare_flash(self, cl1, cl2):  # == FLASH判定 shirai
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

    def compare_straight(self, cl1, cl2):  # == STRAIGHT判定 shirai
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

    # //////////////////////////////////////////////////
    # ここから2人を比較するメソッド（同役）
    # //////////////////////////////////////////////////
    def compair_high_cards(self, cardslist1, cardslist2):  # cardslist(5cards)
        number_list1 = self.convert_cardslist_to_numberlist(cardslist1)
        number_list2 = self.convert_cardslist_to_numberlist(cardslist2)
        array = [number_list1, number_list2]
        collect = [[], []]
        value = [[], []]
        counts = [[], []]
        for i in range(2):
            array[i].sort()
            array[i].reverse()
            collect[i] = collections.Counter(array[i])
            value[i], counts[i] = zip(*collect[i].most_common())
        decide_winner = False
        for i in range(len(value[0])):
            if value[0][i] > value[1][i]:
                return 0
            elif value[0][i] < value[1][i]:
                return 1
        if decide_winner is False:
            return 2
    '''
    5枚のカードリストを２つ受け取り、数字のリストへと変換
    枚数が多い数字順に数字を並べ替え、左からカードの強弱を比較
    先に前者のリストが強い判定が出れば ０
    後者のリストが強い判定が出れば １
    最後まで強弱の関係が無ければ ２

    ＜現状の問題点＞
    １が弱く扱われている → 途中で１を１４に変換する？
    '''

    def convert_cardslist_to_numberlist(self, cards_list):
        number_list = []
        for i in lenge(len(cards_list)):
            number_list.append(cards_list[i].number)
        '''
        for i in range(len(cardslist)):
            if number_list[i] == 1:
                number_list[i] =14
        '''
        return number_list
    # //////////////////////////////////////////////////
    # ここまで2人を比較するメソッド
    # //////////////////////////////////////////////////

    @property
    def field(self):
        return self.__field

    @property
    def list_of_players(self):
        return [i.__class__.__name__ for i in self.__players]

    def your_index(self, instance):
        for _i, _player in enumerate(self.__players):
            if _player == instance:
                return _i

    @property
    def active_players_list(self):
        return [i.in_game for i in self.__list_status]

    @property
    def list_of_money(self):
        return [i.money for i in self.__list_status]

    def get_position(self, _your_inst):
        return self.__players.index(_your_inst)

    @property
    def DB(self):
        return self.__DB

    @property
    def BB(self):
        return self.__BB

    @property
    def SB(self):
        return self.__SB

    @property
    def unit_bet(self):  # initial minimum bet
        return self.__unit_bet

    @property
    def minimum_bet(self):  # current minimum bet
        return self.__minimum_bet

    @property
    def minimum_raise(self):  # current minimum raise
        return self.__minimum_raise

    def DB_update(self):
        return self.__next_alive_player(self.__DB)

    @property
    def response_list(self):
        _response_list = []
        for _status in self.__list_status:
            if _status.in_game:
                _response_list.append(_status.bet_money)
            else:
                _response_list.append(_status.in_game)
        return _response_list

    # --- obsolete ---
    @property
    def resplist(self):
        return self.response_list

    @property
    def bettingrate(self):
        return self.response_list
