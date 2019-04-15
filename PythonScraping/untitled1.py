# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 12:39:14 2019

@author: JJYJa
"""

import json
import pandas as pd
import os
from pandas.io.json import json_normalize

inputfile = 'RNADecks.json'

inputdf = pd.read_json(inputfile, lines=True)
    
inputdf['CourseDeckString'] = inputdf['CourseDeck'].astype(str)
inputdf = inputdf.drop_duplicates('CourseDeckString')

df = pd.DataFrame()

##for i in inputdf['mainDeck'].iteritems():
    ##appended_data.append(json_normalize(i[1]))

for index, row in inputdf.iterrows():
    maindeck = json_normalize(row['CourseDeck']['mainDeck'])
    sideboard = json_normalize(row['CourseDeck']['sideboard'])
    if sideboard.empty:
        sideboard['id'] = 0
    df2 = maindeck.merge(sideboard, on='id', how = 'outer')
    df2 = df2.fillna(value=0)
    df2['playerRank']=row['playerRank']
    df2['Wins']=row['ModuleInstanceData']['WinLossGate']['CurrentWins']
    df2['Losses']=row['ModuleInstanceData']['WinLossGate']['CurrentLosses']
    df2['colors'] = ''.join(str(row['CourseDeck']['colors']))
    df = df.append(df2,ignore_index=True)
    
inputdf.groupby('playerRank').agg(['count'])