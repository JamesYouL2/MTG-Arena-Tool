import requests
import hashlib
import time
import pandas as pd
from pandas.io.json import json_normalize
import json
import numpy as np
from MTGAToolFunctions import loaddatabase

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
                          'filter_owned':"false", 'filter_event':"QuickDraft_RNA_20190315",
                          "filter_wcr":"", "filter_wcm":"", })

    data_this = result.json()

    unique_ids = set([x['_id'] for x in data_this['result']])

    n_unique = len(unique_ids - data_ids)

    data += data_this['result']

    data_ids = data_ids | unique_ids

    print(f"Added {n_unique} new ids of {len(unique_ids)} retrieved, total {len(data)}")

    # download each deck / match result entry
    for entry in data_this['result']:
        time.sleep(.25) # again, give the server a break
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

from sklearn.model_selection import train_test_split

modeldf = df.merge(MainDeckCards,left_index=True,right_index=True).reset_index(drop=True)
#X = StandardScaler().fit_transform(modeldf[feature_list])
modeldf = modeldf.loc[(modeldf['GoodDeck']==1) | (modeldf['GoodDeck']==0)]
modeldf['GoodDeck'] = modeldf['GoodDeck'].apply(int)

X_train, X_test, y_train, y_test = train_test_split(modeldf[feature_list], modeldf['GoodDeck'], test_size=0.25)

#from sklearn.linear_model import LogisticRegression
#logmodel = LogisticRegression()
#logmodel.fit(X_train,y_train)
#pd.crosstab(y_test, logmodel.predict(X_test), rownames=['Actual'], colnames=['Predicted'])

#from sklearn.metrics import classification_report
#print(classification_report(y_test,predictions))

#%matplotlib inline
#import matplotlib.pyplot as plt
#plt.spy(logit)

#from sklearn.decomposition import FactorAnalysis
#factor = FactorAnalysis(1).fit(X)

#df=pd.DataFrame(factor.components_)

# Import the model we are using
from sklearn.ensemble import RandomForestClassifier

# Instantiate model with 1000 decision trees
rf = RandomForestClassifier(n_estimators=400, min_samples_split=2, min_samples_leaf=2, max_features='sqrt', max_depth=60, bootstrap=True)

# Train the model on training data
rf.fit(X_train, y_train)

pd.crosstab(y_test, rf.predict(X_test), rownames=['Actual'], colnames=['Predicted'])

feature_importances = pd.DataFrame(rf.feature_importances_,
                                   index = X_train.columns,
                                    columns=['importance']).sort_values('importance', ascending=False)

# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 100, stop = 1000, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]

from sklearn.model_selection import RandomizedSearchCV
# Create the random grid
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}

# Use the random grid to search for best hyperparameters
# First create the base model to tune
rf = RandomForestRegressor()
# Random search of parameters, using 3 fold cross validation, 
# search across 100 different combinations, and use all available cores
rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = 3, verbose=2, random_state=42, n_jobs = -1)

# Fit the random search model
rf_random.fit(X_train, y_train)

rf_random.best_params_

rf = RandomForestClassifier(n_estimators=500)

# Train the model on training data
rf.fit(X_train, y_train)

pd.crosstab(y_test, rf.predict(X_test), rownames=['Actual'], colnames=['Predicted'])