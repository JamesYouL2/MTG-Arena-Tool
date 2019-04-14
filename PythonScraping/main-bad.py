# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 20:13:03 2019

@author: JJYJa
"""

from MTGAToolFunctions import getdeckids
from MTGAToolFunctions import createdf


getdeckids(inputfile='GRNExplore.json', outputfile='GRNDeckids.txt')
df = createdf('RNAdecks.json')

cardwinrates = df.groupby('id')[['Wins','Losses']].sum()


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

cardwinrates = pd.merge(cardwinrates,carddata,left_index=True,right_on="id")

cardwinrates['W/L'] = cardwinrates['Wins']/(cardwinrates['Losses']+cardwinrates['Wins'])

cardwinrates['Games'] = cardwinrates['Wins']+cardwinrates['Losses']

cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='uncommon',cardwinrates['Games'] * (8/3.0), cardwinrates['Games'])
cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='rare',cardwinrates['Games'] * 6, cardwinrates['AdjustedGames'])
cardwinrates['AdjustedGames'] = np.where(cardwinrates['rarity']=='mythic',cardwinrates['Games'] * 12, cardwinrates['AdjustedGames'])

cardwinrates[['Wins','Losses','name','rarity', 'W/L', 'Games', 'AdjustedGames']].to_csv('cardwinrates.csv')