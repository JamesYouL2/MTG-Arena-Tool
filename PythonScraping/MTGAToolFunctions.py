# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 20:44:50 2019

@author: JJYJa
"""


import json
import pandas as pd
import os
from pandas.io.json import json_normalize

def getdeckids(inputfile, outputfile):  
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    
    inputdf = pd.read_json(inputfile)
    appended_data = []
    
    df = pd.DataFrame
    
    for i in inputdf['result'].iteritems():
        appended_data.append(json_normalize(i[1]))
        
    df = pd.concat(appended_data)
    df = df.reset_index()

    df = df.drop_duplicates("_id")
    
    df["_id"].to_csv(outputfile,index=False)
    
def cardwinrates (inputjson, inputfile, deckwinratefile, outputfile):
    inputdf = pd.read_json(inputjson, lines=True)
    deckid = pd.read_csv(inputfile, header=None, names=['deckid'])
        
    mergedf = pd.merge(inputdf, deckid, left_index=True, right_index=True)
    mergedf = mergedf.drop_duplicates('deckid')
    
    maindecksdf = pd.DataFrame()
    
    for index, row in mergedf.iterrows():
        df2 = json_normalize(row['mainDeck'])
        df2['deckid']=row['deckid']
        maindecksdf = maindecksdf.append(df2,ignore_index=True)

    inputdf = pd.read_json(deckwinratefile, lines = True) 
    appended_data = []
    
    for i in inputdf['result'].iteritems():
        appended_data.append(json_normalize(i[1]))
        
    concatdf = pd.concat(appended_data)
    concatdf = concatdf.reset_index()

    df = pd.merge(maindecksdf,concatdf,left_on="deckid",right_on="_id")
    
    cardwinrates = df.groupby('id')[['w','l']].sum()
    
    data = json.load(open('database.json'))
    l = list(data.values())
    
    df = pd.DataFrame()
    
    for i in l:
        print(i)
        df2 = json_normalize(i)
        df = df.append(df2,ignore_index=True)
        
    cardwinrates = pd.merge(cardwinrates, df, left_index=True, right_on="id")
    
    cardwinrates = cardwinrates.loc[cardwinrates['rarity']!='land']
    
    cardwinrates[['w','l','name','rarity']].to_csv('cardwinrates.csv')