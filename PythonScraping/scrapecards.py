# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 19:59:28 2019

@author: JJYJa
"""
import numpy as np
import json
import pandas as pd
import os
from pandas.io.json import json_normalize

os.chdir("C:/MTG-Arena-Tool/PythonScraping")

inputdf = pd.read_json('RnaDecks.json', lines=True)

inputdf=inputdf.drop_duplicates('deckid')

df = pd.DataFrame()

##for i in inputdf['mainDeck'].iteritems():
    ##appended_data.append(json_normalize(i[1]))

for index, row in inputdf.iterrows():
    df2 = json_normalize(row['CourseDeck']['mainDeck'])
    df2['playerRank']=row['playerRank']
    df2['Wins']=row['ModuleInstanceData']['WinLossGate']['CurrentWins']
    df2['Losses']=row['ModuleInstanceData']['WinLossGate']['CurrentLosses']
    df2['colors'] = row['CourseDeck']['colors']
    df = df.append(df2,ignore_index=True)

data = json.load(open('database.json'))

l = list(data.values())
carddata = pd.DataFrame()

for i in l:
    ##print(i)
    df2 = json_normalize(i)
    carddata = carddata.append(df2,ignore_index=True)
    
carddata['id'] = carddata['id'].apply(str)

cardwinrates = df.groupby('id')[['Wins','Losses']].sum()

cardwinrates = pd.merge(cardwinrates,carddata,left_index=True,right_on="id")

cardwinrates['W/L'] = cardwinrates['Wins']/(cardwinrates['Losses']+cardwinrates['Wins'])

cardwinrates['Games'] = cardwinrates['Wins']+cardwinrates['Losses']

cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='uncommon',cardwinrates['Games'] * (10/3.0), cardwinrates['Games'])
cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='rare',cardwinrates['Games'] * 10, cardwinrates['AdjustedGames'])

cardwinrates[['Wins','Losses','name','rarity', 'W/L', 'Games', 'AdjustedGames']].to_csv('cardwinrates.csv')