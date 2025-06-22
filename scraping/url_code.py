import requests
import pandas as pd
import json


# Function to fetch match details for a given round
def fetch_match_details(season,round_number):
    url = f"https://api.xscores.com/v1/json/stages/{seasoncode[season]}/events?language-type=3&round-name={round_number}&timezone=Europe/London"

    headers = {
        "Authorization": """Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIxemJYOWJwbTlCRWwtMHpzMnA0d3BDdzhtbGhIR1ZfejIwVHBHOUp5ME9VIn0.eyJleHAiOjE3NDYwMzgxMDMsImlhdCI6MTc0NTk5NDkwMywianRpIjoib25ydHJvOjEwMWYyNGJkLTlkY2MtNDUzNi1hODk1LWE4M2IzOTYwZGM0NCIsImlzcyI6Imh0dHBzOi8vYXV0aC54c2NvcmVzLmNvbS9hdXRoL3JlYWxtcy94c2NvcmVzIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImU2MzM5MjA0LTcyZDctNGJlOS1hY2ExLWJhOGRlYjdhZTM0ZCIsInR5cCI6IkJlYXJlciIsImF6cCI6InhzY29yZXMtYXBpIiwic2lkIjoiYTZjNjVlOWEtMTBiNS00ODQ5LWJkZmItYWQ0N2M2MWVhYzEzIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLXhzY29yZXMiLCJvZmZsaW5lX2FjY2VzcyIsIkFETUlOIiwidW1hX2F1dGhvcml6YXRpb24iLCJQUklWSUxFR0VEIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoic2liZXJzIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2liZXJzIiwiZ2l2ZW5fbmFtZSI6InNpYmVycyJ9.UdFfZUcf1Z4jL1ERrVpM-dx7pzF1JpoLO3OyPo2WaWVW1piYEwXFcHoYjbe_6pDL5quR3dtnyiEP3-_jLK2IH4539vs7WCcYpexKMLsDBezV8tPBBgE4Vfc8pcHt7XrEmlxRSzn5S6HFT7VLhU1yrX0YYh0jCcQilfYRv_a4TupTPwnFiyw-Yflxa8HMD7P2EKvn0AjOzt9r4ZNM6ycFrJMJIr8lGMMM6MS8B0iwIKgbCJ0sZnSe50kr4O5GeQYEFcdihBMFV12BbYC4Ldd3zkZpDB36of6oLbu7zeHWiiT8BuEVsYES6e-KbV9aJ_BwRuep3uxejTtVRSkp4yVTHg""",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.xscores.com/",
        "Origin": "https://www.xscores.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        # Check if data is a list
        if isinstance(data, list):
            matches = data
        else:
            matches = data.get("events", [])

        # Collect match details
        match_details = []
        for match in matches:
            home_team = match.get('home', [{}])[0].get('name', 'N/A')
            away_team = match.get('away', [{}])[0].get('name', 'N/A')
            date = match.get('start', 'N/A')
            code = match.get('id', 'N/A')  # Assuming this is the unique 7-digit code

            match_details.append({
                'home_team': home_team,
                'away_team': away_team,
                'date': date,
                'code': code
            })

        return match_details
    else:
        print(f"Failed to fetch data for round {round_number}: {response.text}")
        return []

# Uses other info in df to add the url
def generate_url(row):
    home_team = row['home_team'].lower().replace(" ", "-")
    away_team = row['away_team'].lower().replace(" ", "-")
    date = pd.to_datetime(row['date']).strftime('%d-%m-%Y')  # format date as dd-mm-yyyy
    code = row['code']
    
    # Construct the URL
    url = f"https://www.xscores.com/soccer/match/{home_team}-vs-{away_team}/{date}/{code}"
    return url

# create a dataframe for the season
def season_creator(season):
    all_matches = []
    for round_number in range(1, 39):
        print(f"Fetching data for round {round_number}...")
        round_matches = fetch_match_details(season,round_number)
        all_matches.extend(round_matches)

    # Convert collected data into a DataFrame
    df_matches = pd.DataFrame(all_matches)

    # Add the season to the first column
    df_matches.insert(0, 'season', season)

    # Apply the function to each row in the DataFrame
    df_matches['url'] = df_matches.apply(generate_url, axis=1)

    # Print the DataFrame
    print(f"Total matches collected: {len(df_matches)}")
    print(df_matches.head())  # Print the first few rows to check the data
    return df_matches

seasoncode = {
    "2023/2024": 53010,
    "2022/2023": 39902,
    "2021/2022": 14837,
    "2020/2021": 12851,
    "2019/2020": 10669, 
    "2018/2019": 8337,
    "2017/2018": 6241,
    "2016/2017": 23362,
    "2015/2016": 23361,
    "2014/2015": 23360,
    "2013/2014": 23359,
    "2012/2013": 23358,
    "2011/2012": 23357,
    "2010/2011": 23356,
    "2009/2010": 23355,
    "2008/2009": 23354,
    "2007/2008": 23353,
    "2006/2007": 23352,
    "2005/2006": 23351,
    "2004/2005": 23350,
    "2003/2004": 23349,
    "2002/2003": 23348,
    "2001/2002": 23347,
    "2000/2001": 23346,
    "1999/2000": 23345,
    "1998/1999": 44574,
    "1997/1998": 44583,
    "1996/1997": 44595,
    "1995/1996": 44599,
    "1994/1995": 44608,
    "1993/1994": 44618
}

# Use above to create csv for each season
for season in seasoncode:
    df = season_creator(season)
    output_df = df[['season', 'date', 'home_team', 'away_team', 'url']]
    name_season = season.replace('/','-')
    output_df.to_csv(f'Xscores_{name_season}.csv', index=False)



