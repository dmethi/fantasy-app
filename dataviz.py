import pandas as pd
import plotly.express as px
from sleeperApi import getCurrentWeek
from decimal import Decimal
import json


def homepageTable(table_data):
    names = []
    power_ranks = []
    power_rank_values = []
    points_for = []
    points_against = []
    optimal_points = []

    for owner in table_data:
        names.append(table_data[owner]['team_name'] + ' (' + str(table_data[owner]['wins']) + ' - ' + str(table_data[owner]['losses']) + ')')
        power_ranks.append(int(table_data[owner]['power_rank']))
        power_rank_values.append(table_data[owner]['power_rank_value'])
        points_for.append(table_data[owner]['total_points'])
        points_against.append(table_data[owner]['opponent_points'])
        optimal_points.append(table_data[owner]['optimal_points'])

    data = {'Power Rank': power_ranks, 'Owner': names, 'Power Rank Values': power_rank_values, 'Points For': points_for, 'Points Against': points_against, 'Optimal Points': optimal_points}
    th_props = [
        ('font-size', '10px'),
        ('text-align', 'center'),
    ]
    styles=[dict(selector='th', props=th_props)]

    df = pd.DataFrame(data=data)

    df = df.sort_values(by='Power Rank', ascending=True)
    df = df.style.hide(axis='index')\
        .format('{:.2f}', subset=['Power Rank Values', 'Points For', 'Points Against', 'Optimal Points'])\
        .set_properties(**{
            'text-align': 'center',
            'height': '30px',
        })\
        .set_table_styles(styles)\
        .background_gradient(subset=['Power Rank Values', 'Points For', 'Optimal Points'], cmap='RdYlGn')\
        .background_gradient(subset=['Points Against', 'Power Rank'], cmap='RdYlGn_r')

    html = df.to_html(classes='data', header="true")

    return html

def luckTable(table_data):
    names = []
    luck_ratings = []
    for owner in table_data:
        names.append(table_data[owner]['team_name'])
        luck_ratings.append(table_data[owner]['wins'] - ((table_data[owner]['exp_win_probabilities'] + table_data[owner]['expected_wins'] / 11) / 2))

    data = {'Owner': names, 'Luck Rating': luck_ratings}
    df = pd.DataFrame(data = data)
    luckChart = px.bar(df, x='Luck Rating', y='Owner', color='Luck Rating', color_continuous_scale='temps_r')
    luckChart.update_layout(barmode='stack', yaxis={'categoryorder': 'total ascending'})
    luckChart.update_layout(yaxis_title=None, xaxis_title=None, legend_title=None)
    luckChart.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    luckChart.update_layout(font_family='Avenir')

    html = luckChart.to_html()
    return html

def getWeeklyPositionalPointsChart(data):
    qb_points = []
    rb_points = []
    wr_points = []
    te_points = []
    k_points = []
    dst_points = []

    df_trial = pd.DataFrame()

    for week in data:
        qb_total = 0
        rb_total = 0
        wr_total = 0
        te_total = 0
        k_total = 0
        dst_total = 0
        for owner in data[week]:
            qb_total += data[week][owner]['qb']
            rb_total += data[week][owner]['rb']
            wr_total += data[week][owner]['wr']
            te_total += data[week][owner]['te']
            k_total += data[week][owner]['k']
            dst_total += data[week][owner]['dst']
        qb_points.append(qb_total / 12)
        rb_points.append(rb_total / 12)
        wr_points.append(wr_total / 12)
        te_points.append(te_total / 12)
        k_points.append(k_total / 12)
        dst_points.append(dst_total / 12)
        df_qb_data = {'Week': week, 'Position': 'QB', 'Points': qb_points[week-1]}
        df_trial = df_trial.append(df_qb_data, ignore_index=True)
        df_rb_data = {'Week': week, 'Position': 'RB', 'Points': rb_points[week-1]}
        df_trial = df_trial.append(df_rb_data, ignore_index=True)
        df_wr_data = {'Week': week, 'Position': 'WR', 'Points': wr_points[week-1]}
        df_trial = df_trial.append(df_wr_data, ignore_index=True)
        df_te_data = {'Week': week, 'Position': 'TE', 'Points': te_points[week-1]}
        df_trial = df_trial.append(df_te_data, ignore_index=True)
        df_k_data = {'Week': week, 'Position': 'K', 'Points': k_points[week-1]}
        df_trial = df_trial.append(df_k_data, ignore_index=True)
        df_dst_data = {'Week': week, 'Position': 'DST', 'Points': dst_points[week-1]}
        df_trial = df_trial.append(df_dst_data, ignore_index=True)

    fig = px.bar(df_trial, x='Week', y='Points', color='Position', color_discrete_map={'QB': '#F94144', 'RB': '#F3722C', 'WR': '#F9C74F', 'TE': '#90BE6D', 'K': '#4D908E', 'DST': '#277DA1'})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(font=dict(family='Avenir'))
    fig.update_xaxes(type='category')
    html = fig.to_html()
    return html

def schedulesTable(owner, schedules, ownersDict):
    week = getCurrentWeek()
    he_had_others = []
    others_had_his = []
    owner_names = []
    he_had_others_avg = 0
    others_had_his_avg = 0
    for other in schedules[owner]['he_had_others_record'].keys():
        he_had_others_avg += schedules[owner]['he_had_others_record'][other]/11
        record = str(schedules[owner]['he_had_others_record'][other]) + ' - ' + str(week - 1 - schedules[owner]['he_had_others_record'][other])
        he_had_others.append(record)
        owner_names.append(ownersDict[other]['team_name'])
    for other in schedules[owner]['others_had_his_record'].keys():
        others_had_his_avg += schedules[owner]['others_had_his_record'][other]/11
        record = str(schedules[owner]['others_had_his_record'][other]) + ' - ' + str(week - 1 - schedules[owner]['others_had_his_record'][other])
        others_had_his.append(record)

    owner_names.append('Average')
    he_had_others.append(Decimal(str(round(he_had_others_avg, 2))).normalize())
    others_had_his.append(Decimal(str(round(others_had_his_avg, 2))).normalize())

    he_had_others_header_string = 'If ' + ownersDict[owner]['team_name'] + ' had their schedule'
    others_had_his_header_string = 'If they had ' + ownersDict[owner]['team_name'] + "'s schedule"

    data= {'Team': owner_names, others_had_his_header_string: others_had_his, he_had_others_header_string: he_had_others}
    df = pd.DataFrame(data=data)
    th_props = [
        ('font-size', '10px'),
        ('text-align', 'center'),
    ]
    styles=[dict(selector='th', props=th_props)]
    df = df.style.hide(axis='index')\
        .set_properties(**{
            'text-align': 'center',
            'height': '30px',
        })\
        .set_table_styles(styles)\

    return df.to_html()

def scheduleStrength(schedules, ownersDict):
    arb = []
    team_name = []
    for owner in schedules:
        he_had_others_avg = 0
        others_had_his_avg = 0
        for other in schedules[owner]['he_had_others_record'].keys():
            he_had_others_avg += schedules[owner]['he_had_others_record'][other]/11
        for other in schedules[owner]['others_had_his_record'].keys():
            others_had_his_avg += schedules[owner]['others_had_his_record'][other]/11

        arbitrage = others_had_his_avg - he_had_others_avg
        arb.append(arbitrage)
        team_name.append(ownersDict[owner]['team_name'])

    data = {'Team Name': team_name, 'Wins gained / lost due to schedule': arb}
    df = pd.DataFrame(data=data)

    df = pd.DataFrame(data=data)
    th_props = [
        ('font-size', '10px'),
        ('text-align', 'center'),
    ]
    styles=[dict(selector='th', props=th_props)]
    df = df.sort_values(by='Wins gained / lost due to schedule', ascending=False)
    df = df.style.hide(axis='index')\
        .set_properties(**{
            'text-align': 'center',
            'height': '30px',
        })\
        .set_table_styles(styles)\
        .background_gradient(subset=['Wins gained / lost due to schedule'], cmap='RdYlGn')\
        .format('{:.2f}', subset=['Wins gained / lost due to schedule'])

    return df.to_html()

def positionalEdges(owners, positional_data):
    qb_avg = 0
    rb_avg = 0
    wr_avg = 0
    te_avg = 0
    k_avg = 0
    dst_avg = 0

    week_num = getCurrentWeek() - 1
    owner_avg_data = {}
    league_avg_data = {}
    for week in positional_data:

        for owner in positional_data[week]:
            owner_qb_avg = 0
            owner_rb_avg = 0
            owner_wr_avg = 0
            owner_te_avg = 0
            owner_k_avg = 0
            owner_dst_avg = 0

            qb_avg += positional_data[week][owner]['qb'] / (week_num * 12)
            rb_avg += positional_data[week][owner]['rb'] / (week_num * 12)
            wr_avg += positional_data[week][owner]['wr'] / (week_num * 12)
            te_avg += positional_data[week][owner]['te'] / (week_num * 12)
            k_avg += positional_data[week][owner]['k'] / (week_num * 12)
            dst_avg += positional_data[week][owner]['dst'] / (week_num * 12)

            owner_qb_avg += positional_data[week][owner]['qb'] / week_num
            owner_rb_avg += positional_data[week][owner]['rb'] / week_num
            owner_wr_avg += positional_data[week][owner]['wr'] / week_num
            owner_te_avg += positional_data[week][owner]['te'] / week_num
            owner_k_avg += positional_data[week][owner]['k'] / week_num
            owner_dst_avg += positional_data[week][owner]['dst'] / week_num

            if owner not in owner_avg_data.keys():
                owner_avg_data[owner] = {'qb': owner_qb_avg, 'rb': owner_rb_avg, 'wr': owner_wr_avg, 'te': owner_te_avg, 'k': owner_k_avg, 'dst': owner_dst_avg}
            else:
                owner_avg_data[owner]['qb'] += owner_qb_avg
                owner_avg_data[owner]['rb'] += owner_rb_avg
                owner_avg_data[owner]['wr'] += owner_wr_avg
                owner_avg_data[owner]['te'] += owner_te_avg
                owner_avg_data[owner]['k'] += owner_k_avg
                owner_avg_data[owner]['dst'] += owner_dst_avg

    league_avg_data['qb'] = qb_avg
    league_avg_data['rb'] = rb_avg
    league_avg_data['wr'] = wr_avg
    league_avg_data['te'] = te_avg
    league_avg_data['k'] = k_avg
    league_avg_data['dst'] = dst_avg
    # put in pandas df
    # sort + retrieve top 5 and bottom 5
    # get league averages too for individual owner tables

    owner_positions = []
    positional_edges = []
    raw_points = []

    for owner in owner_avg_data:
        for position in league_avg_data:
            owner_string = owners[owner]['team_name'] + ' ' + position.upper()
            raw_points.append(owner_avg_data[owner][position] )
            positional_edges.append((owner_avg_data[owner][position] - league_avg_data[position]))
            owner_positions.append(owner_string)

    data = {'Owner': owner_positions, 'Weekly Average': raw_points, 'Edge vs. League Average': positional_edges}
    df = pd.DataFrame(data = data)
    df = df.sort_values(by='Edge vs. League Average', ascending=False)
    th_props = [
        ('font-size', '10px'),
        ('text-align', 'center'),
    ]
    styles=[dict(selector='th', props=th_props)]
    df = df.style.hide(axis='index')\
        .set_properties(**{
            'text-align': 'center',
            'height': '30px',
        })\
        .set_table_styles(styles)\
        .background_gradient(subset=['Edge vs. League Average'], cmap='RdYlGn')\
        .format('{:.2f}', subset=['Edge vs. League Average', 'Weekly Average'])

    return df.to_html()

def positionalEdgesRevised(owners, positional_data):
    qb_avg = 0
    rb_avg = 0
    wr_avg = 0
    te_avg = 0
    k_avg = 0
    dst_avg = 0
    flex_avg = 0

    week_num = getCurrentWeek() - 1
    owner_avg_data = {}
    league_avg_data = {}

    for week in positional_data:

        for owner in positional_data[week]:
            owner_qb_avg = 0
            owner_rb_avg = 0
            owner_wr_avg = 0
            owner_te_avg = 0
            owner_k_avg = 0
            owner_dst_avg = 0
            owner_flex_avg = 0

            qb_avg += positional_data[week][owner]['qb'] / (week_num * 12)
            rb_avg += positional_data[week][owner]['rb'] / (week_num * 12)
            wr_avg += positional_data[week][owner]['wr'] / (week_num * 12)
            te_avg += positional_data[week][owner]['te'] / (week_num * 12)
            k_avg += positional_data[week][owner]['k'] / (week_num * 12)
            dst_avg += positional_data[week][owner]['dst'] / (week_num * 12)
            flex_avg += positional_data[week][owner]['flex'] / (week_num * 12)

            owner_qb_avg += positional_data[week][owner]['qb'] / week_num
            owner_rb_avg += positional_data[week][owner]['rb'] / week_num
            owner_wr_avg += positional_data[week][owner]['wr'] / week_num
            owner_te_avg += positional_data[week][owner]['te'] / week_num
            owner_k_avg += positional_data[week][owner]['k'] / week_num
            owner_dst_avg += positional_data[week][owner]['dst'] / week_num
            owner_flex_avg += positional_data[week][owner]['flex'] / week_num

            if owner not in owner_avg_data.keys():
                owner_avg_data[owner] = {'qb': owner_qb_avg, 'rb': owner_rb_avg, 'wr': owner_wr_avg, 'te': owner_te_avg, 'k': owner_k_avg, 'dst': owner_dst_avg, 'flex': owner_flex_avg}
            else:
                owner_avg_data[owner]['qb'] += owner_qb_avg
                owner_avg_data[owner]['rb'] += owner_rb_avg
                owner_avg_data[owner]['wr'] += owner_wr_avg
                owner_avg_data[owner]['te'] += owner_te_avg
                owner_avg_data[owner]['k'] += owner_k_avg
                owner_avg_data[owner]['dst'] += owner_dst_avg
                owner_avg_data[owner]['flex'] += owner_flex_avg

    league_avg_data['qb'] = qb_avg
    league_avg_data['rb'] = rb_avg
    league_avg_data['wr'] = wr_avg
    league_avg_data['te'] = te_avg
    league_avg_data['k'] = k_avg
    league_avg_data['dst'] = dst_avg
    league_avg_data['flex'] = flex_avg
    # put in pandas df
    # sort + retrieve top 5 and bottom 5
    # get league averages too for individual owner tables

    owner_positions = []
    positional_edges = []
    raw_points = []

    for owner in owner_avg_data:
        for position in league_avg_data:
            owner_string = owners[owner]['team_name'] + ' ' + position.upper()
            raw_points.append(owner_avg_data[owner][position])
            positional_edges.append((owner_avg_data[owner][position] - league_avg_data[position]))
            owner_positions.append(owner_string)

    data = {'Owner': owner_positions, 'Weekly Average': raw_points, 'Edge vs. League Average': positional_edges}
    df = pd.DataFrame(data = data)
    df = df.sort_values(by='Edge vs. League Average', ascending=False)
    th_props = [
        ('font-size', '10px'),
        ('text-align', 'center'),
    ]
    styles=[dict(selector='th', props=th_props)]
    df = df.style.hide(axis='index')\
        .set_properties(**{
            'text-align': 'center',
            'height': '30px',
        })\
        .set_table_styles(styles)\
        .background_gradient(subset=['Edge vs. League Average'], cmap='RdYlGn')\
        .format('{:.2f}', subset=['Edge vs. League Average', 'Weekly Average'])

    return df.to_html()

def getRosters(owner, ownersDict):
    roster = ownersDict[owner]['full_roster']
    players = open('static/players.json')
    players_json = json.load(players)

    player_names = []
    player_position = []
    player_team = []
    player_college = []
    player_age = []

    for player in roster:
        if 'full_name' in players_json[player]:
            player_names.append(players_json[player]['full_name'])
        else:
            player_names.append(players_json[player]['first_name'] + ' ' + players_json[player]['last_name'])
        player_position.append(players_json[player]['position'])
        player_team.append(players_json[player]['team'])
        if 'college' in players_json[player]:
            player_college.append(players_json[player]['college'])
        else:
            player_college.append(' ')
        if 'age' in players_json[player]:
            player_age.append(players_json[player]['age'])
        else:
            player_age.append(' ')

    dictionary = {'Name': player_names, 'Position': player_position, 'Team': player_team, 'College': player_college, 'Age': player_age}
    df = pd.DataFrame(data = dictionary)
    th_props = [
        ('font-size', '10px'),
        ('text-align', 'center'),
    ]
    styles=[dict(selector='th', props=th_props)]
    df = df.style.hide(axis='index')\
        .set_properties(**{
            'text-align': 'center',
            'height': '30px',
        })\
        .set_table_styles(styles)\

    return df.to_html()
