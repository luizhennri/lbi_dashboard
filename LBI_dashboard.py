# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import json
from urllib.request import urlopen
import plotly.express as px
from unidecode import unidecode

# Importação dos dados
df_lbi = pd.read_csv('C:/projects/pub/LBI/admin_HD_LBI.csv')
df_dados_mapa = pd.read_csv('C:/projects/pub/LBI/dados_mapa.csv')

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

for feature in Brazil['features']: 
    feature['id'] = unidecode(feature['properties']['name'])
    state_id_map[feature['properties']['sigla']] = feature['id']

BRAZIL_GEOJSON = Brazil.copy()

# Inicialização do Aplicativo
app = Dash(__name__, assets_external_path = 'C:/projects/pub/LBI/Site_HabeasData/assets', title = 'LBI Dashboard', update_title='Atualizando ...', suppress_callback_exceptions=True)

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
    title = "Processos por Estado",
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

            html.Label("Filtrar por Estado"),
            dcc.Dropdown(
                ESTADOS,
                multi = True,
                clearable = True,
                id = "filter-state"
            ),

            html.Label("Filtrar por Região"),
            dcc.Dropdown(
                REGIOES,
                multi = True,
                clearable = True,
                id = "filter-region"
            ),
            
            html.Div([
                html.H6(children='Total de Processos',
                        style={
                            'textAlign': 'center',
                            'color': '#252423',
                            'font-weight':'bold'}
                        ),

                html.Div(None,
                    style={
                        'textAlign': 'center',
                        'color': '#252423',
                        'fontSize': 30},
                    id = 'total_cases'
                    ),

                html.Div(
                    dcc.Graph(figure = fig)
                )
            ], style={
                      'widtg': '5px',
                      'height': '5px'}, className="row flex-display"),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.H6(children='Área do Direito Mais presente',
                                style={
                                    'textAlign': 'center',
                                    'color': '#252423',
                                    'margin-bottom': '3px',
                                    'font-weight':'bold'}
                                ),

                        html.P(f"{df_lbi_filter['area_direito'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold'}
                            ),

                        html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 30,
                                'margin-top': '-10px'},
                                id = 'total_area_direito'
                            ),

                        html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 15,
                                'margin-top': '-18px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )], className="row flex-display"
                )], style={'float':'center',
                    'border-radius': '25px',
                    'border-style': 'outset'}),

                html.Div([
                    html.Div([
                        html.H6(children='Maior Matéria Principal',
                                style={
                                    'textAlign': 'center',
                                    'color': '#252423',
                                    'margin-bottom': '3px',
                                    'font-weight':'bold'}
                                ),

                        html.P(f"{df_lbi_filter['materia_principal'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold'}
                            ),

                        html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 30,
                                'margin-top': '-10px'},
                                id = 'total_materia_principal'
                            ),

                        html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 15,
                                'margin-top': '-18px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )], className="row flex-display"
                )], style={'float':'right',
                    'border-radius': '25px',
                    'border-style': 'outset'})
            ], style={'float':'right',
                    'vertical-align': 'top',
                    'margin-left': '20px'}),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.H6(children='Natureza do processo Mais presente',
                                style={
                                    'textAlign': 'center',
                                    'color': '#252423',
                                    'margin-bottom': '3px',
                                    'font-weight':'bold'}
                                ),

                        html.P(f"{df_lbi_filter['natureza_processo'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold'}
                            ),

                        html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 30,
                                'margin-top': '-10px'},
                                id = 'total_natureza_processo'
                            ),

                        html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 15,
                                'margin-top': '-18px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )], className="row flex-display"
                )], style={'float':'center',
                    'border-radius': '25px',
                    'border-style': 'outset'}),

                html.Div([
                    html.Div([
                        html.H6(children='Natureza da Vara mais Presente',
                                style={
                                    'textAlign': 'center',
                                    'color': '#252423',
                                    'margin-bottom': '3px',
                                    'font-weight':'bold'}
                                ),

                        html.P(f"{df_lbi_filter['natureza_vara'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold'}
                            ),

                        html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 30,
                                'margin-top': '-10px'},
                                id = 'total_natureza_vara'
                            ),

                        html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 15,
                                'margin-top': '-18px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )], className="row flex-display"
                )], style={'float':'right',
                    'border-radius': '25px',
                    'border-style': 'outset'})
            ], style={'float':'right',
                    'vertical-align': 'middle',
                    'margin-left':'20px'}),

            html.Div([
                html.Div([
                    html.Div([
                        html.H6(children='Procedimento Mais Presente',
                                style={
                                    'textAlign': 'center',
                                    'color': '#252423',
                                    'margin-bottom': '3px',
                                    'font-weight':'bold'}
                                ),

                        html.P(f"{df_lbi_filter['procedimento'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold'}
                            ),

                        html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 30,
                                'margin-top': '-10px'},
                                id = 'total_procedimento'
                            ),

                        html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 15,
                                'margin-top': '-18px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )], className="row flex-display"
                )], style={'float':'center',
                    'border-radius': '25px',
                    'border-style': 'outset'}),

                html.Div([
                    html.Div([
                        html.H6(children='Tipo de Processo Mais Presente',
                                style={
                                    'textAlign': 'center',
                                    'color': '#252423',
                                    'margin-bottom': '3px',
                                    'font-weight':'bold'}
                                ),

                        html.P(f"{df_lbi_filter['tipo_processo'].value_counts().index.tolist()[0]}",
                            style={
                                'textAlign': 'center',
                                'color': '#118DFF',
                                'fontSize': 15,
                                'font-weight':'bold'}
                            ),

                        html.P(None,
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 30,
                                'margin-top': '-10px'},
                                id = 'total_tipo_processo'
                            ),

                        html.P('dos processos',
                            style={
                                'textAlign': 'center',
                                'color': '#252423',
                                'fontSize': 15,
                                'margin-top': '-18px',
                                'margin-left': '48px',
                                'font-weight':'bold'}
                            )], className="row flex-display"
                )], style={'float':'right',
                    'border-radius': '25px',
                    'border-style': 'outset'})
            ], style={'float':'right',
                    'vertical-align':'bottom',
                    'margin-left':'20px'})

        
        ])

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