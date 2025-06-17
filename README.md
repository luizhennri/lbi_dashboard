# Dashboard sobre a Lei Brasileira de Inclusão (LBI)

Painel de visualização desenvolvido para o Projeto de Iniciação Científica da USP (PUB - USP) sobre a Lei Brasileira de Inclusão (LBI) utlizando a biblioteca Dash da linguagem Python.


## Histórico:

10/2024: versão 1.3
- Documentação e divisão da importação dos dados e constantes (Incompleto)

9/2024: versão 1.2
- Inserção do sistema de cache para optimização

8/2024: versão 1.1
- Organização dos arquivos, pastas e código

6/2024: versão 1.0
- Abas: Início, Visão Geral, Duração e Demandas
- Criação dos elementos do dashboard, das funções de cálculo e paginação
- Estilo do dashboard

## Componentes:
- Dash (v2.16.1)
- Pandas (v2.2.2)
- Plotly (v5.18.0)
- Plotly Express (v0.4.1)
- Unidecode (v1.3.6)
- Urllib3 (v1.26.14)
- Numpy (v1.26.4)
- Flask Caching (v2.3.0)
- Python Dotenv (v1.0.1)


## Requisitos:
- Python 3.13.5
- Pip 25.1.1

## Instalando a Aplicação no Ambiente de Desenvolvimento:

### Baixar e Instalar o Python e o Pip

### Instalar as Dependências Necessárias
```
pip install requirements.txt
```

### Executar o Comando Para Rodar a Aplicação
```
python app.py
```

## Instalando a Aplicação em Uma Máquina Remota:

### Baixar e Instalar o Python

### Instalar as dependências necessárias
```
pip install requirements.txt
```

### Executar o Comando Para Rodar a Aplicação em Segundo Plano (troque o ip caso necessário)
```
gunicorn -b 127.0.0.1:8050 app:application --workers=4 &
```


## Observações:
- No ambiente de produção deve ser feito a configuração e o direcionamento para o ip que está sendo rodada a aplicação (localhost) em caso de sua utilização em um site ou link embebido;
- Bugs: Formatação dos tipos de dados das colunas do dataset e possibilidade de pesquisa por um estado que não compõe uma região.