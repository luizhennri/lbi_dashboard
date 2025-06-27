import pandas as pd
import numpy as np
from const import *

# Correções
df_lbi = pd.read_csv("assets/data/dados_lbi.csv")

df_lbi['regiao'] = df_lbi.apply(lambda row: UF_TO_REGION.get(row['UF'], row['regiao']), axis=1)

df_lbi['Tempo de Processo em Anos'] = df_lbi['Tempo de Processo em Anos'].str.replace(',', '.').astype(float).apply(lambda x: np.nan if x < 0 else x)

DF_DATA = df_lbi.copy()

dados_censo = pd.read_csv('./assets/data/dados_censo.csv')

dados_censo = dados_censo.drop(columns=['PROCESSOS POR 100MIL HABITANTES', 'Quantidade de Processos por Estado'])
dados_censo['POPULAÇÃO / 100K'] = dados_censo['POPULAÇÃO / 100K'].str.replace(',', '.').astype(float)
dados_censo['REGIAO'] = dados_censo['REGIAO'].str.replace('Região ', '')

DF_CENSO = dados_censo.copy()

DF_MAPA = pd.read_csv('./assets/data/dados_mapa.csv')