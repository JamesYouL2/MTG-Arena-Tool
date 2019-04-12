# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 19:59:28 2019

@author: JJYJa
"""


import pandas as pd
import os
from pandas.io.json import json_normalize

os.chdir("C:/MTG-Arena-Tool/PythonScraping")

inputdf = pd.read_json('M19decks.json', lines=True)

inputdf=inputdf.drop_duplicates('id')

df = pd.DataFrame()

##for i in inputdf['mainDeck'].iteritems():
    ##appended_data.append(json_normalize(i[1]))

for index, row in inputdf.iterrows():
    df2 = json_normalize(row['mainDeck'])
    df2['deckid']=row['id']
    df = df.append(df2,ignore_index=True)

maindecksdf = df

maindecksdf["id"]=maindecksdf["id"].to_string()

df = pd.merge(maindecksdf,df,left_on="deckid",right_on="_id")