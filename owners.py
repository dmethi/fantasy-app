from sleeperApi import getCurrentWeek, getSeasonStats, getRosters, getWeeklyMatchups, getWeeklyPlayerData, getWeeklyProjectionsData
import json
from scipy.stats import rankdata

"""
Returns a dictionary of the form
'user_id':
    'roster_id' -> int
    'team_name' -> str
    'owner_id' -> str
    'weekly_scores' -> float[]
    'sleeper_rank' -> float
    'opponent_points' -> float
    'power_rank_value' -> float
    'power_rank' -> float
    'optimal_points' -> float
    'total_points' -> float
    'wins' -> int
    'losses' -> int
    'exp_win_probabilities' -> float
    'expected_wins' -> float
    'weekly_expected_wins' -> float[]
    'weekly_opponents' -> string[]

    -- TO ADD --
    'weekly_opponent_points' -> float[]
    'weekly_opponent_expected_wins' -> float[]
"""
def getOwners():
    # dict object instantaition
    ownersDict = {}

    # data calls
    currentWeek = getCurrentWeek()
    rosters = getRosters()
    matchups = getWeeklyMatchups(currentWeek)
    usersData = open('static/users.json')
    users = json.load(usersData)

    # dict object mutation
    ownersDict = addMetadata(ownersDict, rosters, users)
    ownersDict = addWeeklyScores(ownersDict, matchups)
    ownersDict = addSleeperRank(ownersDict, rosters)
    ownersDict = addPowerRank(ownersDict, rosters, matchups, currentWeek)
    ownersDict = addLuckRating(ownersDict, matchups)
    ownersDict = addWeeklyOpponents(ownersDict, matchups)

    return ownersDict

def addMetadata(ownersDict, rosters, users):
    for i in range(0, len(rosters)):
        user_id = rosters[i]['owner_id']
        roster_id = rosters[i]['roster_id']
        team_name = ''
        owner_name = ''
        for j in range(0, len(users)):
            if(users[j]['user_id'] == user_id):
                owner_name = users[j]['display_name']
                team_name = users[j]['metadata']['team_name']

        ownersDict[user_id] = {
            'roster_id': roster_id,
            'team_name': team_name,
            'owner_name': owner_name
        }

    return ownersDict

def addWeeklyScores(ownersDict, matchups):
    for owner in ownersDict:
        weekly_scores = []
        for i in range(0, len(matchups)):
            for matchup in matchups[i]:
                if matchup['roster_id'] == ownersDict[owner]['roster_id']:
                    weekly_scores.append(matchup['points'])
        ownersDict[owner]['weekly_scores'] = weekly_scores

    return ownersDict

def addSleeperRank(ownersDict, rosters):
    sleeper_rank_values = []

    for owner in ownersDict:
        opponent_points = 0
        wins = 0
        losses = 0
        for i in range(0, len(rosters)):
            if(owner == rosters[i]['owner_id']):
                sleeper_rank_values.append(rosters[i]['settings']['fpts'] ** (rosters[i]['settings']['wins'] + 1))
                opponent_points = rosters[i]['settings']['fpts_against'] + (rosters[i]['settings']['fpts_against_decimal'] * 0.01)
                wins = rosters[i]['settings']['wins']
                losses = rosters[i]['settings']['losses']

        ownersDict[owner]['opponent_points'] = opponent_points
        ownersDict[owner]['wins'] = wins
        ownersDict[owner]['losses'] = losses

    sleeper_ranks = 13 - rankdata(sleeper_rank_values)
    i = 0

    for owner in ownersDict:
        ownersDict[owner]['sleeper_rank'] = sleeper_ranks[i]
        i = i + 1

    return ownersDict

def addPowerRank(ownersDict, rosters, matchups, current_week):
    power_rank_values = []

    for owner in ownersDict:
        total_points = 0
        optimal_points = 0
        three_week_avg = 0
        num_weeks = 0

        for i in range(0, len(rosters)):
            if(owner == rosters[i]['owner_id']):
                total_points = rosters[i]['settings']['fpts'] + (rosters[i]['settings']['fpts_decimal'] * 0.01)
                optimal_points = rosters[i]['settings']['ppts'] + (rosters[i]['settings']['ppts_decimal'] * 0.01)

        for j in range(max(0, len(matchups) - 3), len(matchups)):
            num_weeks = num_weeks + 1
            for matchup in matchups[j]:
                if(matchup['roster_id'] == ownersDict[owner]['roster_id']):
                    three_week_avg = three_week_avg + matchup['points']

        three_week_avg = three_week_avg / num_weeks
        power_rank_value = (total_points / (current_week - 1))/3 + (optimal_points / (current_week - 1) / 6) + (three_week_avg) / 3
        power_rank_values.append(power_rank_value)
        ownersDict[owner]['optimal_points'] = optimal_points
        ownersDict[owner]['total_points'] = total_points
        ownersDict[owner]['power_rank_value'] = power_rank_value

    power_ranks = 13 - rankdata(power_rank_values)
    i = 0

    for owner in ownersDict:
        ownersDict[owner]['power_rank'] = power_ranks[i]
        i = i + 1

    return ownersDict

def addLuckRating(ownersDict, matchups):
    weekly_arrays = {}
    for i in range(0, len(matchups)):
        points = []
        roster_ids = []
        for matchup in matchups[i]:
            points.append(matchup['points'])
            roster_ids.append(matchup['roster_id'])

        weekly_min_points = min(points);
        weekly_max_points = max(points);
        exp_win_probabilities = []
        for j in range(0, len(points)):
            exp_win_probabilities.append((points[j] - weekly_min_points) / (weekly_max_points - weekly_min_points))
        expected_wins = rankdata(points) - 1

        week = str(i + 1)
        weekly_arrays[week] = {
            'roster_ids': roster_ids,
            'points': points,
            'exp_win_probabilities': exp_win_probabilities,
            'expected_wins': expected_wins
        }

    roster_data = {}
    for week_data in weekly_arrays:
        week = weekly_arrays[week_data]
        if(week_data == '1'):
            for i in range(0, 12):
                roster_data[week['roster_ids'][i]] = {
                    'points': week['points'][i],
                    'exp_win_probabilities': week['exp_win_probabilities'][i],
                    'expected_wins': week['expected_wins'][i]
                }
        else:
            for i in range(0, 12):
                roster_data[week['roster_ids'][i]]['points'] += week['points'][i]
                roster_data[week['roster_ids'][i]]['exp_win_probabilities'] += week['exp_win_probabilities'][i]
                roster_data[week['roster_ids'][i]]['expected_wins'] += week['expected_wins'][i]

    for owner in ownersDict:
        for id in roster_data:
            if ownersDict[owner]['roster_id'] == id:
                ownersDict[owner]['exp_win_probabilities'] = roster_data[id]['exp_win_probabilities']
                ownersDict[owner]['expected_wins'] = roster_data[id]['expected_wins']

        weekly_expected_wins = []
        for week in weekly_arrays:
            for i in range(0, 12):
                if weekly_arrays[week]['roster_ids'][i] == ownersDict[owner]['roster_id']:
                    weekly_expected_wins.append(weekly_arrays[week]['expected_wins'][i])

        ownersDict[owner]['weekly_expected_wins'] = weekly_expected_wins

    return ownersDict

def addWeeklyOpponents(ownersDict, matchups):
    weekly_roster_matchups = {}
    for week in range(0, len(matchups)):
        roster_matchup = {}
        for matchup in matchups[week]:
            roster_matchup[matchup['roster_id']] = matchup['matchup_id']
        weekly_roster_matchups[int(week) + 1] = roster_matchup

    for owner in ownersDict:
        weekly_opponent_roster_ids = []
        for week in weekly_roster_matchups:
            owner_matchup_id = weekly_roster_matchups[week][ownersDict[owner]['roster_id']]
            for id in weekly_roster_matchups[week]:
                if (id != ownersDict[owner]['roster_id'] and weekly_roster_matchups[week][id] == owner_matchup_id):
                    weekly_opponent_roster_ids.append(id)

        weekly_opponents = []
        for nested_owner in ownersDict:
            for i in range(0, len(weekly_opponent_roster_ids)):
                if ownersDict[nested_owner]['roster_id'] == weekly_opponent_roster_ids[i]:
                    weekly_opponents.append(nested_owner)

        ownersDict[owner]['weekly_opponents'] = weekly_opponents

    return ownersDict