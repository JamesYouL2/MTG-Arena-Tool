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
    
    inputdf = pd.read_json(inputfile, lines = True)
    appended_data = []
    
    df = pd.DataFrame
    
    for i in inputdf['result'].iteritems():
        appended_data.append(json_normalize(i[1]))
        
    df = pd.concat(appended_data)
    df = df.reset_index()

    df = df.drop_duplicates("_id")
    
    df["_id"].to_csv(outputfile,index=False)
    
def createdf(inputfile):
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    
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
    
    return cardwinrates