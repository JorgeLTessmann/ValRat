# scripts/importar_fundos_cvm.py
import pandas as pd
import requests
from services.assets.asset_catalog_service import cadastrar_ativo_catalogo

def importar_fundos_cvm():
    # URL direta dos dados cadastrais da CVM
    url = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
    
    print("Baixando dados oficiais da CVM...")
    df = pd.read_csv(url, sep=';', encoding='latin1', low_memory=False)
    
    # Filtra os fundos ativos e adapta para sua tabela
    for idx, row in df.iterrows():
        if idx > 100: # Limite apenas para teste inicial
            break
            
        cadastrar_ativo_catalogo(
            codigo=str(row['CNPJ_FUNDO']), # Use o CNPJ como código único
            nome=row['DENOM_SOCIAL'],
            tipo='fundo',        # Sua classificação
            indexador=None,      # Varia muito, analisar depois
            instituicao=row['ENTIDADE_INVEST'] # Administradora
            # ATENÇÃO: O cálculo real do preço da cota está no INF_DIARIO_FI
        )