from fastapi.testclient import TestClient
import pytest
import main
import pandas as pd
from unittest.mock import patch
from fastapi import HTTPException

client = TestClient(main.app)

# Mock player stats DataFrame
mock_player_stats_df = pd.DataFrame({
    'Player': ['LeBron James', 'Kevin Durant', 'Stephen Curry'],
    'Season': ['2010-11', '2012-13', '2021-22'],
    'PER': [25.0, 26.1, 27.3],
    'PTS': [27.0, 28.0, 29.0],
    'AST': [7.0, 5.5, 6.1],
    'TRB': [7.0, 7.8, 5.3],
    'BLK': [0.7, 1.1, 0.3],
    'TOV': [3.5, 2.8, 3.1],
    '3PA': [5.7, 6.3, 11.1],
    '3P': [2.0, 2.5, 4.1],
    '3P%': [0.350, 0.390, 0.370],
})

# Mock awards DataFrame
mock_awards_df = pd.DataFrame({
    'Season': ['2009-10', '2022-23', '2022-23', '2022-23'],
    'Player': ['Kobe Bryant', 'LeBron James', 'Kevin Durant', 'Stephen Curry'],
    'Award': ['Finals MVP', 'MVP', 'Scoring Leader', 'Three Point Leader']
})

def load_data_mock(base_url: str):
    if base_url.split('/')[-1] == '2099-2100':
        raise HTTPException(status_code=404, detail='Season not found')
    return mock_player_stats_df

@patch('main.load_data_from_github', return_value=mock_player_stats_df)
def test_get_player_stats(mocked_func):
    response = client.get("/players/LeBron James")
    assert response.status_code == 200
    assert "Player" in response.json()[0]
    assert response.json()[0]["Player"] == "LeBron James"
    assert response.json()[0]["PER"] == 25.0

@patch('main.load_data_from_github', return_value=mock_awards_df)
def test_get_awards_by_player(mocked_func):
    response = client.get("/awards/players/LeBron James")
    assert response.status_code == 200
    assert "Player" in response.json()[0]
    assert response.json()[0]["Player"] == "LeBron James"
    assert response.json()[0]["Award"] == "MVP"

@patch('main.load_data_from_github', return_value=mock_player_stats_df)
def test_get_all_players(mocked_func):
    response = client.get("/players")
    assert response.status_code == 200
    assert "Players" in response.json()
    assert "LeBron James" in response.json()["Players"]
    assert "Kevin Durant" in response.json()["Players"]

@patch('main.load_data_from_github', return_value=mock_player_stats_df)
def test_get_player_averages(mocked_func):
    response = client.get("/players/LeBron James/averages")
    assert response.status_code == 200
    assert "PER" in response.json()
    assert "PTS" in response.json()
    assert response.json()["PER"] == 25.0
    assert response.json()["PTS"] == 27.0

@patch('main.load_data_from_github', return_value=mock_player_stats_df)
def test_get_all_stats(mocked_func):
    response = client.get("/players/LeBron James/allseasons")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["Player"] == "LeBron James"

@patch('main.load_data_from_github', return_value=mock_awards_df)
def test_get_awards_by_season(mocked_func):
    response = client.get("/awards/2022-23")
    assert response.status_code == 200
    assert "Player" in response.json()[0]
    assert response.json()[0]["Player"] == "LeBron James"
    assert response.json()[0]["Award"] == "MVP"

@patch('main.load_data_from_github', return_value=mock_awards_df)
def test_get_winners_by_award(mocked_func):
    response = client.get("/awards/types/MVP")
    assert response.status_code == 200
    assert "Player" in response.json()[0]
    assert response.json()[0]["Player"] == "LeBron James"
    assert response.json()[0]["Award"] == "MVP"

@patch('main.load_data_from_github', return_value=mock_awards_df)
def test_get_awards_by_season_and_player(mocked_func):
    response = client.get("/awards/2022-23/LeBron James")
    assert response.status_code == 200
    assert "Player" in response.json()[0]
    assert response.json()[0]["Player"] == "LeBron James"
    assert response.json()[0]["Award"] == "MVP"

@patch('main.load_data_from_github', return_value=mock_player_stats_df)
def test_invalid_player_stats(mocked_func):
    response = client.get("/players/InvalidPlayerName")
    assert response.status_code == 404
    assert "detail" in response.json()

@patch('main.load_data_from_github', side_effect=load_data_mock)
def test_invalid_season(mocked_func):
    response = client.get("/players/LeBron James", params={'season': '2099-2100'})
    assert response.status_code == 404
    assert "detail" in response.json()

@patch('main.load_data_from_github', return_value=mock_player_stats_df)
def test_invalid_stat(mocked_func):
    response = client.get("/top/InvalidStat/2022-23/5")
    assert response.status_code == 400
    assert "detail" in response.json()

@patch('main.load_data_from_github', return_value=mock_awards_df)
def test_invalid_award(mocked_func):
    response = client.get("/awards/types/InvalidAward")
    assert response.status_code == 404
    assert "detail" in response.json()

# Case where no awards data for a given player
@patch('main.load_data_from_github', return_value=mock_awards_df)
def test_no_awards_for_player(mocked_func):
    response = client.get("/awards/players/PlayerWithNoAwards")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"] == "No awards data found for this player"

# Case where no player stats for a given player in a given season
@patch('main.load_data_from_github', return_value=mock_player_stats_df)
def test_no_player_stats_for_season(mocked_func):
    response = client.get("/players/PlayerWithNoStats/2022-23")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"]

# Case where no dataset is found
@patch('main.load_data_from_github', side_effect=HTTPException(status_code=404, detail='Dataset not found'))
def test_no_dataset_found(mocked_func):
    response = client.get("/players/LeBron James")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"] == "Dataset not found"