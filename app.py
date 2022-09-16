
from flask import Flask, render_template, url_for
import plotly.express as px
import json
import plotly
from owners import getOwners
from dataviz import homepageTable

app = Flask(__name__)

#######################################
# APP ROUTES
#######################################

@app.route('/')
def index():
    homeTable = homepageTable()
    return render_template('index.html', tables=[homeTable])

@app.route('/test/<variable>')
def function(variable):
    long_df = px.data.medals_long()
    fig = px.bar(long_df, x="nation", y="count", color="medal", title="Long-Form Input")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    test_json_file = open('static/users.json')
    test_json = json.load(test_json_file)
    owners = getOwners()
    table = homepageTable()
    return render_template('test.html', variable=variable, fig=graphJSON, data=owners, tables=[table])

if __name__ == '__main__':
    app.run()

#######################################
# DATA VIZ
#######################################