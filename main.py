from fastapi import FastAPI, HTTPException, Depends, Path, Query
import pandas as pd
from typing import Optional
import ssl
import certifi
from io import BytesIO
import httpx
import asyncio

app = FastAPI()

async def get_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient() as client:
        yield client

async def load_data_from_github(base_url: str, client: httpx.AsyncClient) -> pd.DataFrame:
    try:
        context = ssl.create_default_context(cafile=certifi.where())

        # Try to load CSV first
        try:
            url = base_url + '.csv'
            response = await client.get(url)
            data = pd.read_csv(BytesIO(response.read()))
            return data
        except Exception:
            pass

        # If CSV fails, try to load XLSX
        url = base_url + '.xlsx?raw=true'  # Add ?raw=true for .xlsx files
        response = client.get(url)
        data = pd.read_excel(BytesIO(response.read()), engine='openpyxl')
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Gets a player's all regular season stats; set to 2022-23 season by default.
@app.get("/players/{player_name}")
async def get_player_stats(player_name: str, season: Optional[str] = Path('2022-23', regex=r'^20\d{2}-\d{2}$'), client: httpx.AsyncClient = Depends(get_client)):
    url = f'https://raw.githubusercontent.com/bayareahomelander/NBA-Stats-API/main/data/{season}'
    data = await load_data_from_github(url, client)

    # If no data for this player, throw an HTTP error
    if data.empty:
        raise HTTPException(status_code=404, detail='Player not found')
    
    player_data = data[data['Player'] == player_name]
    if player_data.empty:
        raise HTTPException(status_code=404, detail='Player not found')
    
    # Convert the data to JSON and return it
    return player_data.to_dict(orient='records')

# Gets all player names; set to 2022-23 season by default.
@app.get('/players')
async def get_all_players(season: Optional[str] = Path('2022-23', regex=r'^20\d{2}-\d{2}$'), client: httpx.AsyncClient = Depends(get_client)):
    url = f'https://raw.githubusercontent.com/bayareahomelander/NBA-Stats-API/main/data/{season}'
    data = await load_data_from_github(url, client)

    if data.empty:
        raise HTTPException(status_code=404, detail='No players found')
    
    player_names = data['Player'].unique().tolist()
    return {'Players':player_names}

async def load_data_for_season(season: str, player_name: str, client: httpx.AsyncClient):
    url = f'https://raw.githubusercontent.com/bayareahomelander/NBA-Stats-API/main/data/{season}'
    data = await load_data_from_github(url, client)
    if data.empty:
        return []

    player_data = data[data['Player'] == player_name]

    # If no data for this player, return an empty list
    if player_data.empty:
        return []

    # Convert the data to a dictionary
    player_data_dict = player_data.to_dict(orient='records')
    for record in player_data_dict:
        record["Season"] = season

    return player_data_dict

# Get player stats across all seasons
@app.get("/players/{player_name}/allseasons")
async def get_all_stats(player_name: str, client: httpx.AsyncClient = Depends(get_client)):
    all_stats = []
    seasons = ['2000-01', '2001-02', '2002-03', '2003-04', '2004-05', '2005-06', '2006-07', '2007-08',
            '2008-09', '2009-10', '2010-11', '2011-12', '2012-13', '2013-14', '2014-15', '2015-16',
            '2016-17', '2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23']

    # Create a task for each season
    tasks = [load_data_for_season(season, player_name, client) for season in seasons]

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)

    # Each result is a list of dicts with stats for one season
    # Combine them all into one list
    for stats in results:
        all_stats.extend(stats)

    # If no data for this player in any season, throw an HTTP error
    if not all_stats:
        raise HTTPException(status_code=404, detail='Player not found in any season')

    # Return the combined stats
    return all_stats

# Returns top players in a category.
@app.get('/top/{stat}/{season}/{limit}')
async def get_top_players(stat: str, season: str = Path('2022-23', regex=r'^20\d{2}-\d{2}$'), limit: int = Path(..., gt=0), client: httpx.AsyncClient = Depends(get_client)):
    url = f'https://raw.githubusercontent.com/bayareahomelander/NBA-Stats-API/main/data/{season}'
    data = await load_data_from_github(url, client)
    if data.empty:
        raise HTTPException(status_code=404, detail='No data found for this season')
    
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
async def get_awards_by_season(season: str = Path('2022-23', regex=r'^20\d{2}-\d{2}$'), client: httpx.AsyncClient = Depends(get_client)):
    url = 'https://github.com/bayareahomelander/NBA-Stats-API/blob/main/data/awardwinners.xlsx?raw=true'
    data = await load_data_from_github(url, client)
    awards_data = data[data['Season'] == season]

    if awards_data.empty:
        raise HTTPException(status_code=404, detail='No awards data found for this season')
    
    return awards_data.to_dict(orient='records')

# Get all awards for a specific player
@app.get("/awards/players/{player_name}")
async def get_awards_by_player(player_name: str, client: httpx.AsyncClient = Depends(get_client)):
    url = 'https://github.com/bayareahomelander/NBA-Stats-API/blob/main/data/awardwinners.xlsx?raw=true'
    try:
        data = await load_data_from_github(url, client)
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
async def get_winners_by_award(award: str, client: httpx.AsyncClient = Depends(get_client)):
    url = 'https://github.com/bayareahomelander/NBA-Stats-API/blob/main/data/awardwinners.xlsx?raw=true'
    data = await load_data_from_github(url, client)
    
    awards_data = data[data['Award'] == award]

    if awards_data.empty:
        raise HTTPException(status_code=404, detail='No data found for this award')
    
    return awards_data.to_dict(orient='records')

# Get all awards for a specific player in a specific season
@app.get("/awards/{season}/{player_name}")
async def get_awards_by_season_and_player(season: str, player_name: str, client: httpx.AsyncClient = Depends(get_client)):
    url = 'https://github.com/bayareahomelander/NBA-Stats-API/blob/main/data/awardwinners.xlsx?raw=true'
    data = await load_data_from_github(url, client)
    if data.empty:
        raise HTTPException(status_code=404, detail='No awards data found')
    
    awards_data = data[(data['Season'] == season) & (data['Player'] == player_name)]

    if awards_data.empty:
        raise HTTPException(status_code=404, detail='No awards data found for this player in this season')
    
    return awards_data.to_dict(orient='records')