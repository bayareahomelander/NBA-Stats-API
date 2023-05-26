from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import pytest
import pandas as pd
from main import app

client = TestClient(app)

@pytest.fixture
def mock_data():
    data = {
        'Player': ['Stephen Curry', 'LeBron James', 'Kevin Durant'],
        'PER': [31.3, 25.0, 26.9],
        'PTS': [32.0, 25.0, 27.0],
        'AST': [5.0, 7.0, 5.0],
        'TRB': [5.0, 8.0, 7.0],
        'BLK': [0.2, 0.5, 0.7],
        'TOV': [3.0, 4.0, 3.0],
        '3PA': [10.0, 5.0, 7.0],
        '3P': [5.0, 2.0, 3.0],
        '3P%': [0.5, 0.4, 0.4]
    }

    return pd.DataFrame(data)

@pytest.fixture
def mock_awards_df():
    data = {
        "Season": ["2009-10", "2009-10", "2019-20", "2019-20", "2020-21", "2020-21"],
        "Player": ["Kobe Bryant", "Kevin Durant", "LeBron James", "Giannis Antetokounmpo", "LeBron James", "Stephen Curry"],
        "Award": ["Finals MVP", "PPG Leader", "Finals MVP", "MVP", "Finals MVP", "MVP"]
    }
    return pd.DataFrame(data)

def test_get_player_stats(mock_data):
    with patch('main.load_data_from_github', return_value=mock_data):
        response = client.get('/players/Stephen Curry')
        assert response.status_code == 200, response.json()['detail']
        assert response.json() == [mock_data[mock_data['Player'] == 'Stephen Curry'].to_dict(orient='records')[0]]


# This is a test for handling empty dataframes, which returns a 404 if the player is not found
def test_get_player_stats_empty_dataframe():
    mock_data = pd.DataFrame()
    with patch('main.load_data_from_github', return_value=mock_data):
        response = client.get('/players/Stephen Curry')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Player not found'}

# This test is for handling invalid player names, which returns a 404 if the player is not found
def test_get_player_stats_not_found(mock_data):
    with patch('main.load_data_from_github', return_value=mock_data):
        response = client.get('/players/NonExistentPlayer')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Player not found'}

# This test is for handling invalid seasons, which returns a 400 if the season is invalid
def test_get_player_stats_invalid_season(mock_data):
    with patch('main.load_data_from_github', side_effect=HTTPException(status_code=400, detail='Invalid season')):
        response = client.get('/players/Stephen Curry?season=2030-31')
        assert response.status_code == 400

def test_get_all_players(mock_data):
    with patch('main.load_data_from_github', return_value=mock_data):
        response = client.get('/players')
        assert response.status_code == 200, response.json()['detail']
        assert response.json() == {'Players': mock_data['Player'].unique().tolist()}

def test_get_player_averages(mock_data):
    with patch('main.load_data_from_github', return_value=mock_data):
        response = client.get('/players/Stephen Curry/averages')
        assert response.status_code == 200, response.json()['detail']
        assert response.json() == {'PER': 31.3, 'PTS': 32.0, 'AST': 5.0, 'TRB': 5.0, 'BLK': 0.2, 'TOV': 3.0, '3PA': 10.0, '3P': 5.0, '3P%': 0.5}

def test_get_player_all_seasons(mock_data):
    with patch('main.load_data_from_github', return_value=mock_data):
        response = client.get('/players/Stephen Curry/all_seasons')
        assert response.status_code == 200, response.json()['detail']
        assert response.json() == mock_data.to_dict(orient='records')

def test_get_top_players(mock_data):
      with patch('main.load_data_from_github', return_value=mock_data):
        response = client.get('/top/PTS/5')
        assert response.status_code == 200
        assert response.json() == mock_data.sort_values(by='PTS', ascending=False).head(5).to_dict(orient='records')

# This test is ensuring that the API behaves correctly when the number of players requested is greater than the number of players in the dataset
def test_get_top_players_more_than_exists(mock_data):
    with patch('main.load_data_from_github', return_value=mock_data):
        response = client.get('/top/PER/2022-23/99999')
        assert response.status_code == 200, response.json()['detail']
        assert len(response.json()) == len(mock_data)

def test_load_data_error():
    with patch('main.load_data_from_github', side_effect=HTTPException(status_code=500, detail='Failed to load data')):
        response = client.get('/players/Stephen Curry')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Failed to load data'}

def test_get_awards_by_season(mock_awards_df):
    with patch('main.load_data_from_github', return_value=mock_awards_df):
        response = client.get('/awards/2020-21')
        assert response.status_code == 200, response.json()['detail']
        assert response.json() == mock_awards_df[mock_awards_df['Season'] == '2020-21'].to_dict(orient='records')

def test_get_awards_by_season_empty_dataframe():
    with patch('main.load_data_from_github', return_value=pd.DataFrame()):
        response = client.get('/awards/2020-21')
        assert response.status_code == 404
        assert response.json() == {'detail': 'No awards data found for this season'}

# This test is for handling invalid seasons, which returns a 400 if the season is invalid
def test_get_awards_by_season_not_found(mock_awards_df):
    with patch('main.load_data_from_github', return_value=mock_awards_df):
        response = client.get('/awards/2030-31')
        assert response.status_code == 404
        assert response.json() == {'detail': 'No awards data found for this season'}

def test_get_awards_by_player(mock_awards_df):
    with patch('main.load_data_from_github', return_value=mock_awards_df):
        response = client.get('/awards/players/LeBron James')
        assert response.status_code == 200, response.json()['detail']
        assert response.json() == mock_awards_df[mock_awards_df['Player'] == 'LeBron James'].to_dict(orient='records')

def test_get_awards_by_player_not_found(mock_awards_df):
    with patch('main.load_data_from_github', return_value=mock_awards_df):
        response = client.get('/awards/players/NonExistentPlayer')
        assert response.status_code == 404
        assert response.json() == {'detail': 'No awards data found for this player'}

def test_get_winners_by_award(mock_awards_df):
    with patch('main.load_data_from_github', return_value=mock_awards_df):
        response = client.get('/awards/types/MVP')
        assert response.status_code == 200, response.json()['detail']
        assert response.json() == mock_awards_df[mock_awards_df['Award'] == 'MVP'].to_dict(orient='records')

def test_get_winners_by_award_not_found(mock_awards_df):
    with patch('main.load_data_from_github', return_value=mock_awards_df):
        response = client.get('/awards/types/NonExistentAward')
        assert response.status_code == 404
        assert response.json() == {'detail': 'No data found for this award'}

def test_get_awards_by_season_and_player(mock_awards_df):
    with patch('main.load_data_from_github', return_value=mock_awards_df):
        response = client.get('/awards/2020-21/LeBron James')
        assert response.status_code == 200, response.json()['detail']
        assert response.json() == mock_awards_df[(mock_awards_df['Season'] == '2020-21') & (mock_awards_df['Player'] == 'LeBron James')].to_dict(orient='records')

def test_get_awards_by_season_and_player_not_found(mock_awards_df):
    with patch('main.load_data_from_github', return_value=mock_awards_df):
        response = client.get('/awards/2030-31/NonExistentPlayer')
        assert response.status_code == 404
        assert response.json() == {'detail': 'No awards data found for this player in this season'}