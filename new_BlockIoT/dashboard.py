# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash,time,json
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input
import plotly.express # type: ignore
from oracle import *
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Markdown('## **Patient Credentials:**',style={'color':'#48233C'}),
            html.Br(),
            html.Br(),
            dcc.Markdown('**First Name: **',style={'color':'#36558F','size':'14'}),dcc.Input(id='fname', value='',placeholder="First Name",type='text'),
            html.Br(),
            html.Br(),
            html.Div([dcc.Markdown('**Last Name: **',style={'color':'#36558F','size':'14'}),dcc.Input(id='lname', value='',placeholder="Last Name",type='text')]),
            html.Br(),
            html.Div([dcc.Markdown('**Date of Birth: **',style={'color':'#36558F','size':'14'}),dcc.Input(id='dob',value='',placeholder="MM-DD-YYYY", type='text')]),
            html.Br(),
            html.Br(),
            html.Button(id='submit-button', type='submit',children='Submit',style={'color':'#40376E','size':'14'})
            ], className='two columns'),
            html.Br(),
            dcc.Markdown('# **               Welcome to BlockIoT!**',style={'color':'#36558F',"text-align":"center"}),
        html.Div([
            dcc.Loading(
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output-1",style={"text-align":"left"}),
                    color='#48233C',
                ),
            html.Br(),
            html.Div(dcc.Graph(id="chart"),style={"height": "90vh"})], className='ten columns'),
    ])
])

@app.callback(Output("loading-output-1", "children"), Input('submit-button', 'n_clicks'))
def input_triggers_spinner(value):
    time.sleep(3)
    return value

@app.callback(
    [Output('fname', 'value'),Output('lname', 'value'),Output('dob', 'value'),Output('chart', "figure")],
    [Input('submit-button', 'n_clicks')],
    [State('fname', 'value'),State('lname', 'value'),State('dob', 'value')])
def update_output(n_clicks,fname,lname,dob):
    if n_clicks != None:
        biometrics = {
            "first_name":fname.lower(),
            "last_name":lname.lower(),
            "dob":dob
        }
        with open('new_BlockIoT/command.json','w') as f:
            json.dump(biometrics,f)
        time.sleep(3)
        with open('new_BlockIoT/graph.json','r') as f:
            return '','','',json.load(f)
        

app.run_server(host='0.0.0.0')