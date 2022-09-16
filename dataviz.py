from owners import getOwners
import pandas as pd

def homepageTable():
    table_data = getOwners()
    names = []
    records = []
    power_ranks = []
    power_rank_values = []
    points_for = []
    points_against = []
    optimal_points = []

    for owner in table_data:
        names.append(table_data[owner]['team_name'])
        records.append(str(table_data[owner]['wins']) + ' - ' + str(table_data[owner]['losses']))
        power_ranks.append(int(table_data[owner]['power_rank']))
        power_rank_values.append(table_data[owner]['power_rank_value'])
        points_for.append(table_data[owner]['total_points'])
        points_against.append(table_data[owner]['opponent_points'])
        optimal_points.append(table_data[owner]['optimal_points'])

    data = {'Owner': names, 'Record': records, 'Power Rank': power_ranks, 'Power Rank Values': power_rank_values, 'Points For': points_for, 'Points Against': points_against, 'Optimal Points': optimal_points}
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
            'font-size': '10px',
            'text-align': 'center',
        }, subset=['Record', 'Power Rank', 'Power Rank Values', 'Points For', 'Points Against', 'Optimal Points'])\
        .set_properties(**{
            'font-size': '10px',
            'text-align': 'left'
        }, subset=['Owner'])\
        .set_table_styles(styles)\
        .background_gradient(subset=['Power Rank Values', 'Points For', 'Optimal Points'], cmap='RdYlGn')\
        .background_gradient(subset=['Points Against', 'Power Rank'], cmap='RdYlGn_r')

    html = df.to_html(classes='data', header="true")

    return html