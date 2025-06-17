# Importação das Bibliotecas
from dash import Dash, html, dcc, Output, Input
import plotly.express as px
from flask_caching import Cache
from const import *
from data import *

# Importação dos Dados
df_lbi = DF_DATA
df_dados_mapa = DF_MAPA
dados_censo = DF_CENSO


# Inicialização do Aplicativo
app = Dash(__name__, external_stylesheets = EXTERNAL_STYLESHEETS, assets_external_path = './assets', title = 'LBI Dashboard', update_title='Atualizando ...', suppress_callback_exceptions=True)

app.css.config.serve_locally = True

# Cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': './temp'
})

app.config.suppress_callback_exceptions = True


# Filtros - Escopo Temporal
df_lbi_filter = df_lbi[df_lbi['numero'].str.split('.').str[1].isin([str(ano) for ano in RECORTE_TEMPORAL])]


# Estilo da Aplicação
app.layout = html.Div([
        html.Div(
            dcc.Tabs(id="tabs-LBI", value='tab-inicial', children=[
                dcc.Tab(label='Início', value='tab-inicial'),
                dcc.Tab(label='Visão Geral', value='tab-visao_geral'),
                dcc.Tab(label='Duração', value='tab-duracao'),
                dcc.Tab(label='Demandas', value='tab-demandas')
        ]), style={'font-weight':'bold',
                   'font-family':'Raleway, sans-serif'}),
        html.Div(id='tabs-content')
    ], style={'margin-top': '10px'})


# ------------------- CallBacks -------------------

# ==== Abas ====
@app.callback(
Output('tabs-content', 'children'),
Input('tabs-LBI', 'value'))
@cache.memoize(timeout=TIMEOUT)
def render_content(tab):
    if tab == 'tab-inicial':
        return html.Div([
                        html.Div([
                            html.Img(src='./assets/img/logo_usp.png', style={'height': 'auto', 'max-width': '20%', 'padding': '15px'}),
                            html.Img(src='./assets/img/logo_fearp.png', style={'height': 'auto', 'max-width': '20%', 'padding': '15px'}),
                            html.Img(src='./assets/img/logo_habeas_data.png', style={'height': 'auto', 'max-width': '40%', 'padding': '15px'})
                        ], style={
                            'display': 'flex',
                            'flex-direction': 'row',
                            'flex-wrap': 'wrap',
                            'height': '100%',
                            'width': '100%',
                            'justify-content': 'space-around',
                            'align-items': 'center',
                        }),
                        html.H4(children='PAINEL PARA VISUALIZAÇÃO DE DADOS PROCESSUAIS DA LEI BRASILEIRA DE INCLUSÃO',
                        style={
                            'textAlign': 'center',
                            'color': '#252423',
                            'margin-bottom': '10px',
                            'font-weight':'bold',
                            'font-size':'28px'}
                        ),
                        
                        html.P(['Discente: Luiz Henrique Alves do Nascimento', html.Br(),'Orientador: Prof. Dr. Ildeberto A. Rodello'],
                            style={
                                'textAlign': 'right',
                                'color': '#252423',
                                'font-weight':'normal',
                                'font-size': '22px',
                                'margin-bottom':'10px',
                                'padding':'5px'}
                            ),

                        html.Label(children = 'Este painel é resultado do projeto "Projeto e Implementação de Um Painel para Análise de Dados de uma Base de Decisões Judiciais", financiado pelo Programa Unificado de Bolsas (PUB) da Universidade de São Paulo. O trabalho foi desenvolvido na Faculdade de Economia, Administração e Contabilidade de Ribeirão Preto (FEA-RP), no grupo de pesquisas Habeas Data. O dataset utilizado abrange dados processuais relacionados à Lei Brasileira de Inclusão (LBI), Lei n. 13.146/2015, especificamente sobre "Tutela", "Curatela" e "Tomada de Decisão Apoiada". O recorte temporal inclui os cinco anos anteriores (2011-2016) e os cinco anos posteriores à vigência da lei (2016-2021).',
                            style={
                                'textAlign': 'justify',
                                'color': '#252423',
                                'font-weight':'normal',
                                'font-size': '22px',
                                'padding':'5px'}
                            )                
                ], style={
                    'display': 'grid',
                    'grid-template-columns': '1fr',
                    'grid-template-rows': '1fr 1fr 1fr 1fr',
                    'gap': '10px',
                    'background-color': '#fff',
                    'border-radius': '15px',
                    'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                    'margin-top':'10px',
                    'margin-bottom':'10px',
                    'font-family': 'Open Sans, sans-serif'
                }),
    elif tab == 'tab-visao_geral':
        return html.Div([

            html.Div([

                # FILTROS
                html.Div([
                            html.Div([
                                html.Label("FILTRAR POR ESTADO", style={'margin-bottom':'5px', 'font-size':'12px'}),
                                dcc.Dropdown(
                                    ESTADOS,
                                    multi = True,
                                    clearable = True,
                                    id = "filter-state"
                                ),], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%', 'margin-right': '20px'}),

                            html.Div([
                                html.Label("FILTRAR POR REGIÃO", style={'margin-bottom':'5px', 'font-size':'12px'}),
                                dcc.Dropdown(
                                    list(LOCALIZACAO.keys()),
                                    multi = True,
                                    clearable = True,
                                    id = "filter-region"
                                ),], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}),

                ], style={ 'display': 'flex',
                          'flex-direction': 'row',             
                }),

                # TOTAL
                html.Div([
                        html.H4(children='Total de Processos',
                        style={
                            'textAlign': 'center',
                            'color': '#252423',
                            'margin-bottom': '5px',
                            'font-weight':'normal',
                            'font-size':'13px'}
                        ),

                        html.Div(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'font-weight':'bold',
                                'font-size': '32px'},
                            id = 'total_cases'
                            ), 

                
                ], style={
                }),

                # MAPA
                html.Div([
                            
                html.Div(
                    dcc.Graph(id = 'choropleth-map-amount')
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
                                html.H6(children='Área do direito mais presente',
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
                                'fontSize': '15px',
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': '35px',
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

                            # Família
                            html.Div([
                                html.H6(children='Maior matéria principal',
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
                                'fontSize': '15px',
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': '35px',
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
                                html.H6(children='Natureza do processo mais presente',
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
                                'fontSize': '13px',
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': '35px',
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
                                html.H6(children='Natureza da vara mais presente',
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
                                'fontSize': '15px',
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': '35px',
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
                                html.H6(children='Procedimento mais presente',
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
                                'fontSize': '15px',
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': '35px',
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
                                html.H6(children='Tipo de processo mais presente',
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
                                'fontSize': '15px',
                                'font-weight':'bold',
                                'margin-top': '5px',
                                'margin-bottom': '15px',
                                }
                            ),
                            html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': '35px',
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
            'font-family': 'Open Sans, sans-serif',
        })

    elif tab == 'tab-duracao':
        return html.Div([

            html.Div([

                # FILTROS
                html.Div([
                            html.Div([
                                html.Label("FILTRAR POR ESTADO", style={'margin-bottom':'5px', 'font-size':'12px'}),
                                dcc.Dropdown(
                                    ESTADOS,
                                    multi = True,
                                    clearable = True,
                                    id = "filter-state"
                                ),], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%', 'margin-right': '20px'}),

                            html.Div([
                                html.Label("FILTRAR POR REGIÃO", style={'margin-bottom':'5px', 'font-size':'12px'}),
                                dcc.Dropdown(
                                    list(LOCALIZACAO.keys()),
                                    multi = True,
                                    clearable = True,
                                    id = "filter-region"
                                ),], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}),

                ], style={ 'display': 'flex',
                          'flex-direction': 'row',             
                }),

                # MÉDIA
                html.Div([
                        html.H4(children='Média de Tempo dos Processos',
                        style={
                            'textAlign': 'center',
                            'color': '#252423',
                            'margin-bottom': '5px',
                            'font-weight':'normal',
                            'font-size':'13px'}
                        ),

                        html.Div(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'font-weight':'bold',
                                'font-size': '32px'},
                            id = 'avg_process'
                        ),

                        html.P(' anos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 12,
                                'margin-top': '5px',
                                'margin-left': '62px',
                                'font-weight':'bold'}
                        )
                
                ], style={
                }),

                # MAPA
                html.Div([
                            
                    html.Div(
                        dcc.Graph(id = 'choropleth-map-duration')
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
                            html.Div(
                                dcc.Graph(id = 'scatter-duration')
                            , style={
                                'background-color': '#fff',
                                'border-radius': '15px',
                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                                'padding': '10px'
                            }),

                            html.Div([  
                                html.Div(
                                    dcc.Graph(id = 'bar-duration')
                                ),

                                html.Div([
                                    html.H4(children='Processos Sentenciados',
                                    style={
                                        'textAlign': 'center',
                                        'color': '#252423',
                                        'margin-bottom': '5px',
                                        'font-weight':'normal',
                                        'font-size':'13px'}
                                    ),

                                    html.Div(None,
                                        style={
                                            'textAlign': 'center',
                                            'color': '#252423',
                                            'font-weight':'bold',
                                            'font-size': '32px'},
                                        id = 'avg_process_sentenced'
                                        ),

                                        html.P('dos processos',
                                        style={
                                            'textAlign': 'center',
                                            'color': '#252423',
                                            'fontSize': 12,
                                            'margin-top': '5px',
                                            'margin-left': '62px',
                                            'font-weight':'bold'}
                                        )
                            
                                ], style={
                                })
                            ], style={
                                    'background-color': '#fff',
                                    'border-radius': '15px',
                                    'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'padding': '10px'
                                    
                                }
                            ),
        
                ], style={
                    'display': 'grid',
                    'grid-template-rows': '1fr 1fr',
                    'gap': '10px'
                }),

        
        ], style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'gap': '10px',
            'padding': '10px',
            'font-family': 'Open Sans, sans-serif',
        })
    
    elif tab == 'tab-demandas':
        return html.Div([

            html.Div([

                # FILTROS
                html.Div([
                            html.Div([
                                html.Label("FILTRAR POR ESTADO", style={'margin-bottom':'5px', 'font-size':'12px'}),
                                dcc.Dropdown(
                                    ESTADOS,
                                    multi = True,
                                    clearable = True,
                                    id = "filter-state"
                                ),], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%', 'margin-right': '20px'}),

                            html.Div([
                                html.Label("FILTRAR POR REGIÃO", style={'margin-bottom':'5px', 'font-size':'12px'}),
                                dcc.Dropdown(
                                    list(LOCALIZACAO.keys()),
                                    multi = True,
                                    clearable = True,
                                    id = "filter-region"
                                ),], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}),

                ], style={ 'display': 'flex',
                          'flex-direction': 'row',             
                }),

                # MÉDIA
                html.Div([
                        html.H4(children='Quantidade de Processos a cada 100 mil habitantes',
                        style={
                            'textAlign': 'center',
                            'color': '#252423',
                            'margin-bottom': '5px',
                            'font-weight':'normal',
                            'font-size':'12px'}
                        ),

                        html.Div(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'font-weight':'bold',
                                'font-size': '32px'},
                            id = 'process_mil'
                        )
                
                ], style={
                }),

                # MAPA
                html.Div([
                            
                html.Div(
                    dcc.Graph(id = 'choropleth-map-demand')
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
                            html.Div(
                                dcc.Graph(id = 'histogram-demand')
                            , style={
                                'background-color': '#fff',
                                'border-radius': '15px',
                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                                'padding': '10px'
                            }),

                            html.Div(
                                dcc.Graph(id = 'bar-demand')
                                ,style={
                                    'background-color': '#fff',
                                    'border-radius': '15px',
                                    'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'padding': '10px'
                            })
        
            ], style={
                'display': 'grid',
                'grid-template-columns': '1fr',
                'grid-template-rows': '1fr 1fr',
                'gap': '10px',
            }),

        
        ], style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'gap': '10px',
            'padding': '10px',
            'font-family': 'Open Sans, sans-serif',
        })

# ==== Mapas ====
# Visão Geral
@app.callback(
    Output('choropleth-map-amount', 'figure'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_map(value_state, value_region):

    df_map = pd.DataFrame()

    df_dados_mapa_merge = df_dados_mapa.copy()
    df_dados_mapa_merge['Estado'] = df_dados_mapa['Estado'].apply(unidecode)

    df_lbi_merge = df_lbi_filter['ESTADOS'].value_counts().to_frame()
    df_lbi_merge.index.names = ['Estado']

    df_dados_mapa_final = pd.merge(df_dados_mapa_merge, df_lbi_merge, how = 'inner', on = 'Estado')

    fig = px.choropleth_map(
        df_dados_mapa_final,
        locations = 'Estado',
        geojson = BRAZIL_GEOJSON,
        color = 'count', 
        hover_name = 'Estado',
        hover_data = ['count','Longitude','Latitude'],
        title = "Quantidade de Processos por Estado",
        map_style= 'white-bg',
        labels={'count': 'Processos'},
        center = {"lat":-14, "lon": -55},
        zoom = 2,
        color_continuous_scale= 'Teal'
    )

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                
                df_map = pd.concat([df_map, df_dados_mapa_final.loc[(df_dados_mapa_final['Região'] == regiao)]])

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_map = pd.concat([df_map, df_dados_mapa_final.loc[(df_dados_mapa_final['Estado'] == unidecode(estado))]])
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_map = pd.concat([df_map, df_dados_mapa_final.loc[((df_dados_mapa_final['Estado'] == unidecode(estado)) & (df_dados_mapa_final['Região'] == regiao))]])    

        if df_map.empty:
            fig = px.choropleth_map(
                df_map,
                geojson = BRAZIL_GEOJSON,
                title = "Quantidade de Processos por Estado",
                map_style= 'white-bg',
                center = {"lat":-14, "lon": -55},
                zoom = 2,
                color_continuous_scale= 'Teal',
                labels={'count': 'Processos'}
            )

            return fig

        fig = px.choropleth_map(
            df_map,
            locations = 'Estado',
            geojson = BRAZIL_GEOJSON,
            color = 'count', 
            hover_name = 'Estado',
            hover_data = ['count','Longitude','Latitude'],
            title = "Quantidade de Processos por Estado",
            map_style= 'white-bg',
            labels={'count': 'Processos'},
            center = {"lat":-14, "lon": -55},
            zoom = 2,
            color_continuous_scale= 'Teal'
        )   

        return fig
    else:
        return fig

# Duração
@app.callback(
    Output('choropleth-map-duration', 'figure'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_map(value_state, value_region):

    df_map = pd.DataFrame()

    df_dados_mapa_merge = df_dados_mapa.copy()
    df_dados_mapa_merge['Estado'] = df_dados_mapa['Estado'].apply(unidecode)

    df_lbi_merge = df_lbi_filter[['ESTADOS', 'Tempo de Processo em Anos']]
    #df_lbi_merge['Tempo de Processo em Anos'] = df_lbi_merge['Tempo de Processo em Anos'].str.replace(',', '.').astype(float)

    df_lbi_merge = df_lbi_merge.groupby(['ESTADOS']).mean(numeric_only = True)

    df_lbi_merge.index.names = ['Estado']

    df_dados_mapa_final = pd.merge(df_dados_mapa_merge, df_lbi_merge, how = 'inner', on = 'Estado')

    fig = px.choropleth_map(
        df_dados_mapa_final,
        locations = 'Estado',
        geojson = BRAZIL_GEOJSON,
        color = 'Tempo de Processo em Anos', 
        hover_name = 'Estado',
        hover_data = ['Tempo de Processo em Anos','Longitude','Latitude'],
        title = "Média de Tempo dos Processos por Estado",
        map_style= 'white-bg',
        labels={'Tempo de Processo em Anos': 'Anos'},
        center = {"lat":-14, "lon": -55},
        zoom = 2,
        color_continuous_scale= 'Teal'
    )

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                
                df_map = pd.concat([df_map, df_dados_mapa_final.loc[(df_dados_mapa_final['Região'] == regiao)]])

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_map = pd.concat([df_map, df_dados_mapa_final.loc[(df_dados_mapa_final['Estado'] == unidecode(estado))]])
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_map = pd.concat([df_map, df_dados_mapa_final.loc[((df_dados_mapa_final['Estado'] == unidecode(estado)) & (df_dados_mapa_final['Região'] == regiao))]])    

        if df_map.empty:
            fig = px.choropleth_map(
                df_map,
                geojson = BRAZIL_GEOJSON,
                title = "Média de Tempo dos Processos por Estado",
                map_style= 'white-bg',
                center = {"lat":-14, "lon": -55},
                zoom = 2,
                color_continuous_scale= 'Teal',
                labels={'Tempo de Processo em Anos': 'Anos'}
            )

            return fig

        fig = px.choropleth_map(
            df_map,
            locations = 'Estado',
            geojson = BRAZIL_GEOJSON,
            color = 'Tempo de Processo em Anos', 
            hover_name = 'Estado',
            hover_data = ['Tempo de Processo em Anos','Longitude','Latitude'],
            title = "Média de Tempo dos Processos por Estado",
            map_style= 'white-bg',
            labels={'Tempo de Processo em Anos': 'Anos'},
            center = {"lat":-14, "lon": -55},
            zoom = 2,
            color_continuous_scale= 'Teal'
        )   

        return fig
    else:
        return fig

# Demandas
@app.callback(
    Output('choropleth-map-demand', 'figure'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_map(value_state, value_region):

    df_map = pd.DataFrame()

    df_dados_mapa_merge = df_dados_mapa.copy()
    df_dados_mapa_merge['Estado'] = df_dados_mapa['Estado'].apply(unidecode)

    df_censo_merge = dados_censo[['ESTADO', 'UF', 'POPULAÇÃO / 100K']].copy()
    df_censo_merge.rename(columns={'ESTADO':'Estado'}, inplace = True)

    df_lbi_merge = df_lbi_filter['ESTADOS'].value_counts().to_frame()
    df_lbi_merge.index.names = ['Estado']

    df_censo_merge = pd.merge(df_censo_merge, df_lbi_merge, how = 'inner', on = 'Estado')
    df_censo_merge.rename(columns={'count':'Processos'}, inplace = True)

    df_dados_mapa_final = pd.merge(df_dados_mapa_merge, df_censo_merge, how = 'inner', on = 'Estado')

    df_dados_mapa_final['PROCESSOS / 100K'] = df_dados_mapa_final['Processos'] / df_dados_mapa_final['POPULAÇÃO / 100K']

    fig = px.choropleth_map(
        df_dados_mapa_final,
        locations = 'Estado',
        geojson = BRAZIL_GEOJSON,
        color = 'PROCESSOS / 100K', 
        hover_name = 'Estado',
        hover_data = ['PROCESSOS / 100K','Longitude','Latitude'],
        title = "Quantidade de Processos a cada 100 mil habitantes por Estado",
        map_style= 'white-bg',
        labels={'PROCESSOS / 100K': 'Processos por 100 mil'},
        center = {"lat":-14, "lon": -55},
        zoom = 2,
        color_continuous_scale= 'Teal'
    )

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                
                df_map = pd.concat([df_map, df_dados_mapa_final.loc[(df_dados_mapa_final['Região'] == regiao)]])

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_map = pd.concat([df_map, df_dados_mapa_final.loc[(df_dados_mapa_final['Estado'] == unidecode(estado))]])
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_map = pd.concat([df_map, df_dados_mapa_final.loc[((df_dados_mapa_final['Estado'] == unidecode(estado)) & (df_dados_mapa_final['Região'] == regiao))]])    

        if df_map.empty:
            fig = px.choropleth_map(
                df_map,
                geojson = BRAZIL_GEOJSON,
                title = "Quantidade de Processos a cada 100 mil habitantes por Estado",
                map_style= 'white-bg',
                center = {"lat":-14, "lon": -55},
                zoom = 2,
                color_continuous_scale= 'Teal',
                labels={'PROCESSOS / 100K': 'Processos por 100 mil'}
            )

            return fig

        fig = px.choropleth_map(
            df_map,
            locations = 'Estado',
            geojson = BRAZIL_GEOJSON,
            color = 'PROCESSOS / 100K', 
            hover_name = 'Estado',
            hover_data = ['PROCESSOS / 100K','Longitude','Latitude'],
            title = "Quantidade de Processos a cada 100 mil habitantes por Estado",
            map_style= 'white-bg',
            labels={'PROCESSOS / 100K': 'Processos por 100 mil'},
            center = {"lat":-14, "lon": -55},
            zoom = 2,
            color_continuous_scale= 'Teal'
        )   

        return fig
    else:
        return fig

# ==== Cards ====
# Visão Geral
@app.callback(
    Output('total_cases', 'children'),
    Output('total_area_direito', 'children'),
    Output('total_materia_principal', 'children'),
    Output('total_natureza_processo', 'children'),
    Output('total_natureza_vara', 'children'),
    Output('total_procedimento', 'children'),
    Output('total_tipo_processo', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
@cache.memoize(timeout=TIMEOUT)
def update_cards_visao(value_state, value_region):

    total_cases = 0
    total_direito = 0
    total_materia = 0
    total_natureza_processo = 0
    total_natureza_vara = 0
    total_procedimento = 0
    total_tipo = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao)]

                total_cases += df_lbi_2['_id'].nunique()
                total_direito += df_lbi_2['area_direito'].value_counts()[0]
                total_materia += df_lbi_2['materia_principal'].value_counts()[0]
                total_natureza_processo += df_lbi_2['natureza_processo'].value_counts()[0]
                total_natureza_vara += df_lbi_2['natureza_vara'].value_counts()[0]
                total_procedimento += df_lbi_2['procedimento'].value_counts()[0]
                total_tipo += df_lbi_2['tipo_processo'].value_counts()[0]

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]

                total_cases += df_lbi_2['_id'].nunique()
                total_direito += df_lbi_2['area_direito'].value_counts()[0]
                total_materia += df_lbi_2['materia_principal'].value_counts()[0]
                total_natureza_processo += df_lbi_2['natureza_processo'].value_counts()[0]
                total_natureza_vara += df_lbi_2['natureza_vara'].value_counts()[0]
                total_procedimento += df_lbi_2['procedimento'].value_counts()[0]
                total_tipo += df_lbi_2['tipo_processo'].value_counts()[0]
        else:
            for regiao in value_region:
                for estado in value_state:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao))]

                    total_cases += df_lbi_2['_id'].nunique()

                    if not df_lbi_2.empty:
                        total_direito += df_lbi_2['area_direito'].value_counts()[0]
                        total_materia += df_lbi_2['materia_principal'].value_counts()[0]
                        total_natureza_processo += df_lbi_2['natureza_processo'].value_counts()[0]
                        total_natureza_vara += df_lbi_2['natureza_vara'].value_counts()[0]
                        total_procedimento += df_lbi_2['procedimento'].value_counts()[0]
                        total_tipo += df_lbi_2['tipo_processo'].value_counts()[0]
        
        if total_cases == 0:
            return '0', ' 0 %', ' 0 %', ' 0 %', ' 0 %', ' 0 %', ' 0 %'
        else:

            return f"{(total_cases):,}".format().replace(',','.'), f'{(total_direito/total_cases)*100:.2f}'.format().replace('.',',') + ' %', f'{(total_materia/total_cases)*100:.2f}'.format().replace('.',',') + ' %', f'{(total_natureza_processo/total_cases)*100:.2f}'.format().replace('.',',') + ' %', f'{(total_natureza_vara/total_cases)*100:.2f}'.format().replace('.',',') + ' %', f'{(total_procedimento/total_cases)*100:.2f}'.format().replace('.',',') + ' %', f'{(total_tipo/total_cases)*100:.2f}'.format().replace('.',',') + ' %'
    else:
        return f"{df_lbi_filter['_id'].nunique():,}".format().replace(',','.'), f"{(df_lbi_filter['area_direito'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %', f"{(df_lbi_filter['materia_principal'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %', f"{(df_lbi_filter['natureza_processo'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %', f"{(df_lbi_filter['natureza_vara'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %', f"{(df_lbi_filter['procedimento'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %', f"{(df_lbi_filter['tipo_processo'].value_counts()[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %'

# Duração
@app.callback(
    Output('avg_process', 'children'),
    Output('avg_process_sentenced', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
@cache.memoize(timeout=TIMEOUT)
def update_cards_duration(value_state, value_region):

    avg_process = 0
    total_cases = 0
    total_sentenced = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao)]

                avg_process += df_lbi_2['Tempo de Processo em Anos'].mean(numeric_only = True)
                total_cases += df_lbi_2['_id'].nunique()
                total_sentenced += df_lbi_2.loc[df_lbi_2['status'] == 'Sentenciado'].shape[0]

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]

                avg_process += df_lbi_2['Tempo de Processo em Anos'].mean(numeric_only = True)
                total_cases += df_lbi_2['_id'].nunique()
                total_sentenced += df_lbi_2.loc[df_lbi_2['status'] == 'Sentenciado'].shape[0]
        else:
            for regiao in value_region:
                for estado in value_state:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao))]

                    avg_process += df_lbi_2['Tempo de Processo em Anos'].mean(numeric_only = True)
                    total_cases += df_lbi_2['_id'].nunique()

                    if not df_lbi_2.empty:
                        total_sentenced += df_lbi_2.loc[df_lbi_2['status'] == 'Sentenciado'].shape[0]
                        
        
        if total_cases == 0:
            return '0', ' 0 %'
        else:

            return f"{(avg_process):.2f}".format().replace('.',','), f'{(total_sentenced/total_cases)*100:.2f}'.format().replace('.',',') + ' %'
    else:
        return f"{df_lbi_filter['Tempo de Processo em Anos'].mean(numeric_only = True):.2f}".format().replace('.',','), f"{(df_lbi_filter.loc[df_lbi_filter['status'] == 'Sentenciado'].shape[0])/(df_lbi_filter['_id'].nunique())*100:.2f}".format().replace('.',',') + ' %'

# Demandas
@app.callback(
    Output('process_mil', 'children'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
@cache.memoize(timeout=TIMEOUT)
def update_cards_demand(value_state, value_region):

    total_habitantes = 0
    total_cases = 0

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao)]
                dados_censo_2 = dados_censo.loc[(dados_censo['REGIAO'] == regiao)]
                
                total_cases += df_lbi_2['_id'].nunique()
                total_habitantes += dados_censo_2['POPULAÇÃO / 100K'].sum()

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_lbi_2 = df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]
                dados_censo_2 = dados_censo.loc[(dados_censo['ESTADO'] == unidecode(estado))]
                
                total_cases += df_lbi_2['_id'].nunique()
                total_habitantes += dados_censo_2['POPULAÇÃO / 100K'].sum()
        else:
            for regiao in value_region:
                for estado in value_state:
                    df_lbi_2 = df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao))]
                    dados_censo_2 = dados_censo.loc[((dados_censo['ESTADO'] == unidecode(estado)) & (dados_censo['REGIAO'] == regiao))]
                    
                    total_cases += df_lbi_2['_id'].nunique()
                    total_habitantes += dados_censo_2['POPULAÇÃO / 100K'].sum()
        
        if total_cases == 0:
            return '0'
        else:

            return f"{(total_cases/total_habitantes):.2f}".format().replace('.',',')
    else:
        return f"{df_lbi_filter['_id'].nunique()/dados_censo['POPULAÇÃO / 100K'].sum():.2f}".format().replace('.',',')
    
# ==== Gráficos =====
@app.callback(
    Output('scatter-duration', 'figure'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_scatter_duration(value_state, value_region):
    
    df_scatter_filter = pd.DataFrame()

    df_scatter = df_lbi_filter.copy()

    df_scatter['ESTADOS'] = df_scatter['ESTADOS'].apply(unidecode)

    df_scatter = df_scatter[['ESTADOS', 'Tempo de Processo em Anos']]

    df_scatter_fig = df_scatter.groupby('ESTADOS').agg({'Tempo de Processo em Anos': 'mean', 'ESTADOS': 'count'})

    df_scatter_fig.index.names = ['Estado']
    df_scatter_fig.columns = ['Média de Tempo de Processo em Anos', 'Quantidade de Processos']
    df_scatter_fig = df_scatter_fig.reset_index()

    df_scatter_fig['Região'] = df_scatter_fig['Estado'].map({unidecode(estado): regiao for regiao, estados in LOCALIZACAO.items() for estado in estados})

    fig = px.scatter(
        df_scatter_fig,
        x = 'Média de Tempo de Processo em Anos',
        y = 'Quantidade de Processos',
        hover_name = 'Estado',
        color = 'Região'
    )

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                
                df_scatter_filter = pd.concat([df_scatter_filter, df_scatter_fig.loc[(df_scatter_fig['Região'] == regiao)]])

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_scatter_filter = pd.concat([df_scatter_filter, df_scatter_fig.loc[(df_scatter_fig['Estado'] == unidecode(estado))]])
        else:
            for estado in value_state:
                for regiao in value_region:
                    df_scatter_filter = pd.concat([df_scatter_filter, df_scatter_fig.loc[((df_scatter_fig['Estado'] == unidecode(estado)) & (df_scatter_fig['Região'] == regiao))]])    

        if df_scatter_filter.empty:
            fig = px.scatter(
                df_scatter_filter,
                x = 'Média de Tempo de Processo em Anos',
                y = 'Quantidade de Processos',
                hover_name = 'Estado',
                color = 'Região'
            )

            return fig

        fig = px.scatter(
            df_scatter_filter,
            x = 'Média de Tempo de Processo em Anos',
            y = 'Quantidade de Processos',
            hover_name = 'Estado',
            color = 'Região'
        )

        return fig
    else:
        return fig

@app.callback(
    Output('bar-duration', 'figure'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_bar_duration(value_state, value_region):

    df_bar_filter = pd.DataFrame()
    
    df_bar = df_lbi_filter.copy()
    df_bar = df_bar.loc[df_bar['sentenca'] != 'NÃO CLASSIFICADO']

    df_bar = df_bar['sentenca'].value_counts().to_frame()
    df_bar.index.names = ['Sentença']
    df_bar = df_bar.reset_index()

    df_bar = df_bar.sort_values(by='count')

    fig = px.bar(df_bar, x = 'count', y = 'Sentença', orientation='h', labels={'count': 'Número de Processos'})

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                
                df_bar_filter = pd.concat([df_bar_filter, df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao)]])

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_bar_filter = pd.concat([df_bar_filter, df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]])

        else:
            for estado in value_state:
                for regiao in value_region:
                    df_bar_filter = pd.concat([df_bar_filter, df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao))]])    

        df_bar_filter = df_bar_filter['sentenca'].value_counts().to_frame()
        df_bar_filter.index.names = ['Sentença']
        df_bar_filter = df_bar_filter.reset_index()

        df_bar_filter = df_bar_filter.sort_values(by='count')

        if df_bar_filter.empty:
            fig = px.bar(df_bar_filter, x = 'count', y= 'Sentença', orientation='h', labels={'count': 'Número de Processos'})

            return fig

        fig = px.bar(df_bar_filter, x = 'count', y= 'Sentença', orientation='h', labels={'count': 'Número de Processos'})

        return fig
    else:
        return fig

@app.callback(
    Output('histogram-demand', 'figure'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_bar_stacked_demand(value_state, value_region):
    
    df_bar_filter = pd.DataFrame()
    
    df_bar = df_lbi_filter.copy()

    df_bar = df_bar.groupby(['ano de inicio', 'status']).size().unstack(fill_value=0)
    df_bar.reset_index(inplace = True)
    df_bar['ano de inicio'] = pd.to_datetime(df_bar['ano de inicio'], format='%Y')

    fig = px.bar(df_bar, x = 'ano de inicio', y = ['Sentenciado', 'Não Sentenciado'],
             labels={'value': 'Número de Processos', 'variable': 'Status', 'ano de inicio':'Ano de Início'},
             barmode = 'stack')

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                
                df_bar_filter = pd.concat([df_bar_filter, df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao)]])

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_bar_filter = pd.concat([df_bar_filter, df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]])

        else:
            for estado in value_state:
                for regiao in value_region:
                    df_bar_filter = pd.concat([df_bar_filter, df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao))]])    

        df_bar_filter = df_bar_filter.groupby(['ano de inicio', 'status']).size().unstack(fill_value=0)
        df_bar_filter.reset_index(inplace= True)
        df_bar_filter['ano de inicio'] = pd.to_datetime(df_bar_filter['ano de inicio'], format='%Y')

        if df_bar_filter.empty:
            fig = px.bar(df_bar_filter, x = 'ano de inicio', y = ['Sentenciado', 'Não Sentenciado'],
             labels={'value': 'Número de Processos', 'variable': 'Status', 'ano de inicio':'Ano de Início'},
             barmode = 'stack')

            return fig

        fig = px.bar(df_bar_filter, x = 'ano de inicio', y = ['Sentenciado', 'Não Sentenciado'],
             labels={'value': 'Número de Processos', 'variable': 'Status', 'ano de inicio':'Ano de Início'},
             barmode = 'stack')

        return fig
    else:
        return fig

@app.callback(
    Output('bar-demand', 'figure'),
    [Input('filter-state', 'value'), Input('filter-region', 'value')])
def update_bar_demand(value_state, value_region):

    df_bar_filter = pd.DataFrame()
    
    df_bar = df_lbi_filter.copy()

    df_bar = df_bar['comarca'].value_counts().to_frame()
    df_bar.index.names = ['Comarca']
    df_bar = df_bar.reset_index()
    df_bar = df_bar.sort_values(by='count').tail(10)

    fig = px.bar(df_bar, x = 'count', y = 'Comarca', orientation='h', title = 'Comarcas com Maior Número de Processos', labels={'count': '', 'Comarca':''})

    if (value_state != None and value_state) or (value_region != None and value_region):
        
        if (value_state == None or not value_state) and (value_region != None and value_region):

            for regiao in value_region:
                
                df_bar_filter = pd.concat([df_bar_filter, df_lbi_filter.loc[(df_lbi_filter['regiao'] == regiao)]])

        elif (value_state != None and value_state) and (value_region == None or not value_region):
            for estado in value_state:
                df_bar_filter = pd.concat([df_bar_filter, df_lbi_filter.loc[(df_lbi_filter['ESTADOS'] == unidecode(estado))]])

        else:
            for estado in value_state:
                for regiao in value_region:
                    df_bar_filter = pd.concat([df_bar_filter, df_lbi_filter.loc[((df_lbi_filter['ESTADOS'] == unidecode(estado)) & (df_lbi_filter['regiao'] == regiao))]])    

        df_bar_filter = df_bar_filter['comarca'].value_counts().to_frame()
        df_bar_filter.index.names = ['Comarca']
        df_bar_filter = df_bar_filter.reset_index()
        df_bar_filter = df_bar_filter.sort_values(by='count').tail(10)

        if df_bar_filter.empty:
            fig = px.bar(df_bar_filter, x = 'count', y = 'Comarca', orientation='h', title = 'Comarcas com Maior Número de Processos', labels={'count': '', 'Comarca':''})

            return fig

        fig = px.bar(df_bar_filter, x = 'count', y = 'Comarca', orientation='h', title = 'Comarcas com Maior Número de Processos', labels={'count': '', 'Comarca':''})

        return fig
    else:
        return fig


# Função principal
if __name__=='__main__':
    application = app.server
    application.run(port='8050')
    #application = app.run_server(port='8050', debug = True)