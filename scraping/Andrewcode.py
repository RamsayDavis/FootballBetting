import requests
import bs4
import json
import pandas as pd
from tqdm import tqdm  # optional: for progress bar

input_files = {'matches': 'Xscores_urls/Xscores_2021-2022.csv'}
output_files = {'goals': 'goals_2021-2022.csv', 'cards': 'cards_2021-2022.csv'}

output_data = {'goals': [], 'cards': []}

# Read URLs
df = pd.read_csv(input_files['matches'])

# Loop over each URL
for _, row in tqdm(df.iterrows(), total = len(df), desc="Processing matches"):
    url = row['url']
    home, away = row['home_team'], row['away_team']
    date = row['date']
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = bs4.BeautifulSoup(response.content, "html.parser")
        page_text = str(soup)
        
        # Find JSON snippet
        a = page_text.find('let matchData') + len('let matchData') + 3 
        b = page_text.find('let urlArr')
        json_text = page_text[a:b].replace(';','').strip()

        match_data = json.loads(json_text)
        timeline = match_data.get('timeline', [])

        for event in timeline:
            if event['typeName'] in ('Regular goal', 'Own goal', 'Penalty'):
                output_data['goals'].append({
                    'URL': url,
                    'Home Team': home,
                    'Away Team': away,
                    'date': date,
                    'Goal Type': event['typeName'],
                    'Score': event['currentScore'],
                    'Player': event['playerName'],
                    'Elapsed Time': event['elapsed'],
                    'Added Time': event.get('elapsedPlus', 0)
                })
            elif event['typeName'] in ('Yellow card', 'Yellow card 2', 'Red card'):
                output_data['cards'].append({
                    'URL': url,
                    'Home Team': home,
                    'Away Team': away,
                    'date': date,
                    'Card Type': event['typeName'],
                    'Side': event['side'],
                    'Player': event['playerName'],
                    'Elapsed Time': event['elapsed'],
                    'Added Time': event.get('elapsedPlus', 0)
                })
    except Exception as e:
        print(f"Error processing URL: {url}\n{e}")

# Save output
for category, file_path in output_files.items():
    pd.DataFrame(output_data[category]).to_csv(file_path, index=False)

print("Done!")
