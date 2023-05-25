# NBA-Stats-API

This is an API built using FastAPI for fetching NBA playe stats and awards data from CSV and Excel files hosted on GitHub.

## Setup
To run the API, install the required Python packages via pip:
```bash
pip install fastapi pandas ssl certifi urllib3 openpyxl uvicorn
```
The API can be run locally with:
```bash
uvicorn main:app --reload
```

## Endpoints
### Get Player Stats
`GET /players/{player_name}`

Fetches all regular season stats for a given player in the 2022-23 season by default. The season can be specified as a query parameter. Please note that so far player stats range from 2019 to 2023 only.

`GET /players/LeBron James`

`GET /players/LeBron James?season=2021-22`
### Get All Players
`GET /players`

Returns the names of all players in the 2022-23 season by default. The season can be specified as a query parameter.

`GET /players?season=2021-22`
### Get Player Averages
`GET /players/{player_name}/averages`

Returns a player's average stats in a given season, set to 2022-23 by default. The season can be specified as a query parameter.

`GET /players/LeBron James/averages`

`GET /players/Jayson Tatum/averages?season=2019-20`
### Get Stats Across All Season
`GET /players/{player_name}/allseasons`

Returns a player's stats across all seasons from 2019-2023.

`GET /players/LeBron James/allseasons`
### Get Top Players
`GET /top/{stat}/{season}/{limit}`

Returns the top players in a given stat category for a specified season, limited by a specified number.

`GET /top/PTS/2022-23/5`

`GET /top/AST/2022-23/10`
### Get Awards By Season
`GET /awards/{season}`

Returns the award winners in a given season, from the 2000-01 to 2022-23 seasons. Please note that all award endpoints do not yet include All-NBA and DPOY awards.

`GET /awards/2022-23`
### Get Awards By Player
`GET /awards/players/{player_name}`

Returns all awards a specific player had ever won.

`GET /awards/players/Kobe Bryant`
### Get Winners By Award
`GET /awards/types/{award}`

Returns all winners of a specific award.

`GET /awards/types/MVP`
### Get Awards by Season and Player
`GET /awards/{season}/{player_name}`

Returns all awards won by a specific player in a specific season.

`GET /awards/2009-10/Kobe Bryant`
## Errors
The API will return HTTP error status codes for various types of errors:

- `400 Bad Requests`:  If the client sends a request with invalid parameters
- `404 Not Found`: If no data is found matching the request
- `500 Internal Server Error`: If an error occurs while processing the request

Each error response will include a detail field with a message explaining the error.
## Credits
Data used in this API is gathered from [Basketball Reference](https://www.basketball-reference.com/), an online basketball reference website providing statistics, news, and more. Please make sure to adhere to the [Terms of Use](https://www.sports-reference.com/termsofuse.html) when using the data provided through this API.
