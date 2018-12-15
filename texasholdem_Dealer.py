#! /usr/bin/env python3

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
        self.__NUM_CARDS = (
                self.__MAX_NUMBER_CARDS - self.__MIN_NUMBER_CARDS + 1)  # = 13
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
        for _num in range(self.__MIN_NUMBER_CARDS,
                             self.__MAX_NUMBER_CARDS+1):
            for _suit in self.__SUITS:
                _cards.append(Card(_suit, _num))
        return _cards

    @property
    def create_all_cards_stack(self):
        return self.__create_all_cards_stack()

    # open one card to a table
    def put_field(self):
        self.__field.append(self.__handling_cards.pop(0))

    # give player index 'ith' as int,
    # return next player's index who is in the game
    def __next_alive_player(self, ith):
        for _i in range(ith+1, self.__num_players):
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
    #   create pot
    #   calculate each hands' scores
    #   check winner and put ranking in each status
    #   distribute money to winners
    def final_accounting(self):
        # usually pots are created during the game, but here create at the last
        self.__create_pot()
        self.__calc_scores()
        self.__max_rank = self.__calc_ranking()
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

    # calcurate scores of each players' hands
    def __calc_scores(self):
        # calculate strength of each hands and save in each status
        for _status in self.__list_status:
            if _status.in_game:
                _seven_cards = _status.cards + self.field
                _status.score, _status.hand = (
                        self.calc_hand_score(_seven_cards))
            else:  # scores for fold players are set to -1
                _status.score = -1

    # set ranking in each status
    # return max value of ranking
    #   eg) [1,2,3,2,3] -> 3
    def __calc_ranking(self):
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
        # distribute from top winner
        for _ranking in range(1, self.__max_rank):
            # distribute from left pot
            for _ipot in range(len(self.__pot)):
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

    # calculate statistics
    # return:
    #     _suit_stat: {'S':<num>, 'C':<num>, ...}
    #     _num_stat: {1:<num>, 2:<num>, ...}
    def __cards_stat(self, card_list):
        _suit_stat = {'S': 0, 'C': 0, 'H': 0, 'D': 0}
        for _suit in self.__SUITS:
            _suit_stat[_suit] = sum(
                    1 for _card in card_list if _card.suit == _suit)
        _num_stat = {}
        for _num in range(1, self.__NUM_CARDS+1):
            _num_stat[_num] = sum(
                    1 for _card in card_list if _card.number == _num)
        _num_stat[self.__MAX_NUMBER_CARDS+1] = _num_stat[1]
        return _suit_stat, _num_stat

    # check card_list has Flash or not
    # Flash:
    #     return True and member of Flash hand (5 best cards)
    # not Flash:
    #     return False and None
    def __check_flash(self, suit_stat, cards):
        for _suit in self.__SUITS:
            if suit_stat[_suit] >= self.__NUM_PORKER_HAND:
                _flash_members = [
                        _card for _card in cards if _card.suit == _suit]
                _suit_stat, _num_stat = self.__cards_stat(_flash_members)
                return True, self.__best_set(_num_stat, _flash_members)
        return False, None

    # check if card_list is Straight
    # Straight:
    #     return True and member of Straight hand (5 best cards)
    # not Straight:
    #     return False and None
    def __check_straight(self, num_straight, num_stat, cards):
        # loop for 14, 13, ..., 5
        for _i in range(self.__MAX_NUMBER_CARDS+1, num_straight-1, -1):
            _prod = num_stat[_i] \
                    * num_stat[_i-1] \
                    * num_stat[_i-2] \
                    * num_stat[_i-3] \
                    * num_stat[_i-4]
            if _prod > 0:
                _straight_members = []
                for _k in range(_i, _i-5, -1):
                    if _k == 14:
                        _kk = 1
                    else:
                        _kk = _k
                    for _card in cards:
                        if _card.number == _kk:
                            _straight_members.append(_card)
                            break
                return True, _straight_members
        return False, None

    # return best set of cards (max: 5)
    # best: 4-Cards, Full-House, 3-Cards, 2-Pairs, 1-Pair, High-Card
    def __best_set(self, num_stat, cards):
        _sorted_num_stat = sorted(
                num_stat.items(), key=lambda x: (-x[1], -x[0]))
        _best_set_members = []
        _num_set = min(self.__NUM_PORKER_HAND, len(cards))
        for _num, _stat in _sorted_num_stat:
            for _card in cards:
                if self.__card_score(_card) == _num:
                    _best_set_members.append(_card)
                    if len(_best_set_members) == _num_set:
                        return _best_set_members

    def __card_score(self, card):
        if card.number == 1:
            return 14
        else:
            return card.number

    # put list of cards
    # return score of cards and its best hand:
    #   8: Straight-Flash, 7: 4-Cards, 6: Full-House, 5: Flash
    #   4: Straight, 3: 3-Cards, 2: 2-Pairs, 1: 1-Pair, 0: High-Card
    def calc_hand_score(self, cards):
        _num_set = min(self.__NUM_PORKER_HAND, len(cards))
        if len(cards) == 0:
            return 0, cards
        _suit_stat, _num_stat = self.__cards_stat(cards)

        # Straight-Flash
        _flash, _flash_hand = self.__check_flash(_suit_stat, cards)
        if _flash:
            _suit_stat_flash, _num_stat_flash = self.__cards_stat(cards)
            _straight, _straight_hand = self.__check_straight(
                    5, _num_stat_flash, _flash_hand)
            if _straight:  # straight-flash
                _mini_score = self.__card_score(_straight_hand[0]) / 14.0
                return 8.0 + _mini_score, _straight_hand

        # calculate best set and its statistics
        _best_set = self.__best_set(_num_stat, cards)
        _suit_stat_best, _num_stat_best = self.__cards_stat(_best_set)
        del _num_stat_best[14]  # delete {14:x} from dictionary

        # 4-cards
        if 4 in _num_stat_best.values():
            _mini_score = 4.0*self.__card_score(_best_set[0])
            _mini_score += self.__card_score(_best_set[-1])/14.0
            _mini_score /= 57.0
            return 7.0 + _mini_score, _best_set

        # Full-House
        if 3 in _num_stat_best.values() and 2 in _num_stat_best.values():
            _mini_score = 3.0*self.__card_score(_best_set[0])
            _mini_score += 2.0*self.__card_score(_best_set[-1])/28.0
            _mini_score /= 43.0
            return 6.0 + _mini_score, _best_set

        # Flash
        if _flash:
            for _i in range(_num_set):
                _mini_score += se.f__card_score(_best_set[_i]) / ((_i+1)*14)
            _mini_score /= 60.0
            return 5.0 + _min_score, _flash_hand

        # Straight
        _straight, _straight_hand = self.__check_straight(5, _num_stat, cards)
        if _straight:
            _mini_score = self.__card_score(_straight_hand[0]) / 14.0
            return 4.0 + _mini_score, _straight_hand

        # 3-Cards
        if 3 in _num_stat_best.values():
            _mini_score = 3.0*self.__card_score(_best_set[0])
            _mini_score += self.__card_score(_best_set[3])/14.0
            _mini_score += self.__card_score(_best_set[4])/28.0
            _mini_score /= 44.0
            return 3.0 + _mini_score, _best_set

        # 2-Pairs
        print("list(_num_stat_best.values()):",list(_num_stat_best.values()))
        if 2 <= list(_num_stat_best.values()).count(2):
            _mini_score = 2.0*self.__card_score(_best_set[0])
            _mini_score += 2.0*self.__card_score(_best_set[2])/28.0
            _mini_score += self.__card_score(_best_set[-1])/28.0
            _mini_score /= 66.0
            print("_mini_score:",_mini_score)
            return 2.0 + _mini_score, _best_set

        # 1-Pair
        if 2 in _num_stat_best.values():
            _mini_score = 2.0*self.__card_score(_best_set[0])
            _mini_score += self.__card_score(_best_set[2])/14.0
            _mini_score += self.__card_score(_best_set[3])/28.0
            _mini_score += self.__card_score(_best_set[4])/32.0
            _mini_score /= 30.0
            print("_mini_score:",_mini_score)
            return 1.0 + _mini_score, _best_set

        # High-Card
        _mini_score = 0.0
        for _i in range(_num_set):
            _mini_score += self.__card_score(_best_set[_i])/((_i+1)*14)
        _mini_score /= 3.0
        return 0.0 + _mini_score, _best_set

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
