# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 18:35:00 2019

@author: JJYJa
"""

import pandas as pd
from MTGAToolFunctions import getdeckids
from MTGAToolFunctions import createdf
from MTGAToolFunctions import loaddatabase

df = createdf('RNAdecks.json')

dfseven = df.loc[(df['Wins'] == 7) & (df['Maindeck'] > 0)].groupby('id').count()['Wins'].reset_index(name='count')

carddata = loaddatabase()

carddata['id'] = carddata['id'].apply(str)
carddata['id'] = carddata['id'].str[:5]
dfseven['id'] = dfseven['id'].apply(str)

merge = pd.merge(dfseven,carddata,on="id",how="left")

dfseven.loc[dfseven["id"]=='67015']["id"]
carddata.loc[carddata["id"]=='67015']["id"]

sort = merge[['count','rarity','name']].sort_values('count', ascending=False)

sort.loc[sort['name']=='Glass of the Guildpact']