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

df = createdf('RNAdecks.json')

colorwinrates = df.groupby('colors')[['Wins','Losses']].sum().reset_index()
colorwinrates['WinLoss'] = colorwinrates['Wins']/(colorwinrates['Wins']+colorwinrates['Losses'])
colorwinrates['colors'] = colorwinrates['colors'].str.replace('1', 'W')
colorwinrates['colors'] = colorwinrates['colors'].str.replace('2', 'U')
colorwinrates['colors'] = colorwinrates['colors'].str.replace('3', 'B')
colorwinrates['colors'] = colorwinrates['colors'].str.replace('4', 'R')
colorwinrates['colors'] = colorwinrates['colors'].str.replace('5', 'G')

cardwinrates = df.loc[df['Maindeck'] > 0].groupby('id')[['Wins','Losses']].sum()

carddata = loaddatabase()

##carddata['id'] = carddata['id'].apply(str)
##carddata['id'] = carddata['id'].str[:5]

cardwinrates = pd.merge(cardwinrates,carddata,left_index=True,right_on="id")

cardwinrates['W/L'] = cardwinrates['Wins']/(cardwinrates['Losses']+cardwinrates['Wins'])

cardwinrates['Games'] = cardwinrates['Wins']+cardwinrates['Losses']

cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='uncommon',cardwinrates['Games'] * (8/3.0), cardwinrates['Games'])
cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='rare',cardwinrates['Games'] * 6, cardwinrates['AdjustedGames'])
cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='mythic',cardwinrates['Games'] * 12, cardwinrates['AdjustedGames'])

cardwinrates['WARC'] = (cardwinrates['W/L'] - .5) * cardwinrates['AdjustedGames']

cardwinrates[['Wins','Losses','name','rarity', 'W/L', 'Games', 'AdjustedGames', 'WARC']].to_csv('cardwinrates.csv')

colorwinrates.sort_values('WinLoss').to_csv('cardwinrates.tab',sep='\t')