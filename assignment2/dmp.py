
# coding: utf-8

# In[1]:

#!/usr/bin/env python
import openpyxl as pxl
import scipy.io as scio
import numpy as np
from collections import OrderedDict
import sys


# In[2]:

book = pxl.load_workbook('LS-2014_ElectionResult.xlsx', use_iterators = True)
sheet = book.get_sheet_by_name(name = 'Result  LS 2014')


# In[3]:

# main_state = 'Uttar Pradesh'
main_state = sys.argv[1]
# main_state = 'Maharashtra'
res_const = OrderedDict()


# In[4]:

### Data Extraction for State

# Storing only the first independent candidate for each constituency
# Only the first can be the winner
for row in sheet.iter_rows():
    for info in row:
        if info.row > 3 and info.row < 8798:
            if info.column == 'A':
                state = info.internal_value
            elif info.column == 'B':
                const = info.internal_value
            elif info.column == 'D':
                votes = info.internal_value
            elif info.column == 'E':
                win = info.internal_value
            elif info.column == 'F':
                abbr = info.internal_value
    if info.row > 3 and info.row < 8798:
        if state == main_state:
            if const not in res_const:
                res_const[const] = { abbr: [win, votes] }
            else:
                if abbr == 'IND':
                    if abbr not in res_const[const]:
                        res_const[const][abbr] = [win, votes]
                else :
                    res_const[const][abbr] = [win,votes]


# In[5]:

## Handling for odd number of seats

# print len(res_const)
# del res_const['BETUL']
if len(res_const) % 2 !=0 :
    del res_const[res_const.keys()[0]]


# In[6]:

## Calculating Total Party Votes

regionVotes = {}
winnerList = []
for item in res_const:
    for party in res_const[item]:
        if party not in regionVotes:
            regionVotes[party] = res_const[item][party][1]
        else:
            regionVotes[party] += res_const[item][party][1]

        if res_const[item][party][0] == 'yes':
            if party not in winnerList:
                winnerList.append(party)

del regionVotes['NOTA']
del regionVotes['IND']

# print winnerList

regionList = []
totalVotes = 0
for item in regionVotes:
    totalVotes += regionVotes[item]

for item in regionVotes:
    regionList.append((regionVotes[item]/totalVotes,item))

regionList.sort(reverse=True)

temp = []
for i in range(len(regionList)):
    if regionList[i][0] >= 0.01 or regionList[i][1] in winnerList:
        temp.append(regionList[i])
regionList = temp

# regionList


# In[7]:

##Pairing Constituencies

paired_const = {}
for i in range(0,len(res_const),2):
    c1 = res_const.keys()[i]
    c2 = res_const.keys()[i+1]

    pair = c1+c2
    paired_const[pair]= {}

    totVotes1 = 0
    for item in res_const[c1]:
        totVotes1 += res_const[c1][item][1]

    totVotes2 = 0
    for item in res_const[c2]:
        totVotes2 += res_const[c2][item][1]

    totVotes = totVotes1 + totVotes2
    newtotVotes = totVotes

    for item in res_const[c1]:
        paired_const[pair][item] = [res_const[c1][item][1]*totVotes/totVotes1,1]
        newtotVotes += res_const[c1][item][1]*totVotes2/totVotes1

    for item in res_const[c2]:
        if item not in paired_const[pair]:
            paired_const[pair][item] = [res_const[c2][item][1]*totVotes/totVotes2,1]
            newtotVotes += res_const[c2][item][1]*totVotes1/totVotes2
        else:
            paired_const[pair][item][1] = 2
            newtotVotes -= paired_const[pair][item][0]*totVotes2/totVotes
            paired_const[pair][item][0] = paired_const[pair][item][0]*totVotes1/totVotes + res_const[c2][item][1]

for pair in paired_const:
    for item in paired_const[pair]:
        paired_const[pair][item][0] /= newtotVotes
# paired_const


# In[8]:

## Primary Winners -- Round 1
primaryWinners = {}

for pair in paired_const:

    winList = []
    for item in paired_const[pair]:
        winList.append((paired_const[pair][item][0],item))
    winList.sort(reverse=True)

    primaryWinners[pair] = winList[0][1]
    if paired_const[pair][winList[0][1]][1] == 2:
        paired_const[pair][winList[0][1]][0] /= 2

    paired_const[pair][winList[0][1]][1] -= 1

#primaryWinners


# In[9]:

## Seats Distribution to be done in Round 2

totalSeats = len(res_const)
firstRound = {}
seatsAlloc = 0
fracList = []
for item in regionList:
    party = item[1]
    won = 0
    for j in primaryWinners:
        if primaryWinners[j] == party:
            won +=1
    more = item[0]*totalSeats
    seatsAlloc += round(item[0]*totalSeats)
    firstRound[party] = [round(more),won,round(more) - won]

    frac = more % 1

    if frac < 0.5:
        fracList.append((frac,party))

rem = totalSeats - seatsAlloc
fracList.sort(reverse=True)

for i in range(int(rem)):
    firstRound[fracList[i][1]][0] += 1
    firstRound[fracList[i][1]][2] += 1

# for item in firstRound:
#     print item,firstRound[item]


# In[10]:

### Preference List of Seats for Parties

prefList = {}
for pair in paired_const:

    for party in paired_const[pair]:
        if paired_const[pair][party][1] > 0:
            if party not in prefList and party in firstRound:
                prefList[party] = [(paired_const[pair][party][0], pair)]
            elif party in firstRound:
                prefList[party].append((paired_const[pair][party][0],pair))
for party in prefList:
    prefList[party].sort(reverse=True)

# prefList


# In[11]:

### Round 2
secondList = {}
clashes = []
party_next = {}
for party in firstRound:
    to_get = int(firstRound[party][2])
    if to_get > 0:
        for i in range(to_get):
            if prefList[party][i][1] not in secondList:
                secondList[prefList[party][i][1]] = [party]
            else:
                secondList[prefList[party][i][1]].append(party)
                if prefList[party][i][1] not in clashes:
                    clashes.append(prefList[party][i][1])
    party_next[party] = to_get


# In[13]:

while len(clashes) > 0:
    pair = clashes[0]
    #print clashes[0]
    best = []
    for party in secondList[pair]:
        best.append((paired_const[pair][party][0],party))
    best.sort(reverse=True)
    # del from list
    clashes.remove(pair)
    # del from dictionary
    del secondList[pair]
    # add to dictionary
    secondList[pair] = [best[0][1]]
    # assign all other parties new seat
    # compute new clashes
    best.remove(best[0])
    #print best[0][1],best
    for i in range(len(best)):
        party = best[i][1]
        next_seat = party_next[party]
        if next_seat >= len(prefList[party]):
            continue
        if prefList[party][next_seat][1] not in secondList:
            secondList[prefList[party][next_seat][1]] = [party]
        else:

            secondList[prefList[party][next_seat][1]].append(party)
            if prefList[party][next_seat][1] not in clashes:
                clashes.append(prefList[party][next_seat][1])
        party_next[party] += 1


# In[15]:

partyres= {}
for item in secondList:
    if secondList[item][0] not in partyres:
        partyres[secondList[item][0]] = 1
    else:
        partyres[secondList[item][0]] += 1
for item in firstRound:
    if item not in partyres:
        partyres[item] = firstRound[item][1]
    else:
        partyres[item] += firstRound[item][1]


# In[16]:

for item in partyres:
    print item, partyres[item]#,firstRound[item]

