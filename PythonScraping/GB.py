GB= df[df['Colors']=='[3, 5]']

maindeck=GB['CourseDeck.mainDeck'].apply(json_normalize)
maindeck=pd.concat(maindeck.to_dict(),axis=0)
maindeck = maindeck.loc[maindeck['quantity'] > 0]
maindeck.index = maindeck.index.set_names(['DeckID', 'Seq'])
maindeck.reset_index(inplace=True)  
maindeck['id']=pd.to_numeric(maindeck['id'])
maindeck=maindeck.merge(carddata)
maindeck=maindeck.merge(GB,left_on='DeckID', right_index=True)


list(GB)
cardwinrates = maindeck.groupby('name')[['ModuleInstanceData.WinLossGate.CurrentWins','ModuleInstanceData.WinLossGate.CurrentLosses']].sum().reset_index()
cardwinrates['W/L'] = cardwinrates['ModuleInstanceData.WinLossGate.CurrentWins']/(cardwinrates['ModuleInstanceData.WinLossGate.CurrentLosses']+cardwinrates['ModuleInstanceData.WinLossGate.CurrentWins'])
