import pandas as pd
import numpy as np
import json

with open('churn_nordeste_raw.json', 'r') as file:
    json_bruto = json.load(file)

dados_normalizados = pd.json_normalize(json_bruto, record_path=['clientes'], meta=['regional', 'data_extracao'], sep='_')

dados_normalizados.info()

dados_normalizados['data_extracao'] = pd.to_datetime(dados_normalizados['data_extracao'], format='%Y-%m-%d')

dados_normalizados[dados_normalizados.select_dtypes('str').columns] = dados_normalizados.select_dtypes('str').apply(lambda x: x.str.strip())

contagem = (dados_normalizados == '').sum()
total_vazios = contagem[contagem > 0].sum()
colunas = contagem[contagem > 0]
print(f'{total_vazios} células foram convertidas de string vazia/espaço nas colunas: ')
for x,y in colunas.items():
    print(x)

dados_normalizados[dados_normalizados.select_dtypes('str').columns] = dados_normalizados.select_dtypes('str').apply(lambda x: x.replace('', np.nan))

dados_normalizados['conta_cobranca_mensal'] = dados_normalizados['conta_cobranca_mensal'].str.replace(',', '.')
dados_normalizados['conta_cobranca_total'] = dados_normalizados['conta_cobranca_total'].str.replace(',', '.')

dados_normalizados['conta_cobranca_mensal'] = pd.to_numeric(dados_normalizados['conta_cobranca_mensal'], errors='coerce')
dados_normalizados['conta_cobranca_total'] = pd.to_numeric(dados_normalizados['conta_cobranca_total'], errors='coerce')

dados_normalizados.info()

dados_normalizados.to_csv('churn_nordeste_transformed.csv', sep=';', index=False, encoding='utf-8')
