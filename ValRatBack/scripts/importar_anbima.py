# scripts/importar_anbima.py
import pandas as pd
import os

def importar_titulos_anbima(caminho_planilha):
    # Lê a planilha que você já baixou
    df = pd.read_excel(caminho_planilha)
    
    # Mapeia as colunas da ANBIMA para sua tabela ativos_master
    for idx, row in df.iterrows():
        cadastrar_ativo_catalogo(
            codigo=row['codigo'],
            nome=row['titulo'],
            tipo='cdb' if 'CDB' in row['tipo'] else 'lci',
            indexador=row['indexador'],
            taxa=row['taxa'] / 100 # converte para decimal
        )