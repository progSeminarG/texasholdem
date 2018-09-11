#確率調査

import random

def kariyaku(any_cards):
    if straightflashchecker()==1:
        return 9
    elif checkpair(any_cards)[0]==1:
        return 8
    elif checkpair(any_cards)==([0,2,0]or[0,1,1]or[0,1,2]):
        return 7
    elif flashchecker(any_cards)==1:
        return 6
    elif straightchecker(any_cards)==1:
        return 5
    elif checkpair(any_cards)[1]==1:
        return 4
    elif checkpair(any_cards)[2]==(2 or 3):
        return 3
    elif checkpair(any_cards)[2]==1:
        return 2
    else:
        return 0

def straightflashchecker():#ストレートなら１を返す
    suitcounter=[0]*4
    cards=[]
    for i in range (0,len(playable_cards)):
        suitcounter[playable_cards[i][0]]=suitcounter[playable_cards[i][0]]+1
    mostmanysuit=0
    for i in range (0,3):
        if suitcounter[mostmanysuit]<suitcounter[i+1]:
            mostmanysuit=i+1
    for i in range (0,7):
        if playable_cards[6-i]==mostmanysuit:
            cards.append(playable_cards[7-i])
    counter=[0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range (0,len(cards)):
        counter[cards[i][1]-1]=counter[cards[i][1]-1]+1
    counter[13]=counter[0]
    straightflash=0
    for j in range(0,10):
        if counter[j]!=0:
            for i in range (0,9):
                if counter[j+1]!=0:
                    if counter[j+2]!=0:
                        if counter[j+3]!=0:
                            if counter[j+4]!=0:
                                straightflash=1
    return straightflash



def checkpair(any_cards):#ペアの評価方法
    pair=[0,0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range (0,len(any_cards)):
        pair[any_cards[i][1]-1]=pair[any_cards[i][1]-1]+1
    pairs=[0,0,0]
    for i in range (0,13):
        if pair[i]==4:
            pairs[0]=pairs[0]+1
        elif pair[i]==3:
            pairs[1]=pairs[1]+1
        elif pair[i]==2:
            pairs[2]=pairs[2]+1
    return pairs

def flashchecker(any_cards): #flashできるときに1を返す
    suitcounter=[0,0,0,0]
    check=0
    for i in range (0,len(any_cards)):
        if any_cards[i][0]==0:
            suitcounter[0]=suitcounter[0]+1
        if any_cards[i][0]==1:
            suitcounter[1]=suitcounter[1]+1
        if any_cards[i][0]==2:
            suitcounter[2]=suitcounter[2]+1
        if any_cards[i][0]==3:
            suitcounter[3]=suitcounter[3]+1
    for i in range (0,4):
        if suitcounter[i]>=5:
            check=1
    return check

def straightchecker(any_cards):#ストレートなら１を返す
    counter=[0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range (0,len(any_cards)):
        counter[any_cards[i][1]-1]=counter[any_cards[i][1]-1]+1
    counter[13]=counter[0]
    straight=0
    for j in range(0,10):
        if counter[j]!=0:
            for i in range (0,9):
                if counter[j+1]!=0:
                    if counter[j+2]!=0:
                        if counter[j+3]!=0:
                            if counter[j+4]!=0:
                                straight=1
    return straight


def searchcase(pairscount):
    distance=0
    if playable_cards[0][1] > playable_cards[1][1]:
        distance = playable_cards[0][1] - playable_cards[1][1]
    else:
        distance = playable_cards[1][1] - playable_cards[0][1]
    if playable_cards[0][0]==playable_cards[1][0]:
        flashcount[distance-1]=flashcount[distance-1]+1
        #print("flash",end="")
    elif playable_cards[0][1]==playable_cards[1][1]:
        #print("pair_",end="")
        pairscount=pairscount+1
    else:
        #print("_____",end="")
        _____count[distance-1]=_____count[distance-1]+1
    #print("......",distance)



all_____count=[0]*12
allpairscount=0
allflashcount=[0]*12
_____count=[0]*12
pairscount=0
flashcount=[0]*12



true=0
all=0
for time in range(0,10000):
    playable_cards=[]

    all_cards=[]
    for i in range (0,4):
        for j in range (0,13):
            all_cards.append([i,j+1])


    for i in range (0,2):
        j=random.randint(0,len(all_cards)-1)
        playable_cards.append(all_cards[j])
        all_cards.pop(j)

    if playable_cards[0][1] > playable_cards[1][1]:
        distance = playable_cards[0][1] - playable_cards[1][1]
    else:
        distance = playable_cards[1][1] - playable_cards[0][1]
    if playable_cards[0][0]==playable_cards[1][0]:
        allflashcount[distance-1]=allflashcount[distance-1]+1
    elif playable_cards[0][1]==playable_cards[1][1]:
        allpairscount=allpairscount+1
    else:
        all_____count[distance-1]=all_____count[distance-1]+1

        #print(playable_cards)

    for i in range (0,5):
        j=random.randint(0,len(all_cards)-1)
        playable_cards.append(all_cards[j])
        all_cards.pop(j)


    player1=[]
    player2=[]
    player3=[]

    for j in range (2,7):
        player1.append(playable_cards[j])
        player2.append(playable_cards[j])
        player3.append(playable_cards[j])


    for i in range (0,2):
        j=random.randint(0,len(all_cards)-1)
        player1.append(all_cards[j])
        all_cards.pop(j)

    for i in range (0,2):
        j=random.randint(0,len(all_cards)-1)
        player2.append(all_cards[j])
        all_cards.pop(j)

    for i in range (0,2):
        j=random.randint(0,len(all_cards)-1)
        player3.append(all_cards[j])
        all_cards.pop(j)

        #print(playable_cards)
    if kariyaku(playable_cards)>=kariyaku(player1):
        if kariyaku(playable_cards)>=kariyaku(player2):
            if kariyaku(playable_cards)>=kariyaku(player3):
                #print(playable_cards,end="            ")
                searchcase(pairscount)
                #print("pairs=",end="")
                #print(checkpair(playable_cards),end=' ')
                #print("straight=",end="")
                #print(straightchecker(playable_cards),end=" ")
                #print("flash=",end='')
                #print(flashchecker(playable_cards),end=" ")
                #print(".........",kariyaku(playable_cards))
                #print()
                if distance==0:
                    pairscount=pairscount+1
'''
print(allpairscount)
print(allflashcount)
print(all_____count)
print(pairscount)
print(flashcount)
print(_____count)'''

print("<pairs> ")
print(pairscount,"/",allpairscount)
print()
print("<flash>")
for i in range (0,12):
    print("distance = ",i+1,".......",flashcount[i],"/",allflashcount[i])
print()
print("<_____>")
for i in range (0,12):
    print("distance = ",i+1,".......",_____count[i],"/",all_____count[i])
