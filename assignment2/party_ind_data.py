#!/usr/bin/env python
import openpyxl as pxl
import scipy.io as scio


# In[ ]:

book = pxl.load_workbook('Party_Contested_GE_2014.xlsx', use_iterators = True)
sheet = book.get_sheet_by_name(name = 'Sheet1')


# In[ ]:

party_ind = {}


# In[ ]:

for party in sheet.iter_rows():
    for info in party:
        if info.row > 2 and info.row < 468:
            if info.column == 'A':
                abbr = info.internal_value
            elif info.column == 'B':
                name = info.internal_value
            elif info.column == 'E':
                seatsWon = info.internal_value
            elif info.column == 'F':
                votes = info.internal_value
            elif info.column == 'G':
                votesPer = info.internal_value
    party_ind[abbr]= [name,seatsWon,votes,votesPer]


# In[ ]:

scio.savemat('party_ind.mat',party_ind)

