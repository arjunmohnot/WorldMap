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
from dash.dependencies import Input, Output, State
import random
import dash_table
import dash
import base64
import datetime
import io
import difflib
import openGlobal
import xlrd
import numpy as np
from flask import send_file



# Global

dataframe = None

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

openGlobal.sizeC = []
openGlobal.colorC = []
openGlobal.regions={}
openGlobal.dropdown=[]
theme = {
    'font-family': 'Raleway',
    'background-color': '#787878',
}


def convert_timestamp(timestamp_ms):
    return arrow.get(timestamp_ms / 1000.0).format()




#metadata = create_metadata(data)
# print(dataframe.head())


def create_header(some_string):
    header_style = {
        'backgroundColor': theme['background-color'],
        'padding': '1.5rem',
    }
    header = html.Header(html.H1(children=some_string, style=header_style))
    return header



def create_content():
    # create empty figure. It will be updated when _update_graph is triggered
    graph = dcc.Graph(id='graph-geo')
    content = html.Div(graph, id='content')
    return content




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
       html.Details([
                        html.Summary('Check Input Format 	\ud83d\udcd4'),
			html.Div([html.Div("File can be be of .xls, .xlsx and .csv format. \n It should contains three columns.\n Download the sample excel file for more detail.",style={"margin-bottom":"1%"}),

			html.A("Download Sample Excel 	\ud83d\udcbe", href="/download_excel/", style={'text-decoration': 'none', 'border': 'solid #1EAEDB 1px', 'padding':'10px 10px 10px 10px', 'color':'black'},),
], style={"margin-bottom":"3%"}),

]),
       
         html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
   
], className="ten columns"),
        html.
        Div(children=[
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
                        value=openGlobal.country,
                        id='dropdown-region',
                        className='five columns'),
                ],
                className='row',
                style={
                    "margin-bottom": "18%","margin-top":"3%"
                }),
                className="twelve columns"),
		 
   
        ], ),
        # html.Hr(),
    html.Div(id='output-data-upload',style={"margin-top":"18%"}),
    ],
    className='container',
    style={
        'font-family': theme['font-family']
    })




def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
      if 'csv' in filename:
          # Assume that the user uploaded a CSV file
          df = pd.read_csv(
              io.StringIO(decoded.decode('utf-8')))
      elif 'xls' in filename:
          # Assume that the user uploaded an excel file
          df = pd.read_excel(io.BytesIO(decoded))
      df['Country'].replace('', np.nan, inplace=True)
      df.dropna(subset=['Country'], inplace=True)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])


    d={}
    country=list(df['Country'])
    classification=list(df['Classification'])
    for i in range(len(df)):
      if country[i] in d:
        if classification[i] in d[country[i]]:
          d[country[i]][classification[i]]+=1
        else:
          d[country[i]][classification[i]]=1
      else:
        d[country[i]]={}
        d[country[i]][classification[i]]=1
    #print(d)
    lat = [x['latlng'] for x in data]
    longL = []
    latL = []
    for i in lat:
        try:
            longL.append(i[1])
            latL.append(i[0])
        except:
            longL.append(0)
            latL.append(0)
    Place=[x['name'] for x in data]
    Population=[x['population'] for x in data]
    Timezone=[x['timezones'] for x in data]
    Capital=[x['capital'] for x in data]
    Area=[x['area'] for x in data]
    dd = {
            'Place': [],
            'Population': [],
            'Time': [] ,
            'Capital':[] ,
            'Longitude': [],
            'Latitude': [],
            'area': [],
            'Text': []
        }
    #print(Place)
    print("Error")
    flag=1
    for k,v in d.items():
      try:
        c=difflib.get_close_matches(k, Place)[0]
        exact=Place.index(c)
        if flag==1:
	        openGlobal.country=k
	        flag=0
        openGlobal.regions[k]={'lat': latL[exact],
        'lon': longL[exact],
        'zoom': 4}
        openGlobal.dropdown.append({'label': k,'value': k})
        dd['Place'].append(k)
        dd['Population'].append(Population[exact])
        dd['Time'].append(Timezone[exact])
        dd['Capital'].append(Capital[exact])
        dd['Longitude'].append(longL[exact])
        dd['Latitude'].append(latL[exact])
        dd['area'].append(Area[exact])
        Text=k+"<br>"
        for kk,vv in v.items():
          Text+=str(kk)+" - "+str(vv)+"<br>"
        dd['Text'].append(Text)
        openGlobal.sizeC.append(random.randint(10, 15))
        openGlobal.colorC.append(random.randint(10, 15))
      except Exception as e:
        print(e,k)
        try:
          c=difflib.get_close_matches(k+" of Great", Place)[0]
          exact=Place.index(c)
          dd['Place'].append(k)
          openGlobal.regions[k]={'lat': latL[exact],
          'lon': longL[exact],
          'zoom': 4}
          openGlobal.dropdown.append({'label': k,
          'value': k
          })
          dd['Population'].append(Population[exact])
          dd['Time'].append(Timezone[exact])
          dd['Capital'].append(Capital[exact])
          dd['Longitude'].append(longL[exact])
          dd['Latitude'].append(latL[exact])
          dd['area'].append(Area[exact])
          Text=k+"<br>"
          for kk,vv in v.items():
            Text+=str(kk)+" - "+str(vv)+"<br>"
          dd['Text'].append(Text)
          openGlobal.sizeC.append(random.randint(10, 15))
          openGlobal.colorC.append(random.randint(10, 15))

        except Exception as e:
          print(e,k)
    openGlobal.child = pd.DataFrame(dd)

    return 1
  



@app.callback([Output('output-data-upload', 'children'),Output('dropdown-region', 'options'),Output('dropdown-region', 'value')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        openGlobal.sizeC=[]
        openGlobal.colorC=[]
        openGlobal.regions={}
        openGlobal.dropdown=[]
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        
        return [html.Div([
          create_content()
        ]),openGlobal.dropdown,openGlobal.country]
    return [html.Div(),[],openGlobal.country]






@app.callback(
    output=Output('graph-geo', 'figure'),
    inputs=[
        Input('dropdown-map-style', 'value'),
        Input('dropdown-region', 'value')
    ])
def _update_graph(map_style, region):
    dff = openGlobal.child
    #print(dff)
    radius_multiplier = {'inner': 1.5, 'outer': 3}
    layout = go.Layout(
        title="World-Map",
        autosize=True,
        hovermode='closest',
        height=720,
        font=dict(family=theme['font-family']),
        margin=go.Margin(l=0, r=0, t=45, b=10),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=openGlobal.regions[region]['lat'],
                lon=openGlobal.regions[region]['lon'],
            ),
            pitch=0,
            zoom=openGlobal.regions[region]['zoom'],
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
                size=openGlobal.sizeC,
                colorscale=colorscale_magnitude,
                color=openGlobal.colorC,
                opacity=1,
            ),
            text=dff['Text'],
            hoverinfo='text',
            showlegend=False,
        ),
        # inner circles represent depth
        go.Scattermapbox(
            lat=dff['Latitude'],
            lon=dff['Longitude'],
            mode='markers',
            marker=go.Marker(
                size=openGlobal.sizeC,
                colorscale=colorscale_depth,
                color=openGlobal.colorC,
                opacity=1,
            ),
            # hovering behavior is already handled by outer circles
            hoverinfo='skip',
            showlegend=False),
    ])

    figure = go.Figure(data=data, layout=layout)
    return figure

@app.server.route('/download_excel/')
def download_excel():
    #Create DF
    df = pd.read_csv("bio.csv")

    #Convert DF
    strIO = io.BytesIO()
    excel_writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    df.to_excel(excel_writer, sheet_name="BIO")
    excel_writer.save()
    excel_data = strIO.getvalue()
    strIO.seek(0)

    return send_file(strIO,
                     attachment_filename='BIO.xlsx',
                     as_attachment=True)



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=True, port=port, threaded=True)


