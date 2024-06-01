import pandas as pd

# Carregando o arquivo CSV
df = pd.read_csv('admin_HD_LBI.csv')

# Dicionário para mapear UF para região
uf_to_region = {
    'AC': 'Norte',
    'AL': 'Nordeste',
    'AP': 'Norte',
    'AM': 'Norte',
    'BA': 'Nordeste',
    'CE': 'Nordeste',
    'DF': 'Centro-Oeste',
    'ES': 'Sudeste',
    'GO': 'Centro-Oeste',
    'MA': 'Nordeste',
    'MT': 'Centro-Oeste',
    'MS': 'Centro-Oeste',
    'MG': 'Sudeste',
    'PA': 'Norte',
    'PB': 'Nordeste',
    'PR': 'Sul',
    'PE': 'Nordeste',
    'PI': 'Nordeste',
    'RJ': 'Sudeste',
    'RN': 'Nordeste',
    'RS': 'Sul',
    'RO': 'Norte',
    'RR': 'Norte',
    'SC': 'Sul',
    'SP': 'Sudeste',
    'SE': 'Nordeste',
    'TO': 'Norte'
}

# Preenchendo os valores ausentes na coluna 'regiao' com base na UF
df['regiao'] = df.apply(lambda row: uf_to_region.get(row['UF'], row['regiao']), axis=1)

# Salvando o DataFrame atualizado de volta no arquivo CSV
df.to_csv('admin_HD_LBI_completo.csv', index=False)