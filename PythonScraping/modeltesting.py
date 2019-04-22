import requests
import hashlib
import time
import pandas as pd
from pandas.io.json import json_normalize
import json
import numpy as np
from MTGAToolFunctions import loaddatabase
from sklearn.model_selection import train_test_split

S = requests.Session()

url ='https://mtgatool.com/api/'
rslt = S.post(url+"login.php", data={'email':'lastchancexi@yahoo.com', 'password':
                                     hashlib.sha1('unreal12'.encode()).hexdigest(),
                                     'playername':'', 'playerid':'',
                                     'mtgaversion':'', 'playerid':'',
                                     'version':'', 'reqId':'ABCDEF',
                                     'method':'auth',
                                     'method_path':'/api/login.php'})

token = rslt.json()['token']

data = []
data_ids = set()

decks = {}

# 100 is the number of sets of 25 decklists to retrieve
for ii in range(200):
    time.sleep(1) # give the server a break, sleep between queries

    skip = ii * 25

    # do not use any filters - it's apparently a lighter load for the server that way
    result = S.post(url+"get_explore.php",
                    data={'token': token, 'filter_wcc': "", 'filter_wcu': "",
                          'filter_sortdir': 1, 'filter_type': '',
                          'filter_sort':"By Date", 'filter_skip':str(skip),
                          'filter_owned':"false", 'filter_event':"QuickDraft_GRN_20190412",
                          "filter_wcr":"", "filter_wcm":"", })

    data_this = result.json()

    unique_ids = set([x['_id'] for x in data_this['result']])

    n_unique = len(unique_ids - data_ids)

    data += data_this['result']

    data_ids = data_ids | unique_ids

    print(f"Added {n_unique} new ids of {len(unique_ids)} retrieved, total {len(data)}")

    # download each deck / match result entry
    for entry in data_this['result']:
        time.sleep(.2) # again, give the server a break
        deckid = entry['_id']

        course = S.post(url+"get_course.php", data={'token': token, 'courseid':deckid})
        course.raise_for_status()
        assert course.json()['ok']

        decks[deckid] = course.json()

        print(".", end="", flush=True)

#have to start by converting to pandas df
inputdf = pd.DataFrame.from_dict(decks,orient='index')
inputseries=inputdf['result']
#save pandas df
inputdf.to_pickle('inputdf.pkl')
##########
#Load pandas df
inputdf=pd.read_pickle('inputdf.pkl')
#########
#Color winrates
df = json_normalize(inputdf['result'])
df['Colors']=df['CourseDeck.colors'].apply(str)
colorwinrates = df.groupby('Colors')[['ModuleInstanceData.WinLossGate.CurrentWins','ModuleInstanceData.WinLossGate.CurrentLosses']].sum().reset_index()
##########

df['GoodDeck']=np.where(df['ModuleInstanceData.WinLossGate.CurrentWins']>4.5, 1, .5)
df['GoodDeck']=np.where(df['ModuleInstanceData.WinLossGate.CurrentWins']<1.5, 0, df['GoodDeck'])

carddata = loaddatabase()

maindeck=df['CourseDeck.mainDeck'].apply(json_normalize)
maindeck=pd.concat(maindeck.to_dict(),axis=0)
maindeck.index = maindeck.index.set_names(['DeckID', 'Seq'])
maindeck.reset_index(inplace=True)  
maindeck['id']=pd.to_numeric(maindeck['id'])
maindeck=maindeck.merge(carddata)

#list of all decks and main deck cards
MainDeckCards=maindeck.pivot_table('quantity', ['DeckID'], 'name').fillna(0)
MainDeckCards = MainDeckCards.astype(int)
feature_list=list(MainDeckCards)

modeldf = df.merge(MainDeckCards,left_index=True,right_index=True).reset_index(drop=True)
#X = StandardScaler().fit_transform(modeldf[feature_list])
modeldf = modeldf.loc[(modeldf['GoodDeck']==1) | (modeldf['GoodDeck']==0)]
modeldf['GoodDeck'] = modeldf['GoodDeck'].apply(int)

X = modeldf[['CourseDeck.colors','playerRank']]

X = X.merge(pd.get_dummies(X['playerRank']), left_index=True, right_index=True)
X = X.merge(pd.get_dummies(X['CourseDeck.colors'].apply(str)), left_index=True, right_index=True)
X = X.drop(columns=['CourseDeck.colors','playerRank'])

X_train, X_test, y_train, y_test = train_test_split(X, modeldf['GoodDeck'], test_size=0.25)

# Import the model we are using
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=500)

# Train the model on training data
rf.fit(X_train, y_train)

pd.crosstab(y_test, rf.predict(X_test), rownames=['Actual'], colnames=['Predicted'])

feature_imp = pd.Series(rf.feature_importances_,index=feature_list).sort_values(ascending=False)