# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 19:59:28 2019

@author: JJYJa
"""

import json
import pandas as pd
import os
from pandas.io.json import json_normalize

os.chdir("C:/MTG-Arena-Tool/PythonScraping")



inputdf = pd.read_json('M19decks.json', lines=True)
deckid = pd.read_csv('deckids.txt',header=None,names=['deckid'])

inputdf = pd.merge(inputdf,deckid,left_index=True,right_index=True)

inputdf=inputdf.drop_duplicates('deckid')

df = pd.DataFrame()

##for i in inputdf['mainDeck'].iteritems():
    ##appended_data.append(json_normalize(i[1]))

for index, row in inputdf.iterrows():
    df2 = json_normalize(row['mainDeck'])
    df2['deckid']=row['deckid']
    df = df.append(df2,ignore_index=True)

maindecksdf = df
maindecksdf=maindecksdf.loc[maindecksdf['quantity']>0]

inputdf = pd.read_json('M19.json', lines=True)

appended_data = []

for i in inputdf['result'].iteritems():
    appended_data.append(json_normalize(i[1]))
    
df = pd.concat(appended_data)
df = df.reset_index()

df = pd.merge(maindecksdf,df,left_on="deckid",right_on="_id")

cardwinrates = df.groupby('id')[['w','l']].sum()

data = json.load(open('database.json'))
l = list(data.values())

df3 = pd.DataFrame()

for i in l:
    print(i)
    df2 = json_normalize(i)
    df3 = df3.append(df2,ignore_index=True)
    
cardwinrates = pd.merge(cardwinrates,df3,left_index=True,right_on="id")

cardwinrates[['w','l','name','rarity']].to_csv('cardwinrates.csv')