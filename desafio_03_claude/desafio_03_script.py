import pandas as pd
import numpy as np
import json

with open('churn_nordeste_raw.json', 'r') as f:
    json_bruto = json.load(f)

dados_normalizados = pd.json_normalize(json_bruto, record_path='clientes', meta=['regional', 'data_extracao'], sep='_')

dados_normalizados[['conta_cobranca_mensal', 'conta_cobranca_total']] = dados_normalizados[['conta_cobranca_mensal', 'conta_cobranca_total']].replace(',', '.', regex=True)
dados_normalizados['conta_cobranca_mensal'] = pd.to_numeric(dados_normalizados['conta_cobranca_mensal'])
dados_normalizados['conta_cobranca_total'] = pd.to_numeric(dados_normalizados['conta_cobranca_total'])
dados_normalizados['data_extracao'] = pd.to_datetime(dados_normalizados['data_extracao'], format='%Y-%m-%d')

colunas_strings = dados_normalizados.select_dtypes('str').columns
dados_normalizados[colunas_strings] = dados_normalizados[colunas_strings].apply(lambda x: x.str.strip())
dados_normalizados[colunas_strings] = dados_normalizados[colunas_strings].replace('', np.nan)

dados_sem_duplicadas = dados_normalizados.drop_duplicates()
# Como o método .drop_duplicate(), por default, compara todas as colunas do DataFrame, ele identifica linhas que tem o mesmo id_cliente,
# mas com outras células com valores diferentes. Dessa forma, essas linhas são consideradas como diferentes.

dados_sem_duplicadas.reset_index(drop=True, inplace=True)

linhas_removidas = dados_normalizados.shape[0] - dados_sem_duplicadas.shape[0]

moda = dados_sem_duplicadas['info_pessoal_genero'].mode()

colunas_valores_nulos = dados_sem_duplicadas.isna().sum()

dados_sem_duplicadas['info_pessoal_genero'] = dados_sem_duplicadas['info_pessoal_genero'].fillna(moda[0])

dados_sem_duplicadas.dropna(subset='churn', inplace=True)
# Como o objetivo principal da análise dos dados é verificar se houve ou não 'churn', as linhas em que os valores da célula dessa coluna sejam NaN
# não ajudaram em nada na referida análise. Motivo este dessas linhas poderem ser removidas do DataFrame sem nenhum prejuízo aparente.

dados_sem_duplicadas.reset_index(drop=True, inplace=True)

print(f"""
RELATÓRIO FINAL
===============
- A quantidade de duplicatas reais removidas é: {linhas_removidas};
- A quantidade de nulos preenchidos pela moda da coluna 'info_pessoal_genero' é: {colunas_valores_nulos['info_pessoal_genero']};
- A quantidade de linhas dropadas por nulo no target é: {colunas_valores_nulos['churn']};
- O DataFrame final ficou com o seguinte shape:
    - Linhas: {dados_sem_duplicadas.shape[0]};
    - Colunas: {dados_sem_duplicadas.shape[1]}.
""")

dados_sem_duplicadas.to_csv('churn_nordeste_clean.csv', sep=';', encoding='utf-8', index=False)


