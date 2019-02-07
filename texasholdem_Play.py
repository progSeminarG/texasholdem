#! /usr/bin/env python3

import argparse
import random
from copy import deepcopy
import sys
import matplotlib.pyplot as plt
from logging import getLogger, StreamHandler, DEBUG, INFO, WARNING

# plotting class import
from texasholdem_Plot import ReadPlot

# import players
from texasholdem_Dealer import Card, Dealer
from texasholdem_Player import Player
from texasholdem_Kawada import KawadaAI
from texasholdem_Shirai import ShiraiAI
from texasholdem_Takahashi import TakahashiAI
from texasholdem_Human import Human
from texasholdem_Muto import MutoAI


def silence(flagquiet):
    if flagquiet:
        __stdout_original = sys.stdout
        nullfile = open(os.devnull, 'w')
        sys.stdout = nullfile
        try:
            yield
        finally:
            sys.stdout = __stdout_original
    else:
        try:
            yield
        finally:
            pass


class Game(object):
    def __init__(self, players_list):
        self.__INITIAL_MONEY = 100  # money each player has in initial
        self.__players = players_list
        self.__num_players = len(self.__players)
        self.__total_money = self.__INITIAL_MONEY * self.__num_players
        # player's money at first
        self.__accounts = [self.__INITIAL_MONEY]*self.__num_players
        self.__DB = 0  # position of Dealer Button
        self.__num_done_games = 0  # number of games already done

    def play(self, minimum_bet=2):
        logger = getLogger(__name__)
        self.__minimum_bet = minimum_bet
        self.__dealer = Dealer(self, self.__players)
        self.__dealer.handout_cards()
        self.__dealer.get_responses()
        for i in range(3):
            self.__dealer.put_field()
        logger.debug("field:"+str([card.card for card in self.__dealer.field]))
        self.__dealer.get_responses()
        self.__dealer.put_field()
        logger.debug("field:"+str([card.card for card in self.__dealer.field]))
        self.__dealer.get_responses()
        self.__dealer.put_field()
        logger.debug("field:"+str([card.card for card in self.__dealer.field]))
        self.__dealer.get_responses()
        self.__dealer.final_accounting()
        self.__accounts = self.__dealer.list_of_money
        self.__DB = self.__dealer.DB_update()
        self.__num_done_games += 1

    def out_index(self, _file):
        _list = self.names_of_players
        _line = 'num,' + ','.join(_list) + "\n"
        _file.write(_line)

    def out_data(self, _file, _i):
        pp = str(_i) + ',' + ','.join([str(i) for i in self.__accounts]) + "\n"
        _file.write(pp)

    @property
    def accounts(self):
        return self.__accounts

    @property
    def total_money(self):
        return self.__total_money

    @property
    def DB(self):  # position of Dealer Button
        return self.__DB

    @property
    def num_players(self):
        return self.__num_players

    @property
    def names_of_players(self):
        return [i.__class__.__name__ for i in players_list]

    @property
    def minimum_bet(self):
        return self.__minimum_bet

    @property
    def num_games(self):  # number of games already done
        return self.__num_done_games


if __name__ == '__main__':

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.MetavarTypeHelpFormatter):
        pass

    parser = argparse.ArgumentParser(description="play Texas Hold'em.",
                                     formatter_class=CustomFormatter)
    parser.add_argument('--noshuffle', action='store_true', dest='noshuffle',
                        help='do not shuffle players')
    parser.add_argument('--numgames', type=int, default=[5], nargs=1,
                        help='set number of games')
    parser.add_argument('--players', type=str,
                        default=['Kawada', 'Shirai', 'Takahashi',
                                 'Player', 'Player', 'Muto'],
                        nargs='+', help='set list of players')
    parser.add_argument('--tournament', action='store_true',
                        help='play untile one has all money')
    parser.add_argument('--numtournament', type=int, nargs=1, default=[1],
                        help='number of player for tournament winner')
    parser.add_argument('--raiserate', type=int, nargs=2, default=[1, 0],
                        help='raise minimum bet in each <int> steps by <int>')
    parser.add_argument('--out', '--output', type=str, nargs=1,
                        default=['stat.csv'], help='set output file')
    parser.add_argument('--plot', action='store_true',
                        help='plot graph')
    parser.add_argument('--fig', type=str, dest='figfile', nargs='?',
                        const=None, default=None, help="output figure name")
    parser.add_argument('--stat', action='store_true',
                        help='static mode: play many tournaments')
    parser.add_argument('--statnum', type=int, nargs=1, default=[100],
                        help='number of tournament in statistic mode')
    parser.add_argument('-v', '--verbose', action='count',
                        help='increase output verbosity')

    args = parser.parse_args()

    # output handling #
    handler = StreamHandler()
    handler.setLevel(WARNING)
    logger = getLogger(__name__)
    logger.setLevel(WARNING)
    logger.addHandler(handler)
    logger.propagate = False
    if args.verbose:
        if args.verbose > 1:
            error_stage = DEBUG
        elif args.verbose == 1:
            error_stage = INFO
        handler.setLevel(error_stage)
        logger.setLevel(error_stage)
        logger.addHandler(handler)
        logger.propagate = False

    # create list of players #
    players_list = []
    for player in args.players:
        if player in {'Kawada', 'KawadaAI'}:
            players_list.append(KawadaAI())
        elif player in {'Muto', 'MutoAI'}:
            players_list.append(MutoAI())
        elif player in {'Shirai', 'ShiraiAI'}:
            players_list.append(ShiraiAI())
        elif player in {'Takahashi', 'TakahashiAI'}:
            players_list.append(TakahashiAI())
        elif player == 'Human':
            players_list.append(Human())
        elif player == 'Player':
            players_list.append(Player())
        else:
            _error_message = "ERROR! No such an AI! " + player
            raise ValueError(_error_message)
    
    # shuffle players #
    if not args.noshuffle:
        random.shuffle(players_list)
    print("players:", [i.__class__.__name__ for i in players_list])
    
    # statistic mode: play many tournaments (--stat)#
    if args.stat:
        _i = 0
        win_list = [0]*len(players_list)
        while _i <= args.statnum[0]:
            logger.info("===== tournament " + str(_i) + " =====")
            game = Game(players_list)  # create game
            while (game.accounts.count(0)
                    != game.num_players - args.numtournament[0]):
                game.play()
                logger.info(game.accounts)
            for i in range(len(game.accounts)):
                if game.accounts[i] != 0:
                    win_list[i] += 1
            _i += 1
        # print data #
        print("----------------------------------------")
        print("{:15}{:>23}".format('players', 'WINs    (%)'))
        print("----------------------------------------")
        for i in range(len(win_list)):
            print("{:15}{:15} ({:>4.1f}%)".format(
                game.names_of_players[i],
                win_list[i],
                win_list[i]/args.statnum[0]*100))
        print("----------------------------------------")
        # plot
        if args.plot:
            plt.axis('equal')
            plt.pie(win_list, labels=game.names_of_players, startangle=90)
            plt.show()

    # normal play mode #
    else:
        game = Game(players_list)
        _output = args.out[0]  # log file
        with open(_output, "w") as _file:
            game.out_index(_file)
            game.out_data(_file, 0)
            # single tournament (--tournmant)
            if args.tournament:
                _minimum_bet = 2
                _num_player_thresh = game.num_players - args.numtournament[0]
                while (game.accounts.count(0) < _num_player_thresh):
                    logger.debug("minimum_bet:"+str(_minimum_bet))
                    game.play()
                    print("game {}: {}".format(game.num_games, game.accounts))
                    game.out_data(_file, game.num_games)
                    if game.num_games % args.raiserate[0] == 0:
                        _minimum_bet += args.raiserate[1]
            # single plays (no option)
            else:
                while game.num_games < args.numgames[0]:
                    game.play()
                    print("game {}: {}".format(game.num_games, game.accounts))
                    game.out_data(_file, game.num_games)

        # plot
        if args.plot:
            stat_inst = ReadPlot(datafile=args.out[0], figfile=args.figfile)
            stat_inst.plot()
