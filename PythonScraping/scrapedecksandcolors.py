# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 19:57:14 2019

@author: JJYJa
"""

import pandas as pd
import os
from pandas.io.json import json_normalize

os.chdir("C:/MTG-Arena-Tool/PythonScraping")

inputdf = pd.read_json('RNAwinrates.json', lines=True)

appended_data = []

for i in inputdf['result'].iteritems():
    appended_data.append(json_normalize(i[1]))
    
df = pd.concat(appended_data)
df = df.reset_index()

df = df.drop_duplicates("_id")

df['colors']=df['colors'].astype(str)

colors = df.groupby('colors')[['w','l']].sum()

colors['winpercentage']=colors['w']/(colors['w']+colors['l'])

colors.sort_values(['winpercentage'])

colors.loc[colors.index.str.split(",").str.len()==2].sort_values(['winpercentage'])

#output decks
df["_id"].to_csv("decks.txt",index=False)
