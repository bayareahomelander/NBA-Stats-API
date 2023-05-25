from fastapi import FastAPI, HTTPException
import pandas as pd
from typing import Optional
import ssl
import certifi
import urllib.request
from io import BytesIO
import os

app = FastAPI()

def load_data_from_github(url: str) -> pd.DataFrame:
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        response = urllib.request.urlopen(url, context=context)
        if os.path.splitext(url)[1] == '.csv':
            data = pd.read_csv(response)
            return data
        else:
            data = pd.read_excel(BytesIO(response.read()), engine='openpyxl')
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Gets a player's all regular season stats; set to 2022-23 season by default.
@app.get("/players/{player_name}")
async def get_player_stats(player_name: str, season: Optional[str] = '2022-23'):
    url = f'https://raw.githubusercontent.com/bayareahomelander/NBA-Stats-API/main/data/{season}.csv'
    data = load_data_from_github(url)
    player_data = data[data['Player'] == player_name]

    # If no data for this player, throw an HTTP error
    if player_data.empty:
        raise HTTPException(status_code=404, detail='Player not found')
    
    # Convert the data to JSON and return it
    return player_data.to_dict(orient='records')

# Gets all player names; set to 2022-23 season by default.
@app.get('/players')
async def get_all_players(season: Optional[str] = '2022-23'):
    url = f'https://raw.githubusercontent.com/bayareahomelander/NBA-Stats-API/main/data/{season}.csv'
    data = load_data_from_github(url)
    
    player_names = data['Player'].unique().tolist()
    return {'Players':player_names}

# Returns a player's average stats in a given season
@app.get('/players/{player_name}/averages')
async def get_player_averages(player_name: str, season: Optional[str] = '2022-23'):
    url = f'https://raw.githubusercontent.com/bayareahomelander/NBA-Stats-API/main/data/{season}.csv'
    data = load_data_from_github(url)
    
    player_data = data[data['Player'] == player_name]
    if player_data.empty:
        raise HTTPException(status_code=404, detail='Player not found')
    
    stats = player_data[['PER', 'PTS', 'AST', 'TRB', 'BLK', 'TOV', '3PA', '3P', '3P%']]

    if stats.empty:
        raise HTTPException(status_code=404, detail='Stats not found')
    
    return stats.to_dict(orient='records')

# Returns a player's stats across all seasons (2019 - 2023)
@app.get("/players/{player_name}/allseasons")
async def get_all_stats(player_name: str):
    seasons = ['2019-20', '2020-21', '2021-22', '2022-23']
    all_stats = []

    for season in seasons:
        url = f'https://raw.githubusercontent.com/bayareahomelander/NBA-Stats-API/main/data/{season}.csv'
        data = load_data_from_github(url)
        
        player_data = data[data['Player'] == player_name]

        # If no data for this player, skip this season
        if player_data.empty:
            continue

        # Convert the data to a dictionary and add it to the all_stats list
        player_data_dict = player_data.to_dict(orient='records')
        for record in player_data_dict:
            record["Season"] = season
        all_stats.extend(player_data_dict)

    # If no data for this player in any season, throw an HTTP error
    if not all_stats:
        raise HTTPException(status_code=404, detail='Player not found in any season')

    # Return the combined stats
    return all_stats

# Returns top players in a category.
@app.get('/top/{stat}/{season}/{limit}')
async def get_top_players(stat: str, season: str, limit: int):
    url = f'https://raw.githubusercontent.com/bayareahomelander/NBA-Stats-API/main/data/{season}.csv'
    data = load_data_from_github(url)
    
    if stat not in data.columns:
        raise HTTPException(status_code=400, detail="Invalid stat category")
    
    try:
        data_sorted = data.sort_values(by=[stat], ascending=False)
        top_players = data_sorted.head(limit)

        # Select only 'Player' and the specified stat column.
        top_players = top_players[['Player', stat]]
    except Exception as e:
        # Handle sorting and limiting errors
        raise HTTPException(status_code=500, detail=str(e))

    return top_players.to_dict(orient='records')

# Returns award winners in each season (2000-01 to 2022-23 season).
@app.get("/awards/{season}")
async def get_awards_by_season(season: str):
    url = 'https://github.com/bayareahomelander/NBA-Stats-API/blob/main/data/awardwinners.xlsx?raw=true'
    data = load_data_from_github(url)
    awards_data = data[data['Season'] == season]

    if awards_data.empty:
        raise HTTPException(status_code=404, detail='No awards data found for this season')
    
    return awards_data.to_dict(orient='records')

# Get all awards for a specific player
@app.get("/awards/players/{player_name}")
async def get_awards_by_player(player_name: str):
    url = 'https://github.com/bayareahomelander/NBA-Stats-API/blob/main/data/awardwinners.xlsx?raw=true'
    try:
        data = load_data_from_github(url)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if 'Player' not in data.columns:
        raise HTTPException(status_code=400, detail="'Player' column not found in the dataset")

    awards_data = data[data['Player'] == player_name]

    if awards_data.empty:
        raise HTTPException(status_code=404, detail='No awards data found for this player')
    
    return awards_data.to_dict(orient='records')

# Get all winners of a specific award
@app.get("/awards/types/{award}")
async def get_winners_by_award(award: str):
    url = 'https://github.com/bayareahomelander/NBA-Stats-API/blob/main/data/awardwinners.xlsx?raw=true'
    data = load_data_from_github(url)
    
    awards_data = data[data['Award'] == award]

    if awards_data.empty:
        raise HTTPException(status_code=404, detail='No data found for this award')
    
    return awards_data.to_dict(orient='records')

# Get all awards for a specific player in a specific season
@app.get("/awards/{season}/{player_name}")
async def get_awards_by_season_and_player(season: str, player_name: str):
    url = 'https://github.com/bayareahomelander/NBA-Stats-API/blob/main/data/awardwinners.xlsx?raw=true'
    data = load_data_from_github(url)
    
    awards_data = data[(data['Season'] == season) & (data['Player'] == player_name)]

    if awards_data.empty:
        raise HTTPException(status_code=404, detail='No awards data found for this player in this season')
    
    return awards_data.to_dict(orient='records')