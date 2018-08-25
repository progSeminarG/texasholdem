#! /usr/bin/env python3

class TakahashiAI(object):
    def get_know_dealer(self,dealer_input):
        self.__dealer = dealer_input
        print(self.__dealer)
        print(self.__dealer.field)
        self.val = "hello"
        print(self.val)

    def get_hand(self,list_of_cards):
        self.__my_cards = list_of_cards
        print("my cards:",self.__my_cards)
        print("self=",self)
        print("@get_hand, self=",self)
        print("@attribute",dir(self))

    def respond(self):
        print("@respond, self=",self)
        print("@attribute",dir(self))
        print(self.__dealer)
        print(self.__dealer.field)
        self.__field = self.__dealer.field
        _list_of_cards = self.__field + self.__my_cards
        self.__find_flash(_list_of_cards)
        return "stay"
        
    def __calc_best_hand(self,list_of_cards):
        pass


    def __find_flash(self,list_of_cards):
        _num_suit = []
        for suit in ['S','C','H','D']:
            _num_suit.append(sum(card.suit==suit for card in list_of_cards))
        print("num of suit:",_num_suit)


from texasholdem_Dealer import Card, Dealer

player = TakahashiAI()

mydealer = Dealer([player])

mydealer.handout_cards()

player.respond()
#mydealer.get_response()
