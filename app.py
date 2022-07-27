
from flask import Flask, render_template, url_for
import plotly.express as px
import json
import plotly

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test/<variable>')
def function(variable):
    long_df = px.data.medals_long()
    fig = px.bar(long_df, x="nation", y="count", color="medal", title="Long-Form Input")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('test.html', variable=variable, fig=graphJSON)

## add functions here (or in lib function) that create the charts
## pass each chart as a variable?

