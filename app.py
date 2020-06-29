import os
import arrow
import requests
import functools
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from flask import Flask, json
from dash import Dash
from dash.dependencies import Input, Output
import random
import dash_table
import dash

external_js = [
    # jQuery, DataTables, script to initialize DataTables
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    '//cdn.datatables.net/1.10.15/js/jquery.dataTables.min.js',
    'https://codepen.io/jackdbd/pen/bROVgV.js',
]

external_css = [
    # dash stylesheet
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css?family=Raleway',
    # 'https://fonts.googleapis.com/css?family=Lobster',
    '//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    '//cdn.datatables.net/1.10.15/css/jquery.dataTables.min.css',
]

tableDf = pd.read_csv('bio.csv')
req = requests.get('https://restcountries.eu/rest/v2/all')  #url)
data = json.loads(req.text)

# local development
# with open('4.5_month.geojson') as data_file:
#     data = json.load(data_file)

mapbox_access_token = os.environ.get(
    'MAPBOX_ACCESS_TOKEN',
    'pk.eyJ1IjoiZ2FycmV0dG1yb2JlcnRzIiwiYSI6ImNrYmdwZ2E3eTB6bWUycm10dXQ1c21vejgifQ.4kBlVdoIqSBbIJ_2_XhURQ'
)
'''@author:arjun'''
# http://colorbrewer2.org/#type=sequential&scheme=YlOrRd&n=5
colorscale_magnitude = [
    [0, '#ffffb2'],
    [0.25, '#fecc5c'],
    [0.5, '#fd8d3c'],
    [0.75, '#f03b20'],
    [1, '#bd0026'],
]

# http://colorbrewer2.org/#type=sequential&scheme=Greys&n=3
colorscale_depth = [
    [0, '#f0f0f0'],
    [0.5, '#bdbdbd'],
    [0.1, '#636363'],
]

sizeC = []
colorC = []
theme = {
    'font-family': 'Raleway',
    'background-color': '#787878',
}


def convert_timestamp(timestamp_ms):
    return arrow.get(timestamp_ms / 1000.0).format()


def create_dataframe(d):
    try:
        lat = [x['latlng'] for x in d]
        longL = []
        latL = []
        for i in lat:
            try:
                longL.append(i[1])
                latL.append(i[0])
            except:
                longL.append(0)
                latL.append(0)
        dd = {
            'Place': [x['name'] for x in d],
            'Population': [x['population'] for x in d],
            'Time': [x['timezones'] for x in d],
            'Capital': [x['capital'] for x in d],
            'Longitude': longL,
            'Latitude': latL,
            'area': [x['area'] for x in d],
            'Text': []
        }

    except Exception as e:
        print([x['name'] for x in d])
        # html text to display when hovering
    for i in range(len(dd['Place'])):
        sizeC.append(random.randint(1, 5))
        colorC.append(random.randint(1, 5))
        text = '{}<br>{}<br>Population: {}<br>area: {} sq.km'.format(
            dd['Time'][i], dd['Place'][i], dd['Population'][i], dd['area'][i])
        dd['Text'].append(text)
    print(
        len(dd['Place']), len(dd['Population']), len(dd['Time']),
        len(dd['Capital']), len(dd['Longitude']), len(dd['Latitude']),
        len(dd['area']), len(dd['Text']))
    return pd.DataFrame(dd)


def create_metadata(d):
    dd = {
        'title': d['metadata']['title'],
        'api': d['metadata']['api'],
    }
    return dd


dataframe = create_dataframe(data)

#metadata = create_metadata(data)
# print(dataframe.head())


def create_header(some_string):
    header_style = {
        'backgroundColor': theme['background-color'],
        'padding': '1.5rem',
    }
    header = html.Header(html.H1(children=some_string, style=header_style))
    return header


def create_dropdowns():
    drop1 = dcc.Dropdown(
        options=[
            {
                'label': 'Light',
                'value': 'light'
            },
            {
                'label': 'Dark',
                'value': 'dark'
            },
            {
                'label': 'Satellite',
                'value': 'satellite'
            },
        ],
        value='dark',
        id='dropdown-map-style',
        className='three columns offset-by-one')
    drop2 = dcc.Dropdown(
        options=[
            {
                'label': 'World',
                'value': 'world'
            },
            {
                'label': 'Europe',
                'value': 'europe'
            },
            {
                'label': 'North America',
                'value': 'north_america'
            },
            {
                'label': 'South America',
                'value': 'south_america'
            },
            {
                'label': 'Africa',
                'value': 'africa'
            },
            {
                'label': 'Asia',
                'value': 'asia'
            },
            {
                'label': 'Oceania',
                'value': 'oceania'
            },
        ],
        value='world',
        id='dropdown-region',
        className='three columns offset-by-four')
    return [drop1, drop2]


def create_content():
    # create empty figure. It will be updated when _update_graph is triggered
    graph = dcc.Graph(id='graph-geo')
    content = html.Div(graph, id='content')
    return content


regions = {
    'world': {
        'lat': 0,
        'lon': 0,
        'zoom': 1
    },
    'europe': {
        'lat': 50,
        'lon': 0,
        'zoom': 3
    },
    'north_america': {
        'lat': 40,
        'lon': -100,
        'zoom': 2
    },
    'south_america': {
        'lat': -15,
        'lon': -60,
        'zoom': 2
    },
    'africa': {
        'lat': 0,
        'lon': 20,
        'zoom': 2
    },
    'asia': {
        'lat': 30,
        'lon': 100,
        'zoom': 2
    },
    'oceania': {
        'lat': -10,
        'lon': 130,
        'zoom': 2
    },
}

app_name = 'BiosectRx 	\U0001f468\u200D\U0001f4bb'
server = Flask(app_name)

app = dash.Dash(
    __name__,
    meta_tags=[{
        'name': 'description',
        'content': 'My description'
    }, {
        'http-equiv': 'X-UA-Compatible',
        'content': 'IE=edge'
    }])

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.title = 'BiosectRx'
app.config['suppress_callback_exceptions'] = True

for js in external_js:
    app.scripts.append_script({'external_url': js})

for css in external_css:
    app.css.append_css({'external_url': css})

app.layout = html.Div(
    children=[
        create_header(app_name),
        html.
        Div(children=[
            html.Div(
                create_content(),
                className='row',
                style={
                    "margin-top": "2%",
                    "margin-bottom": "2%"
                }),
            html.
            Div(html.Div(
                [
                    dcc.Dropdown(
                        options=[
                            {
                                'label': 'Light',
                                'value': 'light'
                            },
                            {
                                'label': 'Dark',
                                'value': 'dark'
                            },
                            {
                                'label': 'Satellite',
                                'value': 'satellite'
                            },
                        ],
                        value='dark',
                        id='dropdown-map-style',
                        className='five columns'),
                    html.Div(
                        "         ‎‎‎‎‎‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎",
                        className="two columns"),
                    dcc.Dropdown(
                        options=[
                            {
                                'label': 'World',
                                'value': 'world'
                            },
                            {
                                'label': 'Europe',
                                'value': 'europe'
                            },
                            {
                                'label': 'North America',
                                'value': 'north_america'
                            },
                            {
                                'label': 'South America',
                                'value': 'south_america'
                            },
                            {
                                'label': 'Africa',
                                'value': 'africa'
                            },
                            {
                                'label': 'Asia',
                                'value': 'asia'
                            },
                            {
                                'label': 'Oceania',
                                'value': 'oceania'
                            },
                        ],
                        value='world',
                        id='dropdown-region',
                        className='five columns'),
                ],
                className='row',
                style={
                    "margin-bottom": "2%"
                }),
                className="twelve columns"),
            dash_table.DataTable(
                id='table123',
                columns=[{
                    "name": i,
                    "id": i
                } for i in tableDf.columns],
                data=tableDf.to_dict("rows"),
                style_cell_conditional=[{
                    'if': {
                        'column_id': c
                    },
                    'textAlign': 'left'
                } for c in ['Company Name', 'Classification', "Country"]],
                style_data_conditional=[{
                    'if': {
                        'row_index': 'odd'
                    },
                    'backgroundColor': 'rgb(248, 248, 248)'
                }],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }),
        ], ),
        # html.Hr(),
    ],
    className='container',
    style={
        'font-family': theme['font-family']
    })


@app.callback(
    output=Output('graph-geo', 'figure'),
    inputs=[
        Input('dropdown-map-style', 'value'),
        Input('dropdown-region', 'value')
    ])
def _update_graph(map_style, region):
    dff = dataframe
    radius_multiplier = {'inner': 1.5, 'outer': 3}

    layout = go.Layout(
        title="World-Map",
        autosize=True,
        hovermode='closest',
        height=750,
        font=dict(family=theme['font-family']),
        margin=go.Margin(l=0, r=0, t=45, b=10),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=regions[region]['lat'],
                lon=regions[region]['lon'],
            ),
            pitch=0,
            zoom=regions[region]['zoom'],
            style=map_style,
        ),
    )

    data = go.Data([
        # outer circles represent magnitude
        go.Scattermapbox(
            lat=dff['Latitude'],
            lon=dff['Longitude'],
            mode='markers',
            marker=go.Marker(
                size=sizeC,
                colorscale=colorscale_magnitude,
                color=colorC,
                opacity=1,
            ),
            text=dff['Text'],
            # hoverinfo='text',
            showlegend=False,
        ),
        # inner circles represent depth
        go.Scattermapbox(
            lat=dff['Latitude'],
            lon=dff['Longitude'],
            mode='markers',
            marker=go.Marker(
                size=sizeC,
                colorscale=colorscale_depth,
                color=colorC,
                opacity=1,
            ),
            # hovering behavior is already handled by outer circles
            hoverinfo='skip',
            showlegend=False),
    ])

    figure = go.Figure(data=data, layout=layout)
    return figure


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=True, port=port, threaded=True)

