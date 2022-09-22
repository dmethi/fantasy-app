from array import array
import requests

def getCurrentWeek() -> int:
    nfl_state = requests.get('https://api.sleeper.app/v1/state/nfl').json()
    return nfl_state['week']

def getRosters() -> any:
    return requests.get('https://api.sleeper.app/v1/league/858866071007019008/rosters').json()

def getUsers() -> any:
    return requests.get('https://api.sleeper.app/v1/league/858866071007019008/users').json()

def getWeeklyMatchups(week) -> array:
    weekly_matchups_data = []
    for i in range (1, week):
        matchups_request_url = 'https://api.sleeper.app/v1/league/858866071007019008/matchups/' + str(i)
        matchups = requests.get(matchups_request_url).json()
        weekly_matchups_data.append(matchups)
    return weekly_matchups_data

def getWeeklyPlayerData(week) -> array:
    weekly_player_data = []
    for i in range (1, week):
        player_data_request_url = 'https://api.sleeper.app/v1/stats/regular/2022/' + str(i)
        player_data = requests.get(player_data_request_url).json()
        weekly_player_data.append(player_data)
    return weekly_player_data

def getWeeklyProjectionsData(week) -> array:
    weekly_projections_data = []
    for i in range (1, week):
        projections_data_request_url = 'https://api.sleeper.app/v1/stats/projections/2022/' + str(i)
        projections_data = requests.get(projections_data_request_url).json()
        weekly_projections_data.append(projections_data)
    return weekly_projections_data
