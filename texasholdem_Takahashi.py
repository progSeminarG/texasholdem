#! /usr/bin/env python3

from texasholdem_Dealer import Card

class TakahashiAI(object):
    def get_know_dealer(self,dealer_input):
        self.__dealer = dealer_input

    def get_hand(self,list_of_cards):
        self.__my_cards = list_of_cards

    def respond(self):
        self.__field = self.__dealer.field
        _list_of_cards = self.__field + self.__my_cards
        _list_of_cards = sorted(_list_of_cards,key=lambda x: x.number)
        # test #
        _list_of_cards = [Card('S',1),Card('S',8),Card('D',11),Card('H',11),Card('S',12),Card('S',13)]
        # test /
        print([card.card for card in _list_of_cards])
        print(self.__determin_combination(_list_of_cards))
        return "stay"
        
    def __calc_best_hand(self,list_of_cards):
        pass

    def __determin_combination(self,list_of_cards):
        _flush_list = self.__find_flush(list_of_cards)
        if _flush_list:
            _straight_flush_list = self.__find_straight(_flush_list)
            if _straight_flush_list:
                return ('straight_flush',_straight_flush_list)
            else:
                return ('flush',_flush_list)
        _straight_list = self.__find_straight(list_of_cards)
        if _straight_list:
            return ('straight',_straight_list)
        _pairs = self.__find_pairs(list_of_cards)
        if _pairs:
            return ('pairs',_pairs)
        return None

            

    def __find_flush(self,list_of_cards):
        for suit in ['C','D','H','S']:
            _num = sum(card.suit==suit for card in list_of_cards)
            if _num >= 5:
                return [card for card in list_of_cards if card.suit == suit]
        return False

    def __find_straight(self,list_of_cards):
        # list_of_cards has to be sorted
        for card in list_of_cards:
            if card == list_of_cards[0]:
                _pre = card.number
                _num = 1
                _num_max = 1
                _list_of_straight = [card]
            elif card.number == _pre + 1:
                _num += 1
                if _num_max < _num:
                    _num_max = _num
                    _list_of_straight.append(card)
            elif card.number != _pre:
                _num = 1
                _list_of_straight = [card]
            else:
                _list_of_straight.append(card)
            _pre = card.number
        if _pre == 13 and list_of_cards[0].number == 1:
            _num += 1
            if _num_max < _num:
                _num_max = _num
            for card in list_of_cards:
                if card.number == 1:
                    _list_of_straight.append(card)
        if _num_max >= 5:
            return _list_of_straight
        else:
            return False

    def __find_pairs(self,list_of_cards):
        _list_of_pairs = []
        for number in range(1,13+1):
            _num = sum(card.number==number for card in list_of_cards)
            if _num >= 2:
                _list_of_pairs.append((number,_num))
        if len(_list_of_pairs) > 0:
            _list_of_pairs = sorted(_list_of_pairs,key=lambda x:x[1],reverse=True)
            return _list_of_pairs
        return False

    def __define_pairs(self,list_of_pairs):
        




#from texasholdem_Dealer import Card, Dealer

#player = TakahashiAI()

#mydealer = Dealer([player])

#mydealer.handout_cards()

#player.respond()
#mydealer.get_response()
