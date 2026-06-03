from services.market.brasilapi_service import buscar_taxa_cdi
from services.brapi_service import buscar_historico_ibov


def gerar_comparativo(historico):
    """
    Gera dados comparativos da carteira vs CDI vs IBOV.
    Sincroniza os benchmarks com os valores reais da carteira.
    """
    if not historico or len(historico) == 0:
        return []
    
    # Busca taxas reais
    cdi_atual = buscar_taxa_cdi()
    if cdi_atual:
        cdi_anual = cdi_atual / 100
    else:
        cdi_anual = 0.105  # fallback conservador (10.5% ao ano)
    
    ibov = buscar_historico_ibov()
    if ibov:
        ibov_percentual = ibov.get("regularMarketChangePercent", 0) / 100
    else:
        ibov_percentual = 0
    
    # Filtra apenas entradas com valor > 0 (ignora snapshots zerados)
    historico_filtrado = [item for item in historico if item["value"] > 0]
    
    if not historico_filtrado:
        return []
    
    # Ordena por data
    historico_filtrado.sort(key=lambda x: x["date"])
    
    # Pega o primeiro valor da carteira que não seja zero
    valor_inicial = historico_filtrado[0]["value"]
    
    if valor_inicial <= 0:
        return []
    
    # Calcula taxas diárias
    taxa_cdi_dia = (1 + cdi_anual) ** (1/252) - 1
    taxa_ibov_dia = (1 + ibov_percentual) ** (1/252) - 1
    
    resultado = []
    cdi_acumulado = valor_inicial
    ibov_acumulado = valor_inicial
    
    for item in historico_filtrado:
        # Atualiza benchmarks
        cdi_acumulado *= (1 + taxa_cdi_dia)
        ibov_acumulado *= (1 + taxa_ibov_dia)
        
        resultado.append({
            "date": item["date"],
            "carteira": round(item["value"], 2),
            "cdi": round(cdi_acumulado, 2),
            "ibov": round(ibov_acumulado, 2)
        })
    
    return resultado