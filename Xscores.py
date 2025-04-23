import requests
import bs4
import json
import pandas as pd

input_files = {'matches': r'C:\Users\andre\Documents\Betting\XScores.csv'}

output = ('goals','cards')

output_data = {'goals': [],
               'cards': []}

output_files = {'goals': r'C:\Users\andre\Documents\Betting\goals.csv',
                'cards': r'C:\Users\andre\Documents\Betting\cards.csv'}

df = pd.read_csv(input_files['matches'])

for url in df['URL']:

    response = requests.get(url)

    soup = bs4.BeautifulSoup(response.content, "html.parser")
        
    s = str(soup)
        
    a = s.find('let matchData') + len('let matchData') + 3 

    b = s.find('let urlArr')

    s = s[a:b].replace(';','')

    x = json.loads(s)

    timeline = x['timeline']

    for t in timeline:
        
        if t['typeName'] in ('Regular goal','Own goal','Penalty'):
            
            d = {'URL': url, 
                 'Goal Type':t['typeName'], 
                 'Score': t['currentScore'], 
                 'Player': t['playerName'], 
                 'Elapsed Time': t['elapsed'],
                 'Added Time': t['elapsedPlus']}
          
            output_data['goals'].append(d)
            
        if t['typeName'] in ('Yellow card','Yellow card 2','Red card'):
            
            d = {'URL': url, 
                 'Card Type':t['typeName'],
                 'Side':t['side'],
                 'Player': t['playerName'], 
                 'Elapsed Time': t['elapsed'],
                 'Added Time': t['elapsedPlus']}
          
            output_data['cards'].append(d) 
            
for x in output:

    pd.DataFrame(output_data[x]).to_csv(output_files[x])