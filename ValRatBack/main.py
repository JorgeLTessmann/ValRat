# main.py (CORRIGIDO)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import engine, SessionLocal
from entities.compra import Compra
from entities.retirada import Retirada
from entities.renda_fixa import RendaFixa
from entities.historico_patrimonio import HistoricoPatrimonio
from entities.historico_ativo import HistoricoAtivo

from models.compra_model import CompraModel
from models.renda_fixa_model import RendaFixaModel

from services.portfolio_service import montar_portfolio
from services.carteira_service import cadastrar_compra_api, remover_compra, retirar_valor
from services.renda_fixa_service import cadastrar_renda_fixa
from services.historico_service import registrar_snapshot
from services.market.benchmark_service import get_benchmarks
from services.analytics.snapshot_service import salvar_snapshot_diario


# =========================
# CRIA TABELAS
# =========================

Compra.metadata.create_all(bind=engine)
Retirada.metadata.create_all(bind=engine)
RendaFixa.metadata.create_all(bind=engine)
HistoricoPatrimonio.metadata.create_all(bind=engine)
HistoricoAtivo.metadata.create_all(bind=engine)


# =========================
# LIFESPAN
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Scheduler desativado temporariamente (serviço pode não existir)
    # iniciar_scheduler()
    salvar_snapshot_diario()
    yield


# =========================
# APP
# =========================

app = FastAPI(lifespan=lifespan)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# MODELS
# =========================

class RetiradaModel(BaseModel):
    ticker: str
    quantidade: float


# =========================
# ROTAS
# =========================

@app.get("/")
def home():
    return {"mensagem": "API online"}


@app.get("/carteira")
def get_carteira():
    return montar_portfolio()


@app.post("/compras")
def cadastrar_compra(compra: CompraModel):
    resultado = cadastrar_compra_api(
        tipo=compra.tipo,
        ticker=compra.ticker,
        data_compra=compra.data,
        quantidade=compra.quantidade,
        plataforma=compra.plataforma,
        valor_investido=compra.valor_investido,
        taxa=compra.taxa,
        indexador=compra.indexador,
        data_vencimento=compra.data_vencimento
    )
    registrar_snapshot()
    return resultado


@app.delete("/compras/{id}")
def deletar_compra(id: int):
    resultado = remover_compra(id)
    registrar_snapshot()
    return resultado


@app.post("/retiradas")
def realizar_retirada(retirada: RetiradaModel):
    resultado = retirar_valor(
        ticker=retirada.ticker,
        quantidade=retirada.quantidade
    )
    registrar_snapshot()
    return resultado


@app.post("/renda-fixa")
def criar_renda_fixa(renda_fixa: RendaFixaModel):
    resultado = cadastrar_renda_fixa(renda_fixa)
    registrar_snapshot()
    return resultado


@app.get("/historico")
def get_historico():
    db = SessionLocal()
    historico = db.query(HistoricoPatrimonio).order_by(HistoricoPatrimonio.id.asc()).all()
    
    resultado = []
    for item in historico:
        resultado.append({
            "id": item.id,
            "data": item.data,
            "patrimonio": item.patrimonio,
            "investido": item.investido,
            "lucro": item.lucro
        })
    
    db.close()
    return resultado


@app.get("/benchmark")
def benchmark():
    carteira = montar_portfolio()
    benchmarks = get_benchmarks()
    
    # Adiciona o percentual da carteira no retorno
    benchmarks["carteira_percentual"] = carteira.get("percentChange", 0)
    
    return benchmarks


@app.get("/ativos/{ticker}/historico")
def get_historico_ativo(ticker: str):
    db = SessionLocal()
    
    historico = db.query(HistoricoAtivo).filter(HistoricoAtivo.ticker == ticker).order_by(HistoricoAtivo.data.asc()).all()
    
    resultado = []
    for item in historico:
        resultado.append({
            "ticker": item.ticker,
            "nome": item.nome,
            "tipo": item.tipo,
            "quantidade": item.quantidade,
            "preco": item.preco,
            "valor_total": item.valor_total,
            "lucro": item.lucro,
            "variacao": item.variacao,
            "data": item.data
        })
    
    db.close()
    return resultado

@app.get("/ativos/sugestoes")
def sugestoes_ativos(tipo: str, termo: str = ""):
    """Retorna sugestões de tickers para autocomplete"""
    from services.asset_validator_service import buscar_sugestoes_ticker, obter_opcoes_tipo
    
    if tipo == "__opcoes__":
        return obter_opcoes_tipo()
    
    return buscar_sugestoes_ticker(tipo, termo)


@app.get("/ativos/validar")
def validar_ativo(tipo: str, ticker: str):
    """Valida se um ativo existe antes de cadastrar"""
    from services.asset_validator_service import validar_ticker, validar_tipo_ativo
    
    # Primeiro valida o tipo
    val_tipo = validar_tipo_ativo(tipo)
    if not val_tipo["valido"]:
        return val_tipo
    
    # Depois valida o ticker
    return validar_ticker(ticker, tipo)


@app.get("/ativos/opcoes")
def opcoes_ativos():
    """Retorna todas as opções disponíveis para selects"""
    from services.asset_validator_service import obter_opcoes_tipo, obter_opcoes_indexador
    
    return {
        "tipos": obter_opcoes_tipo(),
        "indexadores": obter_opcoes_indexador(),
        "plataformas": ["XP", "Inter", "Nubank", "BTG", "Clear", "Rico", "Modal"]
    }