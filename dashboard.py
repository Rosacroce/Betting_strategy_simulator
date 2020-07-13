# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 13:55:03 2020

@author: aless
"""

import base64
import datetime
import io

import plotly.graph_objects as go

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__) #, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Data Analysis Assistant', className='header1-main'),
    dcc.Tabs(id='tabs', value='tab-input',
             children=[
                 dcc.Tab(label='Input', value='tab-input',
                         children=[
                                 dcc.Store(id='memory-output'),
                                 html.Div([
                                     html.Div(className='vertical-separator'),
                                     dcc.Upload(
                                        id='upload-data',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select Files')
                                        ]),
                                        style={
                                            'width': '20%',
                                            'height': '40px',
                                            'lineHeight': '40px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'left',
                                            'padding': '10px'
                                            # 'margin': '5px'
                                        },
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                    ),
                                    html.Div(className='vertical-separator'),
                                    html.Div(id='output-data-upload'),

                                    # dcc.Textarea(
                                    #     id='user-input-code',
                                    #     style={'width':'100%', 'height':200}
                                    #     ),
                                    # html.Button('exec', id='button-exec'),
                                    # html.Div([], id='output-exec'),
                                    html.Div(className='vertical-separator'),
                                    html.Button('data summary', id='button-data-summary'),
                                    html.Div(className='vertical-separator'),
                                    html.Div([], id='missing-values')

                                     ], className='container')


                             ], id='tab-input'
                         ),

                 dcc.Tab(label='Numerical Variables', children=[
                     html.Div([
                         html.Div(className='vertical-separator'),
                         dcc.Dropdown(id='dropdown-num-vars',
                                      options=[],
                                      multi=True),
                         dcc.RadioItems(
                             options=[
                                 {'label':'Output code for plots', 'value':'yes'},
                                 {'label':'Do not output', 'value':'no'}
                                 ],
                             value='no',
                             labelStyle={'display': 'inline-block'},
                             id='radio-plot-code'),
                         html.Div(className='vertical-separator'),
                         html.Button('plot distribution', id='button-make-histogram'),
                         html.Div(className='vertical-separator'),
                         html.Div(id='graph-hist-num-vars')

                         ], className='container')
                     ], id='tab-numerical')
                 ]

        ),

])

# def missing_values(df):

#     vars_na = df.columns.tolist()
#     # determine the percentage of missing values for each variable
#     df_miss_val = round(df[vars_na].isnull().mean()*100, 1)
#     list_miss_val = df_miss_val.tolist()
#     df_miss_val = pd.DataFrame({'variable':vars_na,
#                                 '% missing values': list_miss_val})

#     return df_miss_val

# def var_types(df):

#     df_types = df.dtypes

#     list_types = [str(df_types[i]) for i in range(len(df_types))]

#     # df_miss_val = df_miss_val.to_frame()
#     # df_miss_val.reset_index()
#     # df_miss_val.columns = ['variable', '% missign values']

def code_for_hist(var):
    '''

    test = code_for_hist('ziop')
    '''

    hist_code = f"""
    df[{var}].hist(bins=30)
    plt.ylabel('Count')
    plt.xlabel({var})
    plt.title({var})
    """

    return hist_code

def summary_table(df):
    '''
    DESCRIPTIOIN:
        Creates a summary table from the input dataframe. The summary includes per each variable:
            - data type
            - % missing values
    '''

    # DATA TYPES

    df_types = df.dtypes                                                # evaluate data type
    list_types = [str(df_types[i]) for i in range(len(df_types))]       # put them in a list where each type is converted to a string

    # MISSING VALUES

    vars_na = df.columns.tolist()
    # determine the percentage of missing values for each variable
    df_miss_val = round(df[vars_na].isnull().mean()*100, 1)             # express as a %
    list_miss_val = df_miss_val.tolist()                                # convert it to a list that becomes the column of the output dataframe

    df_summary = pd.DataFrame({'variable name':vars_na,
                                'type':list_types,
                                '% missing values': list_miss_val})

    return df_summary

def parse_contents(contents):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    data_json = df.to_json(orient='records')
    # return df

    table = html.Div([
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],

                style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                style_cell={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                }

            ),
            html.Hr(),  # horizontal line
            ])

    return table, data_json


@app.callback([Output('output-data-upload', 'children'),
              Output('memory-output','data')],
              [Input('upload-data', 'contents')])
def update_output(contents):
    if contents is not None:
        children, data_json = parse_contents(contents[0]) # takes only the first argument of the string, otherwise parse does not work
        return children, data_json

@app.callback(Output('missing-values', 'children'),
              [Input('button-data-summary','n_clicks')],
              [State('memory-output','data')])
def create_summary_table(n_clicks, data_json):

    df_from_json = pd.read_json(data_json, orient='records')

    # Calculate missing values for each variable (if any)
    # df_miss_val = missing_values(df_from_json)
    df_summary = summary_table(df_from_json)
    #data_out = df_from_json.loc[1,:].to_json(orient='records')
    table = html.Div([dash_table.DataTable(
                id='copied-table',
                columns=[{'name': i, 'id': i} for i in df_summary.columns],
                data = df_summary.to_dict('records'),

                style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                style_cell={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                }

                )])
    return table


@app.callback(Output('dropdown-num-vars','options'),
              [Input('memory-output','data')])
def update_dropdown_num_var(data_json):
    '''
    DESCRIPTION:
        Create a dictionary of options for the dropdown menu of the numerical variables tab, named 'dropdown-num-vars'.
        This dropdown menu will be used to select the (numerical) variables for which to plot the distribution.
    '''

    df_from_json = pd.read_json(data_json, orient='records')        # read stored json data and create dataframe

    num_vars = [var for var in df_from_json.columns if df_from_json[var].dtypes == 'int64']

    options = [{'label':i, 'value':i} for i in num_vars]

    options.insert(0, {'label':'Select All', 'value':'Select All'})

    # options.append({'label':'Select All', 'value':'Select All'})

    return options


@app.callback(Output('graph-hist-num-vars','children'),
              [Input('button-make-histogram', 'n_clicks')],
              [State('memory-output','data'),
               State('dropdown-num-vars','value'),
               State('radio-plot-code','value')])
def make_hist_num_var(n_clicks, data_json, selected_vars, code_for_plots):
    '''
    DESCRIPTION:
        Make a series of histograms for the selected (numerical) variables from the dropdown menu id='dropdown-num-vars'.
        The plots are rendered in the tab named 'Numerical Variables'.

    INPUT:
        - n_clicks:                         ->  click of the button id='button-make-histogram'
        - data_json: (json)                 ->  uploaded dataframe stored in json format in 'memory-output'
        - selected_vars: (list of strings)  ->  list of (numerical) variables to be plotted (histograms)
        - code_for_plots: (list of string)  ->  list of one string that can contain the value 'yes' if the checkbox for the output histogram code was selected

    OUTPUT:
        - container_hist: (htlm division)   ->  list of histograms (distribution) stored in a division

    '''

    df_from_json = pd.read_json(data_json, orient='records')    # read stored json data and create dataframe

    list_hist = []

    if 'Select All' in selected_vars:

        selected_vars = [var for var in df_from_json.columns if df_from_json[var].dtypes == 'int64']

    for var in selected_vars:                                   # loop through the selected variables to make a histogram for each of them

        fig = go.Figure(data=[go.Histogram(x=df_from_json[var])])
        fig.update_traces(opacity=0.5)

        fig.update_layout(
            title_text = var,            # title of the plot
            xaxis_title_text = 'Value',  # xaxis label
            yaxis_title_text = 'Count',  # yaxis label
            bargap = 0.05                # gap between bars of adjacent location coordinates
            )

        if code_for_plots=='yes':
            div_code_for_hist = html.Div([
                                dcc.Textarea(
                                    value=code_for_hist(var),
                                    style={'height':200,
                                           'width': 300}
                                    )
                                    ], style={'float':'left'})

            hist = html.Div([
                html.Div([
                    dcc.Graph(figure=fig)
                    ], style={'width':600,
                              'float':'left'}),
                div_code_for_hist
                ], style={'width':'100%',
                          'overflow':'hidden'})

        else:
            hist = html.Div([dcc.Graph(figure=fig),
                             html.Div(className='vertical-separator')])

        list_hist.append(hist)

    container_hist = html.Div(list_hist)

    return container_hist