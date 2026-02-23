import pandas as pd
import numpy as np
import json

def calc_outliers(column, dataframe):
    contagem = 0

    Q1 = dataframe[column].quantile(.25)
    Q3 = dataframe[column].quantile(.75)

    IQR = Q3 - Q1

    limite_inferior = Q1 - (1.5 * IQR)
    limite_superior = Q3 + (1.5 * IQR)

    print(f'Para a coluna ({column}), o valor do limite inferior é: {limite_inferior}')
    print(f'Para a coluna ({column}), o valor do limite superior é: {limite_superior}')

    outliers_index = (dataframe[column] < limite_inferior) | (dataframe[column] > limite_superior)

    print('Abaixo seguem os registros que caíram fora dos limites e os seus respectivos valores:')
    print(dataframe[outliers_index][['id_cliente', column]].to_string())

    if((dataframe[column] < limite_inferior).any()):
        contagem += (dataframe[column] < limite_inferior).sum()
        dataframe.loc[dataframe[column] < limite_inferior, column] = limite_inferior

    if((dataframe[column] > limite_superior).any()):
        contagem += (dataframe[column] > limite_superior).sum()
        dataframe.loc[dataframe[column] > limite_superior, column] = limite_superior

    # Como o DataFrame tem poucos registros e o foco principal é analisar o 'churn',
    # remover linhas não é o ideal.
    # Na pior das hipóteses, mantemos os valores dentro dos limites, para não 'perturbar' muito
    # uma análise de uma determinada coluna com outliers.

    print(f'Na coluna ({column}), foram encontrados e tratados {contagem} outliers.')

    return dataframe

with open('churn_nordeste_raw.json', 'r') as f:
    json_bruto = json.load(f)

dados_normalizados = pd.json_normalize(json_bruto, record_path='clientes', meta=['regional', 'data_extracao'], sep='_')

dados_normalizados[['conta_cobranca_mensal', 'conta_cobranca_total']] = dados_normalizados[['conta_cobranca_mensal', 'conta_cobranca_total']].replace(',', '.', regex=True)
dados_normalizados['conta_cobranca_mensal'] = pd.to_numeric(dados_normalizados['conta_cobranca_mensal'], errors='raise')
dados_normalizados['conta_cobranca_total'] = pd.to_numeric(dados_normalizados['conta_cobranca_total'], errors='raise')
dados_normalizados['data_extracao'] = pd.to_datetime(dados_normalizados['data_extracao'], format='%Y-%m-%d')

colunas_str = dados_normalizados.select_dtypes('str').columns
dados_normalizados[colunas_str] = dados_normalizados[colunas_str].apply(lambda x: x.str.strip()).replace('', np.nan)

print(f'Describe inicial: {dados_normalizados.describe()}')

dados_normalizados = calc_outliers('conta_cobranca_mensal', dados_normalizados)
dados_normalizados = calc_outliers('conta_cobranca_total', dados_normalizados)
dados_normalizados = calc_outliers('conta_meses_contrato', dados_normalizados)

print(f'Describe final: {dados_normalizados.describe()}')

dados_normalizados.to_csv('churn_nordeste_outliers_treated.csv', sep=';', encoding='utf-8', index=False)