# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 20:13:03 2019

@author: JJYJa
"""

import os
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import json

os.chdir("C:/MTG-Arena-Tool/PythonScraping")

from MTGAToolFunctions import getdeckids
from MTGAToolFunctions import createdf
from MTGAToolFunctions import loaddatabase

getdeckids(inputfile='GRNExplore.json', outputfile='GRNDeckids.txt')

basedf = createdf('GRNdecks.json')

df = basedf.loc[basedf['playerRank'].isin(['Silver','Gold', 'Mythic', 'Platinum'])]

carddata = loaddatabase()
deckdf = df.drop_duplicates(subset=['colors','deckid'])

colorwinrates = deckdf.groupby('colors')[['Wins','Losses']].sum().reset_index()
colorwinrates['WinLoss'] = colorwinrates['Wins']/(colorwinrates['Wins']+colorwinrates['Losses'])
colorwinrates['colors'] = colorwinrates['colors'].str.replace('1', 'W')
colorwinrates['colors'] = colorwinrates['colors'].str.replace('2', 'U')
colorwinrates['colors'] = colorwinrates['colors'].str.replace('3', 'B')
colorwinrates['colors'] = colorwinrates['colors'].str.replace('4', 'R')
colorwinrates['colors'] = colorwinrates['colors'].str.replace('5', 'G')

#cardwinrates = df.groupby('id')[['Wins','Losses']].sum().reset_index()

cardwinrates = df.loc[df['Maindeck'] > 0].groupby('id')[['Wins','Losses']].sum().reset_index()

carddata['id'] = carddata['id'].apply(str)
carddata['id'] = carddata['id'].str[:5]
cardwinrates['id'] = cardwinrates['id'].apply(str)
cardwinrates['id'].str.len().unique()

cardwinrates = pd.merge(cardwinrates,carddata,left_on="id",right_on="id")

cardwinrates['W/L'] = cardwinrates['Wins']/(cardwinrates['Losses']+cardwinrates['Wins'])

cardwinrates['Games'] = cardwinrates['Wins']+cardwinrates['Losses']

cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='uncommon',cardwinrates['Games'] * (8/3.0), cardwinrates['Games'])
cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='rare',cardwinrates['Games'] * 6, cardwinrates['AdjustedGames'])
cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='mythic',cardwinrates['Games'] * 12, cardwinrates['AdjustedGames'])

cardwinrates['WARC'] = (cardwinrates['W/L'] - .5) * cardwinrates['AdjustedGames']

cardwinrates.sort_values('W/L', ascending=False)[['Wins','Losses','name','rarity', 'W/L', 'Games']].to_csv('cardwinrates.tab',sep='\t')

colorwinrates.sort_values('WinLoss', ascending=False).to_csv('colorwinrates.tab',sep='\t')