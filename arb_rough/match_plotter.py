import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#importing odds
df = pd.read_csv('odds_2022-2023_v2.csv')
df = df[df['market']=='Over/Under 2.5 Goals']
df = df.drop('Unnamed: 0',axis=1)

#importing goals
goals = pd.read_csv("goals_2022-2023.csv")
goals['Half Time'] = '0'
goals['Goal Scored'] = 'Yes'
goals['date'] = goals['date'].str[:10]

#create new data frame of a match, where it goes minute by minute rather than event by event
def match_df(home,away):
    match_odds = df[(df['Home Team']==home)&(df['Away Team']==away)].copy()

    norm_mins = [(x,0,0) for x in range(0,91)]
    match_odds['time key'] = list(zip(match_odds['Elapsed Time'].astype(int),match_odds['Added Time'].astype(int),match_odds['Half Time'].astype(int)))
    extra_times = set(match_odds['time key'])-set(norm_mins)
    all_times = sorted(norm_mins+list(extra_times))
    new_df = pd.DataFrame(all_times,columns = ['Elapsed Time','Added Time','Half Time'])
    new_df['time key'] = list(zip(new_df['Elapsed Time'].astype(int),new_df['Added Time'].astype(int),new_df['Half Time'].astype(int)))

    under = match_odds[match_odds['Selection']=='Under 2.5 Goals'].copy()
    over = match_odds[match_odds['Selection']=='Over 2.5 Goals'].copy()

    new_df = new_df.merge(under[['time key','Last Traded Price']],on='time key',how ='left')
    new_df = new_df.rename(columns={'Last Traded Price':'Under 2.5 Odds'})
    new_df['Under 2.5 Odds']=new_df['Under 2.5 Odds'].interpolate()
    new_df = new_df.merge(over[['time key','Last Traded Price']],on='time key',how ='left')
    new_df = new_df.rename(columns={'Last Traded Price':'Over 2.5 Odds'})
    new_df['Over 2.5 Odds']=new_df['Over 2.5 Odds'].interpolate()


    goals2 = goals[(goals['Home Team']==home)&(goals['Away Team']==away)].copy()
    goals2['time key'] = list(zip(goals2['Elapsed Time'].astype(int),goals2['Added Time'].astype(int),goals2['Half Time'].astype(int)))

    new_df = new_df.merge(goals2[['time key','Goal Scored','Player','Goal Type','Score']],on='time key',how ='left')
    new_df['Score']=new_df['Score'].ffill().fillna('0-0')
    new_df['Goal Scored']=new_df['Goal Scored'].fillna('No')
    new_df['synth under']=1/(new_df['Over 2.5 Odds']-1)+1

    def format_time(row):
        if row['Half Time']>0:
            return f'HT{row['Half Time']}'
        elif row['Added Time']>0:
            return f"{row['Elapsed Time']}+{row['Added Time']}"
        else: 
            return f"{row['Elapsed Time']}"

    new_df['plot label'] = new_df.apply(format_time,axis=1)
    
    
    return new_df
#turn a reformatted df into a graph to visualise odds vs goals
def plot_odds(new_df,home,away):
    plt.figure(figsize=(10, 6))
    plt.plot('plot label', 'Under 2.5 Odds', data =new_df ,linestyle='-', color='green', label='Under 2.5 Goals')
    plt.plot('plot label', 'Over 2.5 Odds', data =new_df, linestyle='-', color='blue', label='Over 2.5 Goals')
    #plt.plot('plot label', 'synth under', data =new_df, linestyle='-', color='blue', label='synth under')

    y_max = max(new_df['Over 2.5 Odds'].max(),new_df['Under 2.5 Odds'].max())
    #y_range = np.arange(0,y_max,y_max//20)
    plt.xticks(new_df['plot label'],'',rotation=45)
    #plt.yticks(y_range)
    plt.grid()

    goal_times = new_df[new_df['Goal Scored']=='Yes']['plot label']
    for g in goal_times:
        plt.axvline(x=g,color='red',linestyle='--',alpha=0.6)
    imp_times = ['0','HT1','46','90']

    for g in imp_times:
        plt.axvline(x=g,color='orange',linestyle='-',alpha=0.6)
    plt.xlabel('Elapsed Time (minutes)')
    plt.ylabel('Last Traded Price')
    plt.title(f'Last Traded Price Over Time for {home} vs {away}')
    plt.legend()
    
#go through a list of teams, and for each possible combo make the graph
def generate_graphs(teams):
    for home in teams:
        for away in teams:
            if home == away:
                continue
            plot_odds(match_df(home,away),home,away)
    plt.show()

teams = ['Arsenal','Crystal Palace','Brighton']
generate_graphs(teams)