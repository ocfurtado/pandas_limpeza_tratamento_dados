import pandas as pd
import json

with open('churn_nordeste.json') as f:
    json_bruto = json.load(f)

dados_normalizados = pd.json_normalize(json_bruto, record_path='clientes', meta=['regional', 'data_extracao'], sep='_')

#Foi utilizado o sep='_' para manter a consistência com as chaves/colunas que têm nomes compostos, separados por '_'
#Por exemplo, a chave/coluna 'info_pessoal' é separada por '_'. Caso o separador não fosse '_', o nome ficaria como 'info_pessoal.idoso'
#Dessa forma, a escolha pelo separador '_' pode ser resumida em consistência

dados_normalizados

#Impurezas encontradas
#Na coluna 'churn', existe uma célula que não está preenchida. Caso o dado realmente não existe, ela deveria ser preenchida com 'NaN'
#O mesmo acontece para a coluna 'info_pessoal_genero'
#Nesses dois casos, esses valores inexistentes deveriam ser preenchidos com 'NaN'. Dessa forma, seria mais fácil tratá-los, caso necessário.
#Da forma como estar, o Pandas pode interpretar o dado como existente, sendo que isto não é verdade.
#Nas colunas 'conta_cobranca_mensal' e 'conta_cobranca_total' o decimal é ','. O ideal seria convertê-lo para '.', pois o Pandas trabalha com este decimal.

dados_normalizados.info()

#As colunas 'conta_cobranca_mensal' e 'conta_cobranca_total' deveriam ser do tipo float64
#A coluna 'data_extracao' deveria ser convertida para DateTime.

dados_normalizados.to_csv('churn_nordeste_raw.csv', sep=';', index=False, encoding='utf-8')