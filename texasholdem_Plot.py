#! /usr/bin/env python3

import argparse
import pandas
import matplotlib.pyplot as plt
import sys


class ReadPlot(object):
    def __init__(self,datafile="stat.csv",figfile=None):
        self.__datafile = datafile
        self.__figfile = figfile
        self.__readfile(datafile=datafile)

    def __readfile(self,datafile="stat.csv"):
        self.__data = pandas.read_csv(datafile,header=0,index_col=0,encoding='utf-8',skipinitialspace=True)
        self.__players_class_list = list(self.__data.columns)
        self.__num_players = len(self.__players_class_list)
        self.__players_name_list = [name.replace("AI","") for name in self.__players_class_list]
        # calculate statistic values
        self.__average_list = list(self.__data.mean())
        self.__ranking = sorted(range(self.__num_players),key=lambda k:self.__average_list[k])
        self.__each_rank = [self.__ranking.index(i) for i in range(self.__num_players)]
        self.__std_list = list(self.__data.std(ddof=False))
        self.__num_games = len(self.__data)

    @property
    def data(self):
        return self.__data

    def show_stat_horizontal(self):
        self.__print_list(pre="players= ",list=self.__players_class_list,form="{}")
        self.__print_list(pre="ave.= ",list=self.__average_list)
        self.__print_list(pre="std.= ",list=self.__std_list)
        self.__print_list(pre="rank= ",list=self.__each_rank)

    def show_stat_vertical(self):
        _stat_list = []
        for (a,b,c,d) in zip(self.__each_rank,self.__players_class_list,self.__average_list,self.__std_list):
            _stat_list += [[a,b,c,d]]
        print("{:3}{:15}{:5}{:5}".format("#","Name","ave.","std."))
        for _list in sorted(_stat_list):
            print("{0[0]:1}. {0[1]:15}{0[2]:<5.2f}{0[3]:<5.2f}".format(_list))

    def __print_list(self,list=[],form="{:.2f}",pre="",post="",sep=", ",header=None):
        if header:
            print(header)
        _print_text = pre
        for i in list:
            _print_text += form.format(i) + sep
        _print_text = _print_text[:-len(sep)] + post
        print(_print_text)

    def plot(self):
        fig, ax = plt.subplots() # create plot space and axis
        plt.rcParams["font.size"] = 7 # font size except ticks
        plt.tick_params(labelsize=7) # font size of ticks
        fig.subplots_adjust(bottom=0.2) # modify bottom margin
        excel_color_list = ['#4E72BE','#DE8244','#A5A5A5','#F5C142','#699AD0','#7EAA55','#2C4474','#934C20','#626362','#937324']
        ax.plot(self.__data)
        ax.legend(self.__players_name_list)
#        plt.ylim([0,self.__num_games]) # y-range
#        _xticks = [i for i in range(self.__num_players)] # x-tics = [0, 1, 2, ...]
#        _xlabel = [self.__players_name_list[i] for i in self.__ranking] # x-label (list of names)
#        _bottom = [0 for i in range(self.__num_players)] # [0,0,0,...]
#        for ith in range(self.__num_players): # loop for ith-rank: from 1st, 2nd, 3rd, ...
#            _list = []
#            for irank in self.__ranking: # loop for each players: from top player to the last
#                _player = self.__players_class_list[irank] # get column name of irank-th player
#                _count_rank = (self.__data[_player]==ith).sum() # get column data which is ith and count
#                _list.append(_count_rank) # append to _list
#            # plot bar-graph.
#            # x-position, y-height, x-label, offset, align, label for legend
#            ax.bar(_xticks, _list, tick_label=_xlabel, bottom=_bottom, align="center", label=str(ith), color=excel_color_list[ith])
#            for j in range(len(_list)):
#                if _list[j] >= self.__num_games*0.04: # if there is a space in bin
#                    # print number of ith-game
#                    ax.annotate(_list[j], (_xticks[j],_bottom[j]+_list[j]/2),ha='center',va='center',color='white')
#            _bottom = [_bottom[i]+_list[i] for i in range(self.__num_players)] # update offset
#        ax.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=True) # delete x-ticks
#        ax.text(-1,-self.__num_games*0.1,'ave.',ha='center',va='center') # print 'ave.'
#        ax.text(-1,-self.__num_games*0.15,'std.',ha='center',va='center') # print 'std.'
#        # print ave. and std. for each player
#        for i in range(self.__num_players):
#            ax.text(_xticks[i],-self.__num_games*0.11,'{:.2f}'.format(self.__average_list[self.__ranking[i]]),ha='center',va='center')
#            ax.text(_xticks[i],-self.__num_games*0.16,'{:.2f}'.format(self.__std_list[self.__ranking[i]]),ha='center',va='center')
#        # set legend format
#        ax.legend(bbox_to_anchor=(0.,1.,1.,0.05),ncol=self.__num_players,borderaxespad=0.,mode='expand',edgecolor='None')
#        # save as png
        if self.__figfile:
            plt.savefig(self.__figfile)
            print("data plotted:",self.__figfile)
        else:
            plt.show()


if __name__ == '__main__':
    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,argparse.MetavarTypeHelpFormatter):
        pass
    parser = argparse.ArgumentParser(description="Plot score.", formatter_class=CustomFormatter)
    parser.add_argument('--file', '--datafile', type=str, dest='datafile', nargs='?', default='stat.csv', help="input data file")
    parser.add_argument('--fig', type=str, const=None, dest='figfile', nargs='?', default=None, help="output figure file (png)")
    args = parser.parse_args()
    stat_inst = ReadPlot(datafile=args.datafile,figfile=args.figfile)
    stat_inst.show_stat_vertical()
    stat_inst.plot()
