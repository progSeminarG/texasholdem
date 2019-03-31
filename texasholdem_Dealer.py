#! /usr/bin/env python3

import random
import sys
from copy import deepcopy
from itertools import cycle
from scipy.stats import rankdata
from math import ceil
from logging import getLogger, StreamHandler, DEBUG, INFO, WARNING


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


# define players status
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
        # case can put equal or can NOT put enough money
        else:
            _pot = self.__bet_money
            self.__bet_money = 0
            return True, _pot

    def return_money(self):
        self.__money += self.__bet_money

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


# class which automatically calculate score and best hands
# in given set of cards <_cards>
class Porker_Hand(object):
    def __init__(self, _cards):
        self.__NUM_PORKER_HAND = 5
        self.__SUITS = ['S', 'C', 'H', 'D']
        self.__MIN_NUMBER_CARDS = 1  # smallest number of playing cards
        self.__MAX_NUMBER_CARDS = 13  # largest number of playing cards
        self.__MAX_SS = 14.0  # MAX Single Score == score for 'A', 1
        self.__MAX_SS2 = self.__MAX_SS**2
        self.__MAX_SS3 = self.__MAX_SS**3
        self.__NUM_CARDS = (
                self.__MAX_NUMBER_CARDS - self.__MIN_NUMBER_CARDS + 1)  # = 13
        # calculate score and best hand when instance is created
        self.__score, self.__hand = self.__calc_hand_score(_cards)

    @property
    def score(self):
        return self.__score

    @property
    def best_hand(self):
        return self.__hand

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
        # _num_stat[14] = _num_stat[1]
        _num_stat[self.__MAX_NUMBER_CARDS+1] = _num_stat[1]
        return _suit_stat, _num_stat

    # return max number of common numbers and its number
    # as (<number>, <number of statistics>)
    def __max_stat_num(self, _num_stat):
        _sorted_num_stat = sorted(
                _num_stat.items(), key=lambda x: (-x[1], -x[0]))
        return _sorted_num_stat[0]

    # return best hand from _cards
    #   _num_cards:  number of cards selecting
    #   _num_stat:   statistics of card numbers
    #   _cards_ilst: set of cards for creating best hand
    def __best_set(self, _num_cards, _num_stat, _cards):
        # delete key 1:x (only 14:x is used for best hand)
        if 1 in _num_stat:
            del _num_stat[1]
        # select common numbers that number exceed _num_cards
        _exceed_commons = {
                _num: _stat for _num, _stat in _num_stat.items()
                if _stat >= _num_cards}
        _best_set_members = []
        # case exceed common numbers exist
        if len(_exceed_commons) > 0:
            _number = max(_exceed_commons.keys())
            for _card in _cards:
                if self.__card_score(_card) == _number:
                    _best_set_members.append(_card)
                    if len(_best_set_members) == _num_cards:
                        return _best_set_members
        else:
            _number, _stat_num = self.__max_stat_num(_num_stat)
            for _card in _cards:
                if self.__card_score(_card) == _number:
                    _best_set_members.append(_card)
            _num_cards -= _stat_num
            del _num_stat[_number]
            return _best_set_members + self.__best_set(
                    _num_cards, _num_stat, _cards)

    # check cards has Flash or not
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
                return True, self.__best_set(
                        self.__NUM_PORKER_HAND, _num_stat, _flash_members)
        return False, None

    # check cards has Straight or not
    # Straight:
    #     return True and member of Straight hand (5 best cards)
    # not Straight:
    #     return False and None
    def __check_straight(self, num_stat, cards):
        if len(cards) < 5:
            return False, None
        # loop for 14, 13, ..., 5
        for _i in range(self.__MAX_NUMBER_CARDS+1, 4, -1):
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

    # return given card score
    # input: Card class (only 1 card)
    # return: score
    def __card_score(self, card):
        if card.number == 1:
            return self.__MAX_SS
        else:
            return card.number

    # return score of cards and its best hand:
    #   8: Straight-Flash, 7: 4-Cards, 6: Full-House, 5: Flash
    #   4: Straight, 3: 3-Cards, 2: 2-Pairs, 1: 1-Pair, 0: High-Card
    def __calc_hand_score(self, cards):
        _num_set = min(self.__NUM_PORKER_HAND, len(cards))
        if len(cards) == 0:
            return 0, cards
        _suit_stat, _num_stat = self.__cards_stat(cards)

        # Straight-Flash (8.357 < score < 9.0)
        _flash, _flash_hand = self.__check_flash(_suit_stat, cards)
        if _flash:
            _suit_stat_flash, _num_stat_flash = self.__cards_stat(cards)
            _straight, _straight_hand = self.__check_straight(
                    _num_stat_flash, _flash_hand)
            if _straight:  # straight-flash
                _base_score = 8.0
                _mini_score = self.__card_score(_straight_hand[0]) / \
                    (self.__MAX_SS)
                return _base_score + _mini_score, _straight_hand

        # calculate best set and its statistics
        _best_set = self.__best_set(_num_set, deepcopy(_num_stat), cards)
        _suit_stat_best, _num_stat_best = self.__cards_stat(_best_set)
        del _num_stat_best[14]  # delete {14:x} from dictionary

        # 4-cards (7.158 < score < 8.067)
        if 4 in _num_stat_best.values():
            _base_score = 7.0
            _mini_score = self.__card_score(_best_set[0]) / \
                self.__MAX_SS
            if _num_set == 5:
                _mini_score += self.__card_score(_best_set[-1]) \
                            / self.__MAX_SS2
            return _base_score + _mini_score, _best_set

        # Full-House (6.158 < score < 7.067)
        if 3 in _num_stat_best.values() and 2 in _num_stat_best.values():
            _base_score = 6.0
            _mini_score = self.__card_score(_best_set[0]) / self.__MAX_SS
            _mini_score += self.__card_score(_best_set[-1]) / self.__MAX_SS2
            return _base_score + _mini_score, _best_set

        # Flash (5.527 < score < 6.072)
        if _flash:
            _base_score = 5.0
            _mini_score = 0.0
            for _i in range(_num_set):
                _mini_score += self.__card_score(_best_set[_i]) / \
                    (self.__MAX_SS**(_i+1))
            return _base_score + _mini_score, _flash_hand

        # Straight (4.357 < score < 5.0)
        _straight, _straight_hand = self.__check_straight(_num_stat, cards)
        if _straight:
            _base_score = 4.0
            _mini_score = self.__card_score(_straight_hand[0]) / self.__MAX_SS
            return _base_score + _mini_score, _straight_hand

        # 3-Cards (3.164 < score < 4.071)
        if 3 in _num_stat_best.values():
            _base_score = 3.0
            _mini_score = self.__card_score(_best_set[0]) / self.__MAX_SS
            for _i in range(3, _num_set):
                _mini_score += self.__card_score(_best_set[_i]) / \
                    (self.__MAX_SS**(_i-1))
            return _base_score + _mini_score, _best_set

        # 2-Pairs (2.225 < score < 3.071)
        if 2 <= list(_num_stat_best.values()).count(2):
            _base_score = 2.0
            _mini_score = self.__card_score(_best_set[0]) / self.__MAX_SS
            _mini_score += self.__card_score(_best_set[2]) / self.__MAX_SS2
            if _num_set == 5:
                _mini_score += self.__card_score(_best_set[4]) / self.__MAX_SS3
            return _base_score + _mini_score, _best_set

        # 1-Pair (1.169 < score < 2.071)
        if 2 in _num_stat_best.values():
            _base_score = 1.0
            _mini_score = self.__card_score(_best_set[0]) / self.__MAX_SS
            for _i in range(2, _num_set):
                _mini_score += self.__card_score(_best_set[_i]) / \
                    (self.__MAX_SS**(_i))
            return _base_score + _mini_score, _best_set

        # High-Card (0.527 < score < 1.072)
        _base_score = 0.0
        _mini_score = 0.0
        for _i in range(_num_set):
            _mini_score += self.__card_score(_best_set[_i]) / \
                (self.__MAX_SS**(_i+1))
        return _base_score + _mini_score, _best_set


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
        self.__num_games = self.__game_inst.num_games  # number of games
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
        # initial necessary bet
        self.__list_status[self.__SB].bet(int(self.__unit_bet/2))
        self.__list_status[self.__BB].bet(self.__unit_bet)

    # create list of [S1, S2, ..., D13]: whole deck
    def __create_all_cards_stack(self):
        _cards = []
        for _num in range(
                self.__MIN_NUMBER_CARDS, self.__MAX_NUMBER_CARDS+1):
            for _suit in self.__SUITS:
                _cards.append(Card(_suit, _num))
        return _cards

    # handout cards to each player
    def handout_cards(self, call_from):
        if call_from is not self.__game_inst:
            logger.info("Not permitted")
            return None
        self.__all_cards = self.__create_all_cards_stack()
        self.__handling_cards = random.sample(self.__all_cards,
                                              self.__num_handling_cards)
        for _status in self.__list_status:  # save cards in status
            _status.set_cards(
                    [self.__handling_cards.pop(i)
                        for i in range(self.__NUM_HAND)])
            self.__players[_status.index].get_hand(_status.cards)

    # open one card to a table
    def put_field(self,call_from):
        if call_from is not self.__game_inst:
            logger.info("Not permitted")
            return None
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

    # shift order of list: start: _ishift
    def __shift_list(self, _list, _ishift):
        return _list[_ishift:] + _list[:_ishift]

    # MAIN PLAYING METHOD
    # get responses from all players from starter
    # when all players answered after any raise, this method finishs
    def get_responses(self,call_from):
        if call_from is not self.__game_inst:
            logger.info("Not permitted")
            return None
        # create list of status with sequence order
        _cycle_status = self.__shift_list(self.__list_status, self.__starter)
        # loop for getting responses until everybody set
        for _status in cycle(_cycle_status):  # infinite loop of status
            if self.active_players_list.count(True) == 1:
                break
            # if the player is in game
            if _status.in_game:
                _response = self.__players[_status.index].respond()
                self.__handle_response(_status, _response)
            # if the last player
            if (_status.index + 1) % self.__num_players == self.__starter:
                break

    # handle response depending on each player's status
    def __handle_response(self, _status, _response):
        if _response == 'call':
            # bet minimum money otherwise put all (all-in)
            self.__bet_minimum(_status)
        elif _response == 'fold':
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

    # update _status with betting __minimum_bet
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
    def final_accounting(self,call_from):
        if call_from is not self.__game_inst:
            logger.infor("Not permitted")
            return None
        # usually pots are created during the game, but here create at the last
        self.__pot = self.__create_pot()
        self.__calc_scores()  # store hand's scores in each status
        self.__max_rank = self.__calc_ranking()
        self.__distribute_money()

    # create list of pot
    def __create_pot(self):
        _list_bet_money = sorted(
                set([_statu.bet_money for _statu in self.__list_status
                    if _statu.in_game]))
        _pot = [0] * len(_list_bet_money)
        for _status in self.__list_status:  # loop for status
            for _i, _limit in enumerate(_list_bet_money):
                _all_moved, _money = _status.move_to_pot(_limit)
                _pot[_i] += _money
                if _all_moved:  # if bet_money is 0 (empty)
                    _status.pot_rank = _i
                    break
        return _pot

    # calcurate scores of each players' hands
    def __calc_scores(self):
        # calculate strength of each hands and save in each status
        for _status in self.__list_status:
            if _status.in_game:
                _seven_cards = _status.cards + self.field
                _hand_inst = Porker_Hand(_seven_cards)
                _status.score = _hand_inst.score
                _status.hand = _hand_inst.best_hand
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
        # distribute money from top winner
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
        for _status in self.__list_status:
            _status.return_money()

    @property
    def field(self):
        return self.__field

    @property
    def list_of_players(self):
        return [i.__class__.__name__ for i in self.__players]

    @property
    def active_players_list(self):
        return [i.in_game for i in self.__list_status]

    @property
    def list_of_money(self):
        return [i.money for i in self.__list_status]

    def get_position(self, _your_inst):  # return index of _your_inst
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
    def num_games(self):  # current game number (how many game.play executed)
        return self.__num_games

    @property
    def response_list(self):
        _response_list = []
        for _status in self.__list_status:
            if _status.in_game:
                _response_list.append(_status.bet_money)
            else:
                _response_list.append(_status.in_game)
        return _response_list

    def __create_list_showup(self):
        _list_showup = []
        for _status in self.__list_status:
            if _status.in_game:
                _list_showup.append([_card.card for _card in _status.cards])
            else:
                _list_showup.append(None)
        return _list_showup

    def showup(self, call_from):
        if call_from is not self.__game_inst:
            logger.info("Not permitted")
            return None
        _list_alive = [_status.index for _status in self.__list_status if _status.in_game]
        _list_all_in = [_status.index for _status in self.__list_status if _status.money == _status.bet_money]
        if len(_list_alive) == 1 and len(_list_all_in) == 0:
            _list_showup = None
        else:
            _list_showup = self.__create_list_showup()
        for _player in self.__players:
            try:
                _player.get_result(_list_showup)
            except:
                pass



