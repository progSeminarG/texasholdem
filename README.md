# Texas Hold'em

## ゲームの流れ
1. 2 枚ずつ配る (Dealer が handout_cards メソッドを実行: Player の get_hand メソッドが呼ばれる)。  
2. ビッグブランインドの左側のプレイヤーから順番に時計回りにベットする (Dealer が get_response メソッドを実行: Player の respond メソッドが呼ばれる)。  
respond で許されるのは、'call' (最低金額で参加) [str], 'hold' (降りる、ゲーム放棄) [str], レイズ金額 (金額を釣り上げて参加) [int] の 3 種類。レイズする場合には、レイズ金額 (現状の場の最低掛け金への上乗せ分) を指定。
レイズが無ければ、ビッグブラインドのベットまで行う。　　
途中でレイズがあった場合には、さらに 1 周して、レイズがなくなるまで同様に続ける。途中で降りても良いが、それまでに出したチップは返ってこない。  
3. 場に 3 枚開く (Dealer が put_field メソッドを 3 回実行)。  
4. ディーラーボタンの左側のプレイヤーから 2 と同様にしてベットする。
5. 場にカードを 1 枚開ける。  
6.  に戻る (場のカードが 5 枚になるまで)。  
7. 場のカードが 5 枚の状態で 3 に戻り、レイズが止まって 1 周したら、まだ残っているプレイヤーの手札を比べ、最も強い手札を持っている人が、それまで出されたチップを全てもらう。

## プレーヤークラスの必須メソッド
- `get_know_dealer` ディーラーインスタンスを受け取る。
- `get_hand` 初期手札を得る。
- `respond` 'stay', 'hold', レイズ金額を指定。

## ディーラーから得られる情報
- `field` 場のカード
- `players_money` 各プレイヤーの所持金
- `field_money` 場に積まれている金額
- `minimum_bet` 最低掛け金
