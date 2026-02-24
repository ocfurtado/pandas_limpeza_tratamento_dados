import pandas as pd
import numpy as np
import json

def calc_outliers(column, dataframe):
    Q1 = dataframe[column].quantile(.25)
    Q3 = dataframe[column].quantile(.75)

    IQR = Q3 - Q1

    limite_inferior = Q1 - (1.5 * IQR)
    limite_superior = Q3 + (1.5 * IQR)

    outliers_index = (dataframe[column] < limite_inferior) | (dataframe[column] > limite_superior)

    if((dataframe[column] < limite_inferior).any()):
        dataframe.loc[dataframe[column] < limite_inferior, column] = limite_inferior

    if((dataframe[column] > limite_superior).any()):
        dataframe.loc[dataframe[column] > limite_superior, column] = limite_superior
    
    return dataframe

with open('churn_nordeste_raw.json', 'r') as f:
    json_bruto = json.load(f)

dados_normalizados = pd.json_normalize(data=json_bruto, record_path='clientes', meta=['regional', 'data_extracao'], sep='_')

dados_normalizados[['conta_cobranca_mensal', 'conta_cobranca_total']] = dados_normalizados[['conta_cobranca_mensal', 'conta_cobranca_total']].replace(',', '.', regex=True)
dados_normalizados['conta_cobranca_mensal'] = pd.to_numeric(dados_normalizados['conta_cobranca_mensal'], errors='coerce')
dados_normalizados['conta_cobranca_total'] = pd.to_numeric(dados_normalizados['conta_cobranca_total'], errors='coerce')
dados_normalizados['data_extracao'] = pd.to_datetime(dados_normalizados['data_extracao'], format='%Y-%m-%d')

colunas = dados_normalizados.select_dtypes('str').columns
dados_normalizados[colunas] = dados_normalizados[colunas].apply(lambda x: x.str.strip()).replace('', np.nan)

quantidade_nulos = dados_normalizados.isna().sum().sum()
print(f'Não há necessidade de tratar nulos, pois eles não existem após as conversões de tipos e tratamento de strings vazias. Conforme variável "quantidade_nulos" o número é: {quantidade_nulos}')

quantidade_duplicatas = dados_normalizados.duplicated().sum()
print(f'Não há necessidade de tratar duplicatas, pois elas não existem, conforme valor indicado na variável "quantidade_duplicatas": {quantidade_duplicatas}')

dados_normalizados = calc_outliers('conta_meses_contrato', dados_normalizados)
dados_normalizados = calc_outliers('conta_cobranca_mensal', dados_normalizados)
dados_normalizados = calc_outliers('conta_cobranca_total', dados_normalizados)

dados_normalizados = dados_normalizados.drop(columns=['regional', 'data_extracao'])

colunas_categoricas_binarias = []
colunas_categoricas_multicategoria = []

for col in dados_normalizados.select_dtypes(include='str'):
    if(len(dados_normalizados[col].unique()) == 2 and dados_normalizados[col].name != 'servicos_internet' and dados_normalizados[col].name != 'id_cliente'):
        colunas_categoricas_binarias.append(dados_normalizados[col].name)
    elif((len(dados_normalizados[col].unique()) > 2 or dados_normalizados[col].name == 'servicos_internet') and dados_normalizados[col].name != 'id_cliente'):
        colunas_categoricas_multicategoria.append(dados_normalizados[col].name)

mapeamento_binarias = {
    'Sim': 1,
    'Nao': 0,
}
dados_normalizados = dados_normalizados.replace(mapeamento_binarias)

mapeamento_generos = {
    'Masculino': 1,
    'Feminino': 0
}
dados_normalizados = dados_normalizados.replace(mapeamento_generos)
# Destaca-se que a atribuição de 'Masculino' para 1 e 'Feminino' para 0 é arbitrária.

dados_normalizados = pd.get_dummies(dados_normalizados, columns=colunas_categoricas_multicategoria, dtype='int', drop_first=True)
# Como só existem 3 tipos de dados tanto para a coluna 'conta_tipo_contrato' quanto 'conta_pagamento',
# faz sentido utilizar o parâmetro 'drop_first', pois sempre que duas colunas do mesmo tipo tiver valores 0,
# isso significará que o valor é de um terceiro tipo.
# Por exemplo, se 'conta_tipo_contrato_Mensal' e 'conta_tipo_contrato_Um ano' tiverem valor 0, então 'conta_tipo_contrato_Dois anos' existe, ou seja, terá valor 1.

for col in dados_normalizados[colunas_categoricas_binarias]:
    dados_normalizados[col] = pd.to_numeric(dados_normalizados[col])

dados_normalizados.info()
# Após todas as transformações, o DataFrame final não tem as colunas 'regional' e 'data_extracao',
# pois elas não possuem dados que são relevantes para o Modelo. A coluna 'regional' possui somente o valor 'nordeste'
# e a coluna 'data_extracao' somente o valor '2026-02-13'.
# Ademais, a coluna 'id_cliente' é do tipo 'string' e as demais são 'int64' e 'float64'.

print(dados_normalizados.head().to_string())

dados_normalizados.to_csv('churn_nordeste_ml_ready.csv', sep=';', encoding='utf-8', index=False)