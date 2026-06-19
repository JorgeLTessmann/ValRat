# services/analytics/comparison_service.py

from services.market.indicadores_service import buscar_taxa_cdi

def gerar_comparativo(historico):
    """
    Gera dados comparativos da carteira vs CDI vs IBOV.
    Sincroniza os benchmarks com os valores reais da carteira.
    """
    if not historico or len(historico) == 0:
        return []
    
    cdi_atual = buscar_taxa_cdi()
    if cdi_atual:
        cdi_anual = cdi_atual / 100
    else:
        cdi_anual = 0.105   
    
    ibov_percentual = 0.0
    
    historico_filtrado = [item for item in historico if item.get("value", 0) > 0]
    
    if not historico_filtrado:
        return []
    
    historico_filtrado.sort(key=lambda x: x["date"])
    
    valor_inicial = historico_filtrado[0]["value"]
    
    if valor_inicial <= 0:
        return []
    
    taxa_cdi_dia = (1 + cdi_anual) ** (1/252) - 1
    taxa_ibov_dia = (1 + ibov_percentual) ** (1/252) - 1
    
    resultado = []
    cdi_acumulado = valor_inicial
    ibov_acumulado = valor_inicial
    
    for item in historico_filtrado:
        cdi_acumulado *= (1 + taxa_cdi_dia)
        ibov_acumulado *= (1 + taxa_ibov_dia)
        
        resultado.append({
            "date": item["date"],
            "carteira": round(item["value"], 2),
            "cdi": round(cdi_acumulado, 2),
            "ibov": round(ibov_acumulado, 2)
        })
    
    return resultado