import zipp
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import zipfile

AccessToken = 'pk.eyJ1IjoiYXNhZGJhZ2hlcmkiLCJhIjoiY2wzdjlheHJpMGdibDNkbjhhbTJpMTNmeSJ9.HTWj5RrPUtJY-WfVvFrdLw'
px.set_mapbox_access_token(AccessToken)

def get_csv_files():
    zf = zipfile.ZipFile('df29AH.zip', mode='r')
    df29Ahour = pd.read_csv(zf.open('df29Ahourly.csv'), encoding='iso8859_10', low_memory=False)
    df29Ahour['date'] = pd.to_datetime(df29Ahour['date'])
    df29Adavg = pd.read_csv('df29davg.csv', low_memory=False, encoding='iso8859_10')
    df29Amavg = pd.read_csv('df29mavg.csv', low_memory=False, encoding='iso8859_10')
    df29Amsum = pd.read_csv('df29msum.csv', low_memory=False, encoding='iso8859_10')
    df29Amsumagg = pd.read_csv('df29msumagg.csv', low_memory=False, encoding='iso8859_10')
    df29Amap = pd.read_csv('df29map.csv', low_memory=False, encoding='iso8859_10')
    dfb = pd.read_csv('df29base.csv', low_memory=False, encoding='iso8859_10')
    return [dfb, df29Ahour, df29Adavg, df29Amavg, df29Amsum, df29Amsumagg, df29Amap]

app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.server
colors = {'background': '#A9A9A9', 'text': '#7FDBFF'}

[dfbase, df29h, df29davg, df29mavg, df29msum, df29msumagg, df29map] = get_csv_files()
app.layout = html.Div(

    style={'backgroundColor': colors['background']},
    children=[
        # html.H1(children="Strøm monitoring for veiobjekter, 2021",
        #         style={"fontSize": "48px", "color": "blue",'textAlign': 'center'}),
        html.Div(
            className="row",
            children=[
                html.Div([
                    dcc.Graph(figure=px.pie(dfbase,
                                            values=list(dfbase['Antall']),
                                            names=list(dfbase['ForbruksKoder']),
                                            hole=0.3,
                                            title='Målepunkter fordelt per forbrukskode',
                                            hover_name=list(dfbase['ForbruksBeskrivelse']))),
                ],
                    style={'width': '30%', 'display': 'inline-block', 'height' : '5%'},
                ),
                html.Div([
                    dcc.Graph(figure=go.Figure(go.Indicator(value=len(df29h.StasjonsNavn.unique()),
                                                            delta={'reference': 187},
                                                            gauge={'axis': {'visible': False}},
                                                            title={'text': "Aktiv veiobjekter(målepunkter)"},
                                                            mode="number+gauge"))),
                ],
                    style={'width': '30%', 'display': 'inline-block', 'hieght': '5%'},
                ),

                html.Div([
                    dcc.Graph(figure=px.bar(df29msumagg, x=df29msumagg.date, y=df29msumagg['ForbruksVerdi'].div(1000),
                                            title='Samlet månedlig forbruk for veiobjekter',
                                            labels={
                                                'date': 'Date (måned)',
                                                'y': 'Forbruksverdi (MWh)'
                                            },
                                            ),
                              ),
                ],
                    style={'width': '38%', 'display': 'inline-block', 'height' : '5%'},
                ),
            ]
        ),
        html.Br(),


        html.Div(className='row', style=dict(display='flex'), children=[
            # html.H1(children="Velg strekning og ønsket oppløsning:",
            #         style={"fontSize": "24px", "color": "blue",'textAlign': 'center'}),
            html.Div(className="four columns", children=[
                html.Label(['Velg strekning:'], style={'font-weight': 'bold', "color": "blue","text-align": "center"}),
                dcc.Dropdown(
                    id="strekning-filter",
                    options=[
                        {"label": strekning, "value": strekning}
                        for strekning in list(df29davg['StrekningsProsjekt'].unique())
                    ],
                    value='E18 Tvedestrand-Bamble',
                    placeholder = 'Velg strekning',
                    searchable=False,
                    clearable=False,
                ),
            ]
                     ),

            html.Div(className="four columns", style=dict(display='flex'),children=[

                dcc.RadioItems(
                    ['Time', 'Dag', 'Måned'],
                    value='Dag',
                    id='xaxis-resolusjon-type',

                    labelStyle={'display': 'inline-block', 'marginTop': '5px'}
                )
            ],
                     ),


        ],
                 ),
        html.Br(),
        html.Div([
            dcc.Graph(id = 'Agg-StrekningForbruks' )
        ]
        ),

        html.Div(
            children=[
                html.Div(className='row', style=dict(display='flex'), children=[
                    html.Div(className="six columns", children=[
                        dcc.Graph(
                            id='map-plot',
                            hoverData={'points': [{'customdata': 'Målepunkt'}]}
                        )
                    ]),
                    html.Div(className="six columns", children=[
                        #dcc.Graph(id='Agg-StrekningForbruks'),
                        dcc.Graph(id='Forbruks-series'),
                        dcc.Graph(id='Temperatur-series'),
                    ]),
                ])
            ]
        ),

        html.Div(
            [
                dcc.Graph(figure=px.scatter(df29davg, x='date', y='ForbruksVerdi', color='StasjonsNavn',
                                            title='Daglig gjennomsnitt forbruk for alle veiobjekter',
                                            labels={'date': 'Date','ForbruksVerdi': 'Forbruksverdi (KWh)'},
                                            ),
                          ),
            ]
        ),

        html.Div(
            [
                dcc.Graph(figure=px.scatter(df29davg, x='date', y='Temperatur', color='StasjonsNavn',
                                            title='Daglig gjennomsnitt temperatur for alle veiobjekter',
                                            labels={'date': 'Date','Temperatur': 'Temperatur (°C)'},
                                            ),
                          ),
            ]
        )
    ])

@app.callback(
    Output('Agg-StrekningForbruks', 'figure'),
    Input('strekning-filter', 'value')
)
def update_agg_graph(strek):
    customdf = df29h[df29h['StrekningsProsjekt'] == strek]
    #print(customdf)
    Strekmsum = customdf.groupby(['StasjonsNavn']) \
        .resample('M', on='date').sum().reset_index(drop=False).fillna(0)
    Strekmsumagg = Strekmsum.groupby(['date'], as_index=False).agg({'ForbruksVerdi': 'sum'}).round(0)
    # print(Strekmsumagg)
    # print('we are befor fig call')
    fig = px.bar(Strekmsumagg, x=Strekmsumagg.date, y=Strekmsumagg['ForbruksVerdi'].div(1000),
                     title = 'Samlet månedlig forbruk for veiobjekter i strekning',
                     labels = {'x': 'Date (måned)', 'y': 'Forbruksverdi (MWh)'},
                     )

    # print(fig)
    return fig

@app.callback(
    Output('map-plot', 'figure'),
    Input('strekning-filter', 'value')
)
def update_graph(strekning):
    customdf = df29h[df29h['StrekningsProsjekt'] == strekning]
    Zoom = 10

    fig = px.scatter_mapbox(df29map, lat= 'Lat', lon= 'Lon', width=800, height=900,
                            hover_data=["Name", "Lat", "Lon"],
                            center={"lat": np.mean(customdf['Lat']), "lon": np.mean(customdf['Lon'])},
                            hover_name='Name', title='Målepunkter veiobjekter 2021', zoom=Zoom)
    fig.update_layout(hovermode='closest',
                      mapbox_style="dark", mapbox_accesstoken=AccessToken)

    return fig
#
@app.callback(
    Output('Forbruks-series', 'figure'),
    Input('map-plot', 'hoverData'),
    Input('xaxis-resolusjon-type', 'value'))
def update_Forbruks_timeseries(hoverData, axis_type):
    stName = hoverData['points'][0]['customdata']
    Stasjon = stName[0]
    dfF = pd.DataFrame()
    if axis_type == 'Time':
        dfF = df29h
    if axis_type == 'Dag':
        dfF = df29davg
    if axis_type == 'Måned':
        dfF = df29mavg

    dfFPlot = dfF.query("StasjonsNavn == @Stasjon").reset_index(drop=True)
    title = '<b>{}</b> forbruk, <br>{} gjennomsnitt'.format(Stasjon, axis_type)
    if axis_type == 'Time':
        fig = px.scatter(dfFPlot, x='date', y='ForbruksVerdi',
                         title=title, labels={'date': 'Date', 'y': 'Forbruksverdi (KWh)'})
        fig.update_traces(mode='lines+markers')
    else:
        fig = px.bar(dfFPlot, x='date', y='ForbruksVerdi',
                     title=title, labels={'date': 'Date', 'y': 'Forbruksverdi (KWh)'})

    fig.update_xaxes(showgrid=False)
    return fig

@app.callback(
    Output('Temperatur-series', 'figure'),
    Input('map-plot', 'hoverData'),
    Input('xaxis-resolusjon-type', 'value'))
def update_Temperatur_timeseries(hoverData, axis_type):
    stName = hoverData['points'][0]['customdata']
    Stasjon = stName[0]
    dfT = pd.DataFrame()
    if axis_type == 'Time':
        dfT = df29h
    if axis_type == 'Dag':
        dfT = df29davg
    if axis_type == 'Måned':
        dfT = df29mavg
    dfTPlot = dfT.query("StasjonsNavn == @Stasjon").reset_index(drop=True)
    title = '<b>{}</b> temp., <br>{} gjennomsnitt'.format(Stasjon, axis_type)
    Tlist = dfTPlot['Temperatur'].tolist()
    is_all_zero = set(Tlist) == {0}
    fig = px.scatter(dfTPlot, x='date', y='Temperatur',
                     title=title, labels={'date': 'Date', 'y': 'Temperatur (°C)'})
    if is_all_zero:
        fig.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[
                {
                    "text": "No data found",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
        return fig

    else:
        if axis_type == 'Timelig':
            fig.update_traces(mode='lines+markers')
            fig.update_xaxes(showgrid=False)
            return fig
        else:
            fig = px.bar(dfTPlot, x='date', y='Temperatur', title=title)
            fig.update_xaxes(showgrid=False)
            return fig


if __name__ == '__main__':
    app.run_server(debug=True)
