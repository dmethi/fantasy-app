from cmath import exp
from sleeperApi import getCurrentWeek, getRosters, getWeeklyMatchups, getWeeklyPlayerData, getWeeklyProjectionsData, getUsers
import json
from scipy.stats import rankdata
import pandas as pd

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
"""
def getOwners():
    # dict object instantaition
    ownersDict = {}

    # data calls
    currentWeek = getCurrentWeek()
    rosters = getRosters()
    matchups = getWeeklyMatchups(currentWeek)
    users = getUsers()

    # dict object mutation
    ownersDict = addMetadata(ownersDict, rosters, users)
    ownersDict = addWeeklyScores(ownersDict, matchups)
    ownersDict = addSleeperRank(ownersDict, rosters)
    ownersDict = addPowerRank(ownersDict, rosters, matchups, currentWeek)
    ownersDict = addLuckRating(ownersDict, matchups)
    ownersDict = addWeeklyOpponents(ownersDict, matchups)
    ownersDict = addRosters(ownersDict, rosters)

    return ownersDict

def addRosters(ownersDict, rosters):
    for roster in rosters:
        for owner in ownersDict:
            if roster['roster_id'] == ownersDict[owner]['roster_id']:
                ownersDict[owner]['starters'] = roster['starters']
                ownersDict[owner]['full_roster'] = roster['players']
                ownersDict[owner]['ir'] = roster['reserve']

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
        weekly_scores = {}
        for i in range(0, len(matchups)):
            for matchup in matchups[i]:
                if matchup['roster_id'] == ownersDict[owner]['roster_id']:
                    weekly_scores[str(i + 1)] = matchup['points']
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
        expected_wins = expected_wins.tolist()

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

        weekly_expected_wins = {}
        for week in weekly_arrays:
            for i in range(0, 12):
                if weekly_arrays[week]['roster_ids'][i] == ownersDict[owner]['roster_id']:
                    weekly_expected_wins[week] = (weekly_arrays[week]['expected_wins'][i])

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

        weekly_opponents = {}
        for nested_owner in ownersDict:
            for i in range(0, len(weekly_opponent_roster_ids)):
                if ownersDict[nested_owner]['roster_id'] == weekly_opponent_roster_ids[i]:
                    weekly_opponents[i + 1] = nested_owner

        ownersDict[owner]['weekly_opponents'] = weekly_opponents

    return ownersDict

def getMaxAndMinPoints(ownersDict):
    max_points = 100
    min_points = 100
    for owner in ownersDict:
        for points in ownersDict[owner]['weekly_scores'].values():
            if points > max_points:
                max_points = points
            if points < min_points:
                min_points = points

    return [max_points, min_points]

def getWeeklyOwnersTable(owner, ownersDict):
    wins = []
    week_list = []
    points = []
    opp_points = []
    expected_wins = []
    opp_expected_wins = []
    opponent = []
    currentWeek = getCurrentWeek()
    max_and_min = getMaxAndMinPoints(ownersDict)
    max = max_and_min[0]
    min = max_and_min[1]
    for i in range (0, currentWeek - 1):
        week = i + 1
        # lineup points
        week_points = ownersDict[owner]['weekly_scores'][str(week)]
        points.append(week_points)

        # opponent name
        opponent.append(ownersDict[ownersDict[owner]['weekly_opponents'][week]]['team_name'])

        # opp points
        opp_week_points = ownersDict[ownersDict[owner]['weekly_opponents'][week]]['weekly_scores'][str(week)]
        opp_points.append(opp_week_points)

        # expected wins
        weekly_expected_wins = ownersDict[owner]['weekly_expected_wins'][str(week)]
        expected_wins.append(weekly_expected_wins)

        # opp expected wins
        opp_weekly_expected_wins = ownersDict[ownersDict[owner]['weekly_opponents'][week]]['weekly_expected_wins'][str(week)]
        opp_expected_wins.append(opp_weekly_expected_wins)

        # wins
        win = ''
        if week_points > opp_week_points:
            win = 'W'
        elif week_points < opp_week_points:
            win = 'L'
        else:
            win = 'T'
        wins.append(win)

        # week
        week_list.append(i + 1)

    data = {'Week': week_list, 'Points': points, 'Opponent': opponent, 'Opp. Points': opp_points, 'Result': wins, 'Exp. Wins': expected_wins, 'Opp. Exp. Wins': opp_expected_wins}
    df = pd.DataFrame(data = data)
    th_props = [
        ('font-size', '10px'),
        ('text-align', 'center'),
    ]
    styles=[dict(selector='th', props=th_props)]
    df = df.style.hide(axis='index')\
        .background_gradient(subset=['Points'], vmin=min, vmax=max, cmap='RdYlGn')\
        .background_gradient(subset=['Opp. Points'], vmin=min, vmax=max, cmap='RdYlGn_r')\
        .background_gradient(subset=['Exp. Wins'], vmin=0, vmax=11, cmap='RdYlGn')\
        .background_gradient(subset=['Opp. Exp. Wins'], vmin=0, vmax=11, cmap='RdYlGn_r')\
        .format('{:.2f}', subset=['Points', 'Opp. Points'])\
        .format('{:.0f}', subset=['Exp. Wins', 'Opp. Exp. Wins'])\
        .set_properties(**{
            'text-align': 'center',
            'height': '30px',
        })\
        .set_table_styles(styles)

    html = df.to_html(classes='data', header="true")
    return html

def getWeeklyPositionalPoints(matchups, ownersDict):
    players_data = open('static/players.json')
    players = json.load(players_data)
    positional_points_dict = {}
    i = 1
    for week in matchups:
        week_dict =  {}
        for matchup in week:
            qb_points = 0
            rb_points = 0
            wr_points = 0
            te_points = 0
            k_points = 0
            dst_points = 0

            owner_id = ''
            for owner in ownersDict:
                if ownersDict[owner]['roster_id'] == matchup['roster_id']:
                    owner_id = owner

            for player in matchup['starters']:
                if player != '0':
                    if players[player]['position'] == 'QB':
                        qb_points = qb_points + matchup['players_points'][player]
                    elif players[player]['position'] == 'RB':
                        rb_points = rb_points + matchup['players_points'][player]
                    elif players[player]['position'] == 'WR':
                        wr_points = wr_points + matchup['players_points'][player]
                    elif players[player]['position'] == 'TE':
                        te_points = te_points + matchup['players_points'][player]
                    elif players[player]['position'] == 'K':
                        k_points = k_points + matchup['players_points'][player]
                    else:
                        dst_points = dst_points + matchup['players_points'][player]

            week_dict[owner_id] = {
                'qb': qb_points,
                'rb': rb_points,
                'wr': wr_points,
                'te': te_points,
                'k': k_points,
                'dst': dst_points
            }
        positional_points_dict[i] = week_dict
        i += 1
    return positional_points_dict

def positionalPointsRevised(matchups, ownersDict):
    players_data = open('static/players.json')
    players = json.load(players_data)
    positional_points_dict = {}
    i = 1
    for week in matchups:
        week_dict =  {}
        for matchup in week:
            qb_points = 0
            rb_points = 0
            wr_points = 0
            te_points = 0
            k_points = 0
            dst_points = 0
            flex_points = 0

            rb_scores = []
            wr_scores = []
            te_scores = []

            owner_id = ''
            for owner in ownersDict:
                if ownersDict[owner]['roster_id'] == matchup['roster_id']:
                    owner_id = owner

            for player in matchup['starters']:
                if player != '0':
                    if players[player]['position'] == 'QB':
                        qb_points = qb_points + matchup['players_points'][player]
                    elif players[player]['position'] == 'RB':
                        rb_scores.append(matchup['players_points'][player])
                    elif players[player]['position'] == 'WR':
                        wr_scores.append(matchup['players_points'][player])
                    elif players[player]['position'] == 'TE':
                        te_scores.append(matchup['players_points'][player])
                    elif players[player]['position'] == 'K':
                        k_points = k_points + matchup['players_points'][player]
                    else:
                        dst_points = dst_points + matchup['players_points'][player]

            if len(rb_scores) == 3:
                flex_points += min(rb_scores)
                for a in rb_scores:
                    rb_points += a
                rb_points -= flex_points
            else:
                for b in rb_scores:
                    rb_points += b

            if len(wr_scores) == 3:
                flex_points += min(wr_scores)
                for c in wr_scores:
                    wr_points += c
                wr_points -= flex_points
            else:
                for d in wr_scores:
                    wr_points += d

            if len(te_scores) == 2:
                flex_points += min(te_scores)
                for e in te_scores:
                    te_points += e
                te_points -= flex_points
            else:
                for f in te_scores:
                    te_points += f

            week_dict[owner_id] = {
                'qb': qb_points,
                'rb': rb_points,
                'wr': wr_points,
                'te': te_points,
                'k': k_points,
                'dst': dst_points,
                'flex': flex_points
            }
        positional_points_dict[i] = week_dict
        i += 1
    return positional_points_dict

def hallOfFameAndShame(positional_points, ownersDict):
    highest_weekly_total = {'points': 0, 'owner': '', 'week': 0}
    lowest_weekly_total = {'points': 100, 'owner': '', 'week': 0}
    highest_qb_weekly_score = {'points': 0, 'owner': '', 'week': 0}
    lowest_qb_weekly_score = {'points': 100, 'owner': '', 'week': 0}
    highest_rb_weekly_score = {'points': 0, 'owner': '', 'week': 0}
    lowest_rb_weekly_score = {'points': 100, 'owner': '', 'week': 0}
    highest_wr_weekly_score = {'points': 0, 'owner': '', 'week': 0}
    lowest_wr_weekly_score = {'points': 100, 'owner': '', 'week': 0}
    highest_te_weekly_score = {'points': 0, 'owner': '', 'week': 0}
    lowest_te_weekly_score = {'points': 100, 'owner': '', 'week': 0}
    highest_k_weekly_score = {'points': 0, 'owner': '', 'week': 0}
    lowest_k_weekly_score = {'points': 100, 'owner': '', 'week': 0}
    highest_dst_weekly_score = {'points': 0, 'owner': '', 'week': 0}
    lowest_dst_weekly_score = {'points': 100, 'owner': '', 'week': 0}
    highest_mov = {'points': 0, 'owner': '', 'week': 0}
    lowest_mov = {'points': 100, 'owner': '', 'week': 0}

    for owner in ownersDict:
        scores = ownersDict[owner]['weekly_scores']
        for week in scores:
            if scores[week] > highest_weekly_total['points']:
                highest_weekly_total['points'] = scores[week]
                highest_weekly_total['owner'] = ownersDict[owner]['team_name']
                highest_weekly_total['week'] = week
            if scores[week] < lowest_weekly_total['points']:
                lowest_weekly_total['points'] = scores[week]
                lowest_weekly_total['owner'] = ownersDict[owner]['team_name']
                lowest_weekly_total['week'] = week

            if scores[week] - ownersDict[ownersDict[owner]['weekly_opponents'][int(week)]]['weekly_scores'][week] > highest_mov['points']:
                highest_mov['points'] = round(scores[week] - ownersDict[ownersDict[owner]['weekly_opponents'][int(week)]]['weekly_scores'][week], 2)
                highest_mov['owner'] = ownersDict[owner]['team_name'] + ' vs. ' + ownersDict[ownersDict[owner]['weekly_opponents'][int(week)]]['team_name']
                highest_mov['week'] = week
            if scores[week] - ownersDict[ownersDict[owner]['weekly_opponents'][int(week)]]['weekly_scores'][week] < lowest_mov['points'] and scores[week] - ownersDict[ownersDict[owner]['weekly_opponents'][int(week)]]['weekly_scores'][week] > 0:
                lowest_mov['points'] = round(scores[week] - ownersDict[ownersDict[owner]['weekly_opponents'][int(week)]]['weekly_scores'][week], 2)
                lowest_mov['owner'] = ownersDict[owner]['team_name'] + ' vs. ' + ownersDict[ownersDict[owner]['weekly_opponents'][int(week)]]['team_name']
                lowest_mov['week'] = week

    for week in positional_points:
        for owner_code in positional_points[week]:
            owner_id = positional_points[week][owner_code]
            if owner_id['qb'] > highest_qb_weekly_score['points']:
                highest_qb_weekly_score['points'] = owner_id['qb']
                highest_qb_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                highest_qb_weekly_score['week'] = week
            if owner_id['qb'] < lowest_qb_weekly_score['points']:
                lowest_qb_weekly_score['points'] = owner_id['qb']
                lowest_qb_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                lowest_qb_weekly_score['week'] = week
            if owner_id['rb'] > highest_rb_weekly_score['points']:
                highest_rb_weekly_score['points'] = owner_id['rb']
                highest_rb_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                highest_rb_weekly_score['week'] = week
            if owner_id['rb'] < lowest_rb_weekly_score['points']:
                lowest_rb_weekly_score['points'] = owner_id['rb']
                lowest_rb_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                lowest_rb_weekly_score['week'] = week
            if owner_id['wr'] > highest_wr_weekly_score['points']:
                highest_wr_weekly_score['points'] = owner_id['wr']
                highest_wr_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                highest_wr_weekly_score['week'] = week
            if owner_id['wr'] < lowest_wr_weekly_score['points']:
                lowest_wr_weekly_score['points'] = owner_id['wr']
                lowest_wr_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                lowest_wr_weekly_score['week'] = week
            if owner_id['te'] > highest_te_weekly_score['points']:
                highest_te_weekly_score['points'] = owner_id['te']
                highest_te_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                highest_te_weekly_score['week'] = week
            if owner_id['te'] < lowest_te_weekly_score['points']:
                lowest_te_weekly_score['points'] = owner_id['te']
                lowest_te_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                lowest_te_weekly_score['week'] = week
            if owner_id['k'] > highest_k_weekly_score['points']:
                highest_k_weekly_score['points'] = owner_id['k']
                highest_k_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                highest_k_weekly_score['week'] = week
            if owner_id['k'] < lowest_k_weekly_score['points']:
                lowest_k_weekly_score['points'] = owner_id['k']
                lowest_k_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                lowest_k_weekly_score['week'] = week
            if owner_id['dst'] > highest_dst_weekly_score['points']:
                highest_dst_weekly_score['points'] = owner_id['dst']
                highest_dst_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                highest_dst_weekly_score['week'] = week
            if owner_id['dst'] < lowest_k_weekly_score['points']:
                lowest_dst_weekly_score['points'] = owner_id['dst']
                lowest_dst_weekly_score['owner'] = ownersDict[owner_code]['team_name']
                lowest_dst_weekly_score['week'] = week

    hall_dict = {
        'highest_weekly_total': highest_weekly_total,
        'lowest_weekly_total': lowest_weekly_total,
        'highest_qb_weekly_score': highest_qb_weekly_score,
        'lowest_qb_weekly_score': lowest_qb_weekly_score,
        'highest_rb_weekly_score': highest_rb_weekly_score,
        'lowest_rb_weekly_score': lowest_rb_weekly_score,
        'highest_wr_weekly_score': highest_wr_weekly_score,
        'lowest_wr_weekly_score': lowest_wr_weekly_score,
        'highest_te_weekly_score': highest_te_weekly_score,
        'lowest_te_weekly_score': lowest_te_weekly_score,
        'highest_k_weekly_score': highest_k_weekly_score,
        'lowest_k_weekly_score': lowest_k_weekly_score,
        'highest_dst_weekly_score': highest_dst_weekly_score,
        'lowest_dst_weekly_score': lowest_dst_weekly_score,
        'highest_mov': highest_mov,
        'lowest_mov': lowest_mov,
    }

    return hall_dict

def scheduleAnalysis(ownersDict):
    scheduleDict = {}
    for owner in ownersDict:
        he_had_others_record = {}
        others_had_his_record = {}
        for nested_owner in ownersDict:
            if nested_owner != owner:
                wins = 0
                others_wins = 0
                for week in ownersDict[owner]['weekly_opponents'].keys():
                    opponent = ownersDict[nested_owner]['weekly_opponents'][week]
                    opponent_points = ownersDict[opponent]['weekly_scores'][str(week)]
                    if ownersDict[owner]['weekly_scores'][str(week)] >= opponent_points:
                        wins += 1

                    his_opponent = ownersDict[owner]['weekly_opponents'][week]
                    his_opponent_points = ownersDict[his_opponent]['weekly_scores'][str(week)]
                    if ownersDict[nested_owner]['weekly_scores'][str(week)] >= his_opponent_points:
                        others_wins += 1
                he_had_others_record[nested_owner] = wins
                others_had_his_record[nested_owner] = others_wins
        scheduleDict[owner] = {
            'he_had_others_record': he_had_others_record,
            'others_had_his_record': others_had_his_record
        }

    return scheduleDict