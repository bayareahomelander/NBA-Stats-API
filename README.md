# NBA-Stats-API

This is an API built using FastAPI for fetching NBA player stats and awards data from CSV and Excel files hosted on GitHub. Player's average, advanced, and total stats are available from the 2000-01 season to the current season. Stats are regular season only.

## Setup
To run the API, install the required Python packages via pip:
```bash
pip3 install fastapi pandas ssl certifi httpx openpyxl uvicorn
```
The API can be run locally with:
```bash
uvicorn main:app --reload
```

## Endpoints
- `GET /players/{player_name}`: returns a players' stats for a given season
- `GET /players`: returns all player names for a given season
- `GET /players/{player_name}/averages`: returns a player's average stats in a given season
- `GET /players/{player_name}/allseason`: returns a player's stats across all seasons from 2000 to 2023
- `GET /top/{stat}/{season}/limit`: returns the top players in a given stat category, for a given season, limited by the 'limit' parameter
- `GET /awards/{season}`: returns award winners in a given season
- `GET /awards/players/{player_name}`: returns all awards for a specific player
- `GET /awards/types/{award}`: returns all winners of a speicifc award
- `GET /awards/{season}/{player_name}`: returns all awards for a specific player in a specific season

## Errors
The API will return HTTP error status codes for various types of errors:

- `400 Bad Requests`:  If the client sends a request with invalid parameters
- `404 Not Found`: If no data is found matching the request
- `500 Internal Server Error`: If an error occurs while processing the request

Each error response will include a detail field with a message explaining the error.
## Unit Testing
There is a combination of unit tests to verify individual components, and integration tests to check that these components work correctly together.
### Testing Tools
Tests are written using Python's `unittest` module, with the `pytest` framework to run the tests and generate reports. `unittest.mock` is used to isolate components for unit testing.
### Running the Tests
Tests can be run locally by navigating to the project directory and executing the following command:

```bash
pytest test.py
```

Installation might be needed if not already installed:

```bash
pip3 install pytest
```
### Test Coverage
A test coverage report can be generated using the `pytest-cov` plugin. It can be installed using:

```bash
pip3 install pytest-cov
```

This will show the percentage of the code in the main.py file that's covered by the tests.
## Credits
Data used in this API is gathered from [Basketball Reference](https://www.basketball-reference.com/), an online basketball reference website providing statistics, news, and more. Please make sure to adhere to the [Terms of Use](https://www.sports-reference.com/termsofuse.html) when using the data provided through this API.
