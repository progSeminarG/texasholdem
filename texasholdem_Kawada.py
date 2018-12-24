
import random
from texasholdem_Dealer import Card


class Player(object):  # とりあえず仮のベースのメゾットこれを継承する
    def get_know_dealer(self, dealer_input):
        self.dealer = dealer_input

    def get_hand(self, list_of_cards):
        self.my_cards = list_of_cards

    def respond(self):
        resp = ["call", "レイズ金額", "fold"]
        return resp[random.randint(0, 2)]


class KawadaAI(Player):  # プレイ可能カードのリスト

    def __init__(self):
        self.shirai_data = [[]]
        self.takahashi_data = [[]]
        self.money_check = 100
        self.check_turn_number = 0
        self.my_number = 0

    def get_hand(self, dealer_input):
        self.my_cards = dealer_input
#        # print([card.card for card in self.my_cards])
        if self.dealer.list_of_money[self.my_number] == 100:
            self.money_check = self.dealer.list_of_money[self.my_number]
            self.check_turn_number = 0
        self.check_turn_number = self.check_turn_number + 1


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

    def checkpair(self, any_cards):  # ペアの評価方法
        pair = [0]*13  # A~Kまでの13個のリスト要素を用意
        for i in range(0, len(any_cards)):  # カードの枚数ぶんだけ試行
            pair[any_cards[i].number-1] = pair[any_cards[i].number-1]+1
            # カードのnumber要素を参照し先ほどのリストpairの対応要素のカウントを1つ増やす
        pairs = [0, 0, 0]  # pairsは[4カード有無,3カードの有無,ペアの数]のリスト
        for i in range(0, 13):  # pairの要素A~13すべて順に参照
            if pair[i] == 4:  # その要素が４枚あるときpairs[0]のカウントを増やす
                pairs[0] = pairs[0]+1
            elif pair[i] == 3:  # 同様に3枚
                pairs[1] = pairs[1]+1
            elif pair[i] == 2:  # 同様に2枚
                pairs[2] = pairs[2]+1
        return pairs  # pairsは[4カード有無,3カードの有無,ペアの数]のリスト

    def ablepair(self):  # すべてのカードでの評価
        any_cards = self.get_playable_cards()
        return self.checkpair(any_cards)

    def fieldpair(self):  # 共通カードでの評価
        any_cards = self.dealer.field
        return self.checkpair(any_cards)

    def flashchecker(self):  # flashできるときに1を返す
        playable_cards = self.get_playable_cards()
        suitcounter = [0]*4
        check = 0
        for i in range(0, len(playable_cards)):
            if playable_cards[i].suit == 'S':
                suitcounter[0] = suitcounter[0]+1
            if playable_cards[i].suit == 'C':
                suitcounter[1] = suitcounter[1]+1
            if playable_cards[i].suit == 'H':
                suitcounter[2] = suitcounter[2]+1
            if playable_cards[i].suit == 'D':
                suitcounter[3] = suitcounter[3]+1
        for i in range(0, 4):
            if suitcounter[i] >= 5:
                check = 1
        return check

    def straightchecker(self):  # ストレートなら１を返す
        any_cards = self.get_playable_cards()
        counter = [0]*14
        for i in range(0, len(any_cards)):
            counter[any_cards[i].number-1] = counter[any_cards[i].number-1]+1
        counter[12] = counter[0]
        straight = [0, 0]
        straightlevel = 0
        for i in range(0, 10):
            if counter[i] * counter[i + 1]*counter[i + 2] == 1:
                if counter[i + 3]*counter[i + 4] == 1:
                    straight = 1
                    straightlevel = i
        return straight

    def shirai_vs_kawada(self):
        self.ret = False
        '''
        if self.money_check != self.dealer.list_of_money[self.my_number]:
            self.shirai_data.append([])
            self.money_check = self.dealer.list_of_money[self.my_number]
        self.shirai_data[-1].append(self.dealer.minimum_bet)'''
        if self.dealer.list_of_money[self.my_number] >= 500:
            self.ret = len(self.dealer.list_of_players)*100-self.dealer.list_of_money[self.my_number]

        # print()
        # print("shirai_date ", self.shirai_data)
        # print()

    def get_players_number(self):  # self.my_numberを得る
        return self.dealer.your_index(self)

    def respond(self):

        # print(self.check_turn_number)
        # プレイヤーのインスタンスの呼び出しが1回ということは確認できた
        self.my_number = self.get_players_number()

        flash = self.flashchecker()
        pairrate = []
        for i in range(0, 3):
            pairrate.append(self.ablepair()[i] - self.fieldpair()[i])
        if pairrate == [0, 0, 3]:
            pairrate = [0, 0, 2]
        straight = self.straightchecker()
        # print(self.dealer.active_players_list.count(True))
        if self.dealer.active_players_list.count(True) == 2:
            self.shirai_vs_kawada()
            if self.ret != False:
                return self.ret
        if self.dealer.minimum_bet == self.dealer.response_list[self.my_number]:
            return "call"  # 掛け金増やさないで参加できるなら参加する(絶対)
        elif self.dealer.minimum_bet == 2:
            return "call"
        elif (len(self.get_playable_cards())
              == 2 and self.ablepair() != [0, 0, 1] and self.my_cards[0].suit == self.my_cards[1].suit):
            if self.dealer.active_players_list.count(True) != 2:
                return 'fold'
            if self.dealer.minimum_bet >= random.randint(8, 12) and random.randint(0, 5) != 1:
                return "fold"
            return "call"

        elif self.check_turn_number <= 10 and len(self.dealer.field) == 0:
            return "fold"

        elif len(self.dealer.field) == 0:
            return 1  # 初ターン役ありならcall




        elif pairrate == [0, 0, 0] and straight == [0, 0] and flash == 0:
            return "fold"  # 役がないなら降りる
        elif pairrate == [1, 0, 0] or pairrate == [0, 1, 1]:
            money_potit = self.search_money_class()
            if money_potit[1] != 0:
                return self.money_potit[0][self.money_potit[1]-1]
            return self.dealer.list_of_money[self.my_number]
        elif self.dealer.active_players_list.count(True) == 2:
            if self.dealer.list_of_money[self.my_number] >= 400:
                return len(self.dealer.list_of_players)*100-self.dealer.list_of_money[self.my_number]

            return 'call'
        elif (self.dealer.minimum_bet /
              (self.dealer.minimum_bet-self.dealer.unit_bet) >= 10) and random.randint(0,3) != 0:
            return "fold"
        elif (len(self.dealer.field) == 5
              and pairrate == [0, 0, 1] and straight == [0, 0]) and flash == 0:
            return "fold"
        elif (self.dealer.minimum_bet >= sorted(self.dealer.list_of_money)
              [len(self.dealer.list_of_players)-2]-self.dealer.minimum_bet):
            return "call"
        elif pairrate == [1, 0, 0] or pairrate == [0, 1, 1]:
            money_potit = self.search_money_class()
            if money_potit[1] != 0:
                return self.money_potit[0][self.money_potit[1]-1]
            return self.dealer.list_of_money[self.my_number]
        elif pairrate == [0, 0, 2] or flash == 1:
            return self.dealer.minimum_bet*3
        return "call"  # とりあえず合う条件が無ければcall
        # ////////////未実装事項////////////
        # ポーカーフェイスではったりをかますplayerを洗い出したい
        # 最適化または単純化
        # 学習妨害案の検討
