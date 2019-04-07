
import random
from texasholdem_Dealer import Card
import csv

class KawadaAI(object):

    def __init__(self):
        self.datalist = [['phase', 'gap', 'symbol','money']]
        self.money_check = 100
        self.check_turn_number = 0
        # 精度は低いがトーナメントが始まってから何ゲーム目なのかを示す
        self.my_number = 0
        self.liar_status = 0
        self.two_turn_no_money = False
        self.cards = []
        # 所持金が無くてもカードが配布されているので
        # 2ターン連続で所持金0なのかを確認する目安

    def get_know_dealer(self, dealer_input):
        self.dealer = dealer_input  # need

    def get_hand(self, dealer_input):
        self.my_cards = dealer_input
        if self.dealer.list_of_money[self.my_number] == 100:
            self.money_check = self.dealer.list_of_money[self.my_number]
            self.check_turn_number = 0
        self.money_check = self.dealer.list_of_money[self.my_number]
        self.check_turn_number = self.check_turn_number + 1
        if self.two_turn_no_money == False and self.dealer.list_of_money[self.my_number] == 0:
            self.recording()
            self.two_turn_no_money = True
        else:
            pass

    def judge_case_check_data(self):
        self.two_turn_no_money == False
        if self.my_cards != self.cards:
            self.cards = self.my_cards
            self.playable_cards_count = 2
        elif self.playable_cards_count != len(self.get_playable_cards()):
            self.playable_cards_count = len(self.get_playable_cards())
        else:
            return 'not_record'
        return 'record'

    def search_money_class(self):
        full = sorted(self.dealer.list_of_money)
        j = self.dealer.list_of_money[self.my_number]
        for i in range(len(self.dealer.__players)):
            if full[i] == j:
                money_class = i
        return [full, money_class]

    def get_playable_cards(self):
        playable_cards = self.dealer.field+self.my_cards
        return playable_cards

    def get_players_number(self):  # self.my_numberを得る
        return self.dealer.get_position(self)

    def recording(self):
        phase = self.playable_cards_count
        gap = self.my_cards[0].number-self.my_cards[1].number
        if gap <= 0:
            gap = -gap
        if self.my_cards[0].suit == self.my_cards[1].suit:
            suit = 1
        else:
            suit = 0
        self.datalist.append([phase, gap, suit, self.dealer.list_of_money[self.my_number]])
        if self.check_turn_number == 1:
            with open("1st.csv", "w", newline = "") as f:    # ファイル名を1st.csvとする
                farstout = csv.writer(f)    # ファイルを書き込むためのオブジェクトにする
                farstout.writerows(self.datalist)

    def respond(self):
        if self.judge_case_check_data() == 'record':
            # self.recording()
            pass # 消す
        return 'call'
