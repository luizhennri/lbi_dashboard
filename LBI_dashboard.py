# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import json
from urllib.request import urlopen
import plotly.express as px
from unidecode import unidecode

# Importação dos dados
df_lbi = pd.read_csv('./admin_HD_LBI.csv')
df_dados_mapa = pd.read_csv('./dados_mapa.csv')

# DataSets Auxiliares
recorte_temporal = ['2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']
REGIOES = ['Norte', 'Nordeste', 'Centro-Oeste','Sudeste', 'Sul']
ESTADOS = [
    "Acre",
    "Alagoas",
    "Amapa",
    "Amazonas",
    "Bahia",
    "Ceará",
    "Distrito Federal",
    "Espirito Santo",
    "Goias",
    "Maranhão",
    "Mato Grosso",
    "Mato Grosso do Sul",
    "Minas Gerais",
    "Para",
    "Paraíba",
    "Parana",
    "Pernambuco",
    "Piaui",
    "Rio de Janeiro",
    "Rio Grande do Norte",
    "Rio Grande do Sul",
    "Rondonia",
    "Roraima",
    "Santa Catarina",
    "São Paulo",
    "Sergipe",
    "Tocantins"
]

with urlopen("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson") as response: Brazil = json.load(response)

state_id_map = {}      


external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap',
]

for feature in Brazil['features']: 
    feature['id'] = unidecode(feature['properties']['name'])
    state_id_map[feature['properties']['sigla']] = feature['id']

BRAZIL_GEOJSON = Brazil.copy()

# Inicialização do Aplicativo
app = Dash(__name__, external_stylesheets=external_stylesheets, assets_external_path = './assets', title = 'LBI Dashboard', update_title='Atualizando ...', suppress_callback_exceptions=True)

app.css.config.serve_locally = True


# Métricas
df_lbi_filter = df_lbi[df_lbi['numero'].str.split('.').str[1].isin([str(ano) for ano in range(2011, 2022)])]

# Mapa - Visão Geral
df_dados_mapa_merge = df_dados_mapa.copy()
df_dados_mapa_merge['Estado'] = df_dados_mapa['Estado'].apply(unidecode)

df_lbi_merge = df_lbi_filter['ESTADOS'].value_counts().to_frame()
df_lbi_merge.index.names = ['Estado']

df_dados_mapa_final = pd.merge(df_dados_mapa_merge, df_lbi_merge, how = 'inner', on = 'Estado')

fig = px.choropleth_mapbox(
    df_dados_mapa_final,
    locations = 'Estado',
    geojson = BRAZIL_GEOJSON,
    color = 'count', 
    hover_name = 'Estado',
    hover_data = ['count','Longitude','Latitude'],
    title = "Quantidade de Processos por Estado",
    mapbox_style= 'white-bg',
    center = {"lat":-14, "lon": -55},
    zoom = 2,
    color_continuous_scale= 'Teal'
)

#fig.update_layout(
#    title_text='Map Text',
#    geo = dict(
#        scope='usa',
#        projection=go.layout.geo.Projection(type = 'albers usa'),
#        showlakes=True, # lakes
#        lakecolor='rgb(255, 255, 255)'),
#)

# Estilo da Aplicação
app.layout = html.Div([
        html.Div(
            dcc.Tabs(id="tabs-LBI", value='tab-visao_geral', children=[
                dcc.Tab(label='Visão Geral', value='tab-visao_geral'),
                dcc.Tab(label='Duração', value='tab-duracao'),
                dcc.Tab(label='Demandas', value='tab-demandas')
        ]), style={'float': 'bottom'}),
        html.Div(id='tabs-content', style={'foat': 'top'})
    ], style={'margin-top': '15px'})

@callback(
Output('tabs-content', 'children'),
Input('tabs-LBI', 'value'))
def render_content(tab):
    if tab == 'tab-visao_geral':
        return html.Div([


            html.Div([

                #FILTROS
                html.Div([
                            html.Div([
                                html.Label("FILTRAR POR ESTADO"),
                                dcc.Dropdown(
                                    ESTADOS,
                                    multi = True,
                                    clearable = True,
                                    id = "filter-state"
                                ),], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%', 'margin-right': '20px',}),

                            html.Div([
                                html.Label("FILTRAR POR REGIÃO"),
                                dcc.Dropdown(
                                    REGIOES,
                                    multi = True,
                                    clearable = True,
                                    id = "filter-region"
                                ),], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}),

                ], style={ 'display': 'flex',
                          'flex-direction': 'row',
                          
                }),
                #TOTAL
                html.Div([

                        html.H2(children='Total de Processos',
                        style={
                            'textAlign': 'center',
                            'color': '#252423',
                            'font-weight':'bold',
                            'font-size': '24px'},
                        id = 'total_cases'
                        ),      

                
                ], style={
                }),

                #MAPA
                html.Div([
                            
                html.Div(
                    dcc.Graph(figure = fig)
                )
                
                ], style={
                }),
                            

        
        ], style={
                                'background-color': '#fff',
                                'border-radius': '15px',
                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                                'padding': '10px',
        }),

                html.Div([
                            # Direito civil
                            html.Div([
                                html.H6(children='Área do Direito Mais presente',
                                    style={
                                        'textAlign': 'center',
                                        'color': '#252423',
                                        'margin-bottom': '3px',
                                        'font-weight': '400',
                                        'font-size': '14px',
                                        }
                                    ),
                            html.P(f"{df_lbi_filter['area_direito'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 40,
                                'margin': '0px',
                                },
                                id = 'total_area_direito'
                            ),
                            html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 12,
                                'margin-top': '5px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )
                            ], style={
                                'background-color': '#fff',
                                'border-radius': '15px',
                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                            }),


                            # Familia
                            html.Div([
                                html.H6(children='Maior Matéria Principal',
                                    style={
                                        'textAlign': 'center',
                                        'color': '#252423',
                                        'margin-bottom': '3px',
                                        'font-weight': '400',
                                        'font-size': '14px',
                                        }
                                    ),
                            html.P(f"{df_lbi_filter['materia_principal'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 40,
                                'margin': '0px',
                                },
                                id = 'total_materia_principal'
                            ),
                            html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 12,
                                'margin-top': '5px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )
                            ], style={
                                'background-color': '#fff',
                                'border-radius': '15px',
                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                            }),


                            # Processo civil e do trabalho
                            html.Div([
                                html.H6(children='Natureza do processo Mais presente',
                                    style={
                                        'textAlign': 'center',
                                        'color': '#252423',
                                        'margin-bottom': '3px',
                                        'font-weight': '400',
                                        'font-size': '14px',
                                        }
                                    ),
                            html.P(f"{df_lbi_filter['natureza_processo'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 40,
                                'margin': '0px',
                                },
                                id = 'total_natureza_processo'
                            ),
                            html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 12,
                                'margin-top': '5px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )
                            ], style={
                                'background-color': '#fff',
                                'border-radius': '15px',
                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                            }),

                            # Cível
                            html.Div([
                                html.H6(children='Natureza da Vara mais Presente',
                                    style={
                                        'textAlign': 'center',
                                        'color': '#252423',
                                        'margin-bottom': '3px',
                                        'font-weight': '400',
                                        'font-size': '14px',
                                        }
                                    ),
                            html.P(f"{df_lbi_filter['natureza_vara'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 40,
                                'margin': '0px',
                                },
                                id = 'total_natureza_vara'
                            ),
                            html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 12,
                                'margin-top': '5px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )
                            ], style={
                                'background-color': '#fff',
                                'border-radius': '15px',
                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                            }),

                            # Procedimento de conhecimento
                            html.Div([
                                html.H6(children='Procedimento Mais Presente',
                                    style={
                                        'textAlign': 'center',
                                        'color': '#252423',
                                        'margin-bottom': '3px',
                                        'font-weight': '400',
                                        'font-size': '14px',
                                        }
                                    ),
                            html.P(f"{df_lbi_filter['procedimento'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 40,
                                'margin': '0px',
                                },
                                id = 'total_procedimento'
                            ),
                            html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 12,
                                'margin-top': '5px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )
                            ], style={
                                'background-color': '#fff',
                                'border-radius': '15px',
                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                            }),


                            # Processo de conhecimento
                            html.Div([
                                html.H6(children='Tipo de Processo Mais Presente',
                                    style={
                                        'textAlign': 'center',
                                        'color': '#252423',
                                        'margin-bottom': '3px',
                                        'font-weight': '400',
                                        'font-size': '14px',
                                        }
                                    ),
                            html.P(f"{df_lbi_filter['tipo_processo'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 40,
                                'margin': '0px',
                                },
                                id = 'total_tipo_processo'
                            ),
                            html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 12,
                                'margin-top': '5px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )
                            ], style={
                                'background-color': '#fff',
                                'border-radius': '15px',
                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                            }),



            
                    

        
        ], style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-template-rows': '1fr 1fr 1fr',
            'gap': '10px',
        }),
                    

        
        ], style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'gap': '10px',
            'padding': '10px',
            'font-family': 'Roboto, Open Sans, verdana, arial, sans-serif',
        })

    elif tab == 'tab-duracao':
        return html.Div(
                    dcc.Graph(figure = fig)
                )
    elif tab == 'tab-demandas':
        return None

# CallBacks
@callback(
    Output('total_cases', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_state(value_state, value_region):

    total_cases = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao.upper())]

                total_cases += df_lbi_2['_id'].nunique()

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]

                total_cases += df_lbi_2['_id'].nunique()
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao.upper()))]

                    total_cases += df_lbi_2['_id'].nunique()

        return f'{(total_cases):,}'
    else:
        return f"{df_lbi_filter['_id'].nunique():,}"
    
@callback(
    Output('total_area_direito', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_state(value_state, value_region):

    total_cases = 0
    total_cases_type = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao.upper())]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['area_direito'].value_counts()[0]

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['area_direito'].value_counts()[0]
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao.upper()))]

                    total_cases += df_lbi_2['_id'].nunique()

                    if not df_lbi_2.empty:
                        total_cases_type += df_lbi_2['area_direito'].value_counts()[0]   
        if total_cases == 0 or total_cases_type == 0:
            return ' 0 %'
        else:
            return f'{(total_cases_type/total_cases)*100:.2f}'.format().replace('.',',') + ' %'
    else:
        return f"{(df_lbi_filter['area_direito'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %'

@callback(
    Output('total_materia_principal', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_state(value_state, value_region):

    total_cases = 0
    total_cases_type = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao.upper())]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['materia_principal'].value_counts()[0]

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['materia_principal'].value_counts()[0]
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao.upper()))]

                    total_cases += df_lbi_2['_id'].nunique()

                    if not df_lbi_2.empty:
                        total_cases_type += df_lbi_2['materia_principal'].value_counts()[0]   
        if total_cases == 0 or total_cases_type == 0:
            return ' 0 %'
        else:
            return f'{(total_cases_type/total_cases)*100:.2f}'.format().replace('.',',') + ' %'
    else:
        return f"{(df_lbi_filter['materia_principal'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %'

@callback(
    Output('total_natureza_processo', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_state(value_state, value_region):

    total_cases = 0
    total_cases_type = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao.upper())]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['natureza_processo'].value_counts()[0]

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['natureza_processo'].value_counts()[0]
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao.upper()))]

                    total_cases += df_lbi_2['_id'].nunique()

                    if not df_lbi_2.empty:
                        total_cases_type += df_lbi_2['natureza_processo'].value_counts()[0]   
        if total_cases == 0 or total_cases_type == 0:
            return ' 0 %'
        else:
            return f'{(total_cases_type/total_cases)*100:.2f}'.format().replace('.',',') + ' %'
    else:
        return f"{(df_lbi_filter['natureza_processo'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %'

@callback(
    Output('total_natureza_vara', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_state(value_state, value_region):

    total_cases = 0
    total_cases_type = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao.upper())]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['natureza_vara'].value_counts()[0]

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['natureza_vara'].value_counts()[0]
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao.upper()))]

                    total_cases += df_lbi_2['_id'].nunique()

                    if not df_lbi_2.empty:
                        total_cases_type += df_lbi_2['natureza_vara'].value_counts()[0]   
        if total_cases == 0 or total_cases_type == 0:
            return ' 0 %'
        else:
            return f'{(total_cases_type/total_cases)*100:.2f}'.format().replace('.',',') + ' %'
    else:
        return f"{(df_lbi_filter['natureza_vara'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %'

@callback(
    Output('total_procedimento', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_state(value_state, value_region):

    total_cases = 0
    total_cases_type = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao.upper())]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['procedimento'].value_counts()[0]

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['procedimento'].value_counts()[0]
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao.upper()))]

                    total_cases += df_lbi_2['_id'].nunique()

                    if not df_lbi_2.empty:
                        total_cases_type += df_lbi_2['procedimento'].value_counts()[0]   
        if total_cases == 0 or total_cases_type == 0:
            return ' 0 %'
        else:
            return f'{(total_cases_type/total_cases)*100:.2f}'.format().replace('.',',') + ' %'
    else:
        return f"{(df_lbi_filter['procedimento'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %'

@callback(
    Output('total_tipo_processo', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_state(value_state, value_region):

    total_cases = 0
    total_cases_type = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao.upper())]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['tipo_processo'].value_counts()[0]

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]

                total_cases += df_lbi_2['_id'].nunique()
                total_cases_type += df_lbi_2['tipo_processo'].value_counts()[0]
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao.upper()))]

                    total_cases += df_lbi_2['_id'].nunique()

                    if not df_lbi_2.empty:
                        total_cases_type += df_lbi_2['tipo_processo'].value_counts()[0]   
        if total_cases == 0 or total_cases_type == 0:
            return ' 0 %'
        else:
            return f'{(total_cases_type/total_cases)*100:.2f}'.format().replace('.',',') + ' %'
    else:
        return f"{(df_lbi_filter['tipo_processo'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %'

# Run the app
if __name__ == '__main__':
    app.run(debug = True, port="8050")