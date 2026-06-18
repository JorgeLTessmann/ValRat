import requests
from datetime import date, timedelta
from typing import Optional

AWESOME_BASE = "https://economia.awesomeapi.com.br/json/daily/USD-BRL"
FALLBACK_RATE = 5.40

def _buscar_cotacao_awesomeapi(data: date) -> Optional[float]:
    try:
        data_str = data.strftime("%Y%m%d")
        res = requests.get(f"{AWESOME_BASE}/?start_date={data_str}&end_date={data_str}", timeout=10)
        
        if res.status_code == 200 and (dados := res.json()):
            taxa = float(dados[0].get("bid", 0))
            if taxa > 0: return taxa
        return None
    except Exception as e:
        print(f"❌ Erro AwesomeAPI {data}: {e}")
        return None

def buscar_taxa_cambio_usd_brl(data: date) -> float:
    for delta in range(5):
        if (taxa := _buscar_cotacao_awesomeapi(data - timedelta(days=delta))) is not None:
            return taxa
    return FALLBACK_RATE

def buscar_taxa_cambio_atual() -> float:
    return buscar_taxa_cambio_usd_brl(date.today())