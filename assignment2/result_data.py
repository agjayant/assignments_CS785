
# coding: utf-8

# In[ ]:

#!/usr/bin/env python
import openpyxl as pxl
import scipy.io as scio


# In[ ]:

book = pxl.load_workbook('LS-2014_ElectionResult.xlsx', use_iterators = True)
sheet = book.get_sheet_by_name(name = 'Result  LS 2014')


# In[ ]:

res_const = {}


# In[ ]:

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
        if const not in res_const:
            res_const[const] = [state, { abbr: [win, votes] } ]
        else:
            if abbr == 'IND':
                if abbr not in res_const[const][1]:
                    res_const[const][1][abbr] = [win, votes]
            else :
                res_const[const][1][abbr] = [win,votes]

