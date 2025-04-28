import requests
import bs4
import json
import pandas as pd
from tqdm import tqdm  # optional: for progress bar

input_files = {'matches': 'XScores.csv'}
output_files = {'goals': 'goals.csv', 'cards': 'cards.csv'}

output_data = {'goals': [], 'cards': []}

# Read URLs
df = pd.read_csv(input_files['matches'])

# Loop over each URL
for url in tqdm(df['URL'], desc="Processing matches"):

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
                    'Goal Type': event['typeName'],
                    'Score': event['currentScore'],
                    'Player': event['playerName'],
                    'Elapsed Time': event['elapsed'],
                    'Added Time': event.get('elapsedPlus', 0)
                })
            elif event['typeName'] in ('Yellow card', 'Yellow card 2', 'Red card'):
                output_data['cards'].append({
                    'URL': url,
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
