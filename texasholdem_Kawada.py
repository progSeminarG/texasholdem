
'''
基本ルール
　ポーカーのルールは意外に知られていない。そのため基本的なルールを書いてみます。
１，ポーカーの役
　(1)ノーペア　＝　以下のどの役も無いもの
　(2)ワンペア　＝　５枚の中に同じ数字のカードが２枚ある（ペア）もの
　(3)ツーペア　＝　５枚の中に２種類のペアがあるもの
　(4)スリーカード　＝　５枚の中に同じ数字のカードが３枚あるもの
　(5)ストレート　＝　５枚すべてが連続した数字のもの
　(6)フラッシュ　＝　５枚すべてが同じスート（スペード・ダイアなど）のもの
　(7)フルハウス　＝　５枚がペアとスリーカードになっているもの
　(8)フォーカード　＝　５枚の中に同じ数字が４枚あるもの
　(9)ストレートフラッシュ　＝　５枚のカードがフラッシュとストレートになっているもの

２、カードの強さ
　(強)Ａ＞Ｋ＞Ｑ＞Ｊ＞10＞９＞８＞７＞６＞５＞４＞３＞２(弱)
'''

'''
＜評価メソッド＞
ペアチェックで4カード→フルハウス→3カードペア(セット数も)の判定
フラッシュの有→リスト抜き出す　無→4カードなら終わり　ストレートへ
同じ役内の強弱'''





import random

class Player(object):#とりあえず仮のベースのメゾットこれを継承する
    def get_know_dealer(self,dealer_input):
        self.dealer = dealer_input
    def get_hand(self, list_of_cards):
        self.my_cards = list_of_cards
    def respond(self):
        resp=["call","レイズ金額","fold"]
        return resp[random.randint(0,2)]
        #お金の関係はまだ理解してないので未入力


class KawadaAI(Player):#プレイ可能カードのリスト
    def get_playable_cards(self):
        playable_cards=[]
        for i in range (0,len(self.dealer.field)):
            playable_cards.append(self.dealer.field[i])
        for i in range (0,len(self.my_cards)):
            playable_cards.append(self.my_cards[i])
        return playable_cards


    def checkpair(self,any_cards):#ペアの評価方法
        pair=[0,0,0,0,0,0,0,0,0,0,0,0,0]
        for i in range (0,len(any_cards)):
            pair[any_cards[i].number-1]=pair[any_cards[i].number-1]+1
        pairs=[0,0,0]
        for i in range (0,13):
            if pair[i]==4:
                pairs[0]=pairs[0]+1
            elif pair[i]==3:
                pairs[1]=pairs[1]+1
            elif pair[i]==2:
                pairs[2]=pairs[2]+1
        return pairs


    def ablepair(self):#すべてのカードでの評価
        any_cards=self.get_playable_cards()
        return self.checkpair(any_cards)
    def fieldpair(self):#共通カードでの評価
        any_cards=self.dealer.field
        return self.checkpair(any_cards)


    def flashchecker(self): #flashできるときに1を返す
        playable_cards=self.get_playable_cards()
        suitcounter=[0,0,0,0]
        check=0
        for i in range (0,len(playable_cards)):
            if playable_cards[i].suit=='S':
                suitcounter[0]=suitcounter[0]+1
            if playable_cards[i].suit=='C':
                suitcounter[1]=suitcounter[1]+1
            if playable_cards[i].suit=='H':
                suitcounter[2]=suitcounter[2]+1
            if playable_cards[i].suit=='D':
                suitcounter[3]=suitcounter[3]+1
        for i in range (0,4):
            if suitcounter[i]>=5:
                check=1
        return check

    def straightchecker(self):#ストレートなら１を返す
        any_cards=self.get_playable_cards()
        counter=[0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for i in range (0,len(any_cards)):
            counter[any_cards[i].number-1]=counter[any_cards[i].number-1]+1
        counter[12]=counter[0]
        straight=[0,0]
        straightlevel=0
        for i in range (0,9):
            if counter[i]!=0:
                if counter[i+1]!=0:
                    if counter[i+2]!=0:
                        if counter[i+3]!=0:
                            if counter[i+4]!=0:
                                straight[0]=1
        '''for i in range (0,10):
            if counter[i]*counter[i+1]*counter[i+2]*counter[i+3]*counter[i+4]==1:
                straight=1
                straightlevel=i
        loyal=counter[0]*counter[9]*counter[10]*counter[11]*counter[12]
        if loyal!=0:
            straight=1
        return [straight,straightlevel]'''
        return straight

    def respond(self):
        flash = self.flashchecker()
        pairrate=[]
        for i in range (0,3):
            pairrate.append(self.ablepair()[i]-self.fieldpair()[i])
        if pairrate==[0,0,3]:
            pairrate=[0,0,2]
        straight=self.straightchecker()
        if pairrate==[0,0,0] and straight==[0,0]:
            return "fold"
        elif pairrate==[1,0,0] or pairrate==[0,1,1] or pairrate==[0,0,2] or flash==1:
            return "レイズ金額"
        else:
            return "call"


'''
評価の実装段階
・フラッシュ
・ストーレート
・ロイヤルストレート
・ペア数[4カード有無,3カード有無,ペアの数](フルハウス)
    →これを点数化してみるか
点数化したらベットが額にall inを導入するかも
'''
