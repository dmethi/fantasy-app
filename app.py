
from flask import Flask, render_template, url_for
import plotly.express as px
import json
import requests
from owners import getOwners, getWeeklyOwnersTable, getWeeklyPositionalPoints, hallOfFameAndShame, scheduleAnalysis
from dataviz import homepageTable, luckTable, getWeeklyPositionalPointsChart, schedulesTable, scheduleStrength, positionalEdges, getRosters
from sleeperApi import getCurrentWeek, getWeeklyMatchups, getWeeklyPlayerData

app = Flask(__name__)

#######################################
# APP CONSTANTS
#######################################

week = getCurrentWeek()
weekly_matchups = getWeeklyMatchups(week)
weekly_player_scores = getWeeklyPlayerData(week)
owners = getOwners()
positional_points = getWeeklyPositionalPoints(weekly_matchups, owners)
hall = hallOfFameAndShame(positional_points, owners)
schedules = scheduleAnalysis(owners)
sched_strength = scheduleStrength(schedules, owners)
edges = positionalEdges(owners, positional_points)

#######################################
# APP ROUTES
#######################################

@app.route('/')
def index():
    homeTable = homepageTable(owners)
    luck = luckTable(owners)
    positional_chart = getWeeklyPositionalPointsChart(positional_points)
    return render_template('index.html', tables=[homeTable, luck, positional_chart, sched_strength, edges], hall=hall)

@app.route('/test/<id>')
def function(id):
    name = owners[id]['team_name']
    record = str(owners[id]['wins']) + ' - ' + str(owners[id]['losses'])
    power_rank = int(owners[id]['power_rank'])
    ppw = round(owners[id]['total_points']/(owners[id]['wins'] + owners[id]['losses']), 2)
    table = getWeeklyOwnersTable(id, owners)
    schedules_data = schedulesTable(id, schedules, owners)
    roster = getRosters(id, owners)
    return render_template('test.html', team_metadata=[name, record, power_rank, ppw], weekly_dict=table, schedules_table = schedules_data, roster=roster)

if __name__ == '__main__':
    app.run()