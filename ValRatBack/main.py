from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

from database import engine, SessionLocal
from entities.compra import Compra
from entities.retirada import Retirada
from entities.renda_fixa import RendaFixa
from entities.historico_patrimonio import HistoricoPatrimonio
from entities.historico_ativo import HistoricoAtivo

from models.compra_model import CompraModel
from models.renda_fixa_model import RendaFixaModel

from services.portfolio_service import montar_portfolio, montar_portfolio_resumido
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

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Roda em background (não aguarda)
    yield


# =========================
# APP
# =========================

app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
async def home():
    return {"mensagem": "API online"}


@app.get("/carteira/rapida")
async def get_carteira_rapida():
    """Versão rápida (apenas totais do último snapshot)"""
    return montar_portfolio_resumido()


@app.get("/carteira/completa")
async def get_carteira_completa(force_refresh: bool = False):
    """Versão completa com cache de 30 segundos"""
    return montar_portfolio(force_refresh=force_refresh)


@app.get("/carteira")
async def get_carteira(force_refresh: bool = False):
    """Redireciona para completa (compatibilidade)"""
    return montar_portfolio(force_refresh=force_refresh)


@app.post("/compras")
async def post_compras(compra: CompraModel):
    """Cadastra renda variável ou criptomoeda"""
    resultado = cadastrar_compra_api(
        categoria=compra.categoria,
        ticker=compra.ticker,
        data_compra=compra.data_compra,
        quantidade=compra.quantidade,
        plataforma=compra.plataforma
    )
    return resultado


@app.delete("/compras/{id}")
async def deletar_compra(id: int):
    resultado = remover_compra(id)
    registrar_snapshot()
    return resultado


@app.post("/retiradas")
async def realizar_retirada(retirada: RetiradaModel):
    resultado = retirar_valor(
        ticker=retirada.ticker,
        quantidade=retirada.quantidade
    )
    registrar_snapshot()
    return resultado


@app.post("/renda-fixa")
async def post_renda_fixa(renda_fixa: CompraModel):
    """Cadastra renda fixa (CDB, LCI, LCA, Tesouro)"""
    resultado = cadastrar_renda_fixa(
        nome_aplicacao=renda_fixa.nome_aplicacao,
        valor_aplicado=renda_fixa.valor_investido,
        data_aplicacao=renda_fixa.data_compra,  # ← MUDOU AQUI
        data_vencimento=renda_fixa.data_vencimento,
        tipo_ativo=renda_fixa.tipo_renda_fixa,  # ← MUDOU AQUI
        indexador=renda_fixa.indexador,
        taxa_contratada=renda_fixa.taxa_contratada,
        tem_carencia=renda_fixa.tem_carencia,
        data_carencia=renda_fixa.data_carencia,
        plataforma=renda_fixa.plataforma
    )
    return resultado

@app.get("/historico")
async def get_historico():
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
async def benchmark():
    carteira = montar_portfolio()
    benchmarks = get_benchmarks()
    benchmarks["carteira_percentual"] = carteira.get("percentChange", 0)
    return benchmarks


@app.get("/ativos/{ticker}/historico")
async def get_historico_ativo(ticker: str):
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


@app.get("/ativos/validar")
async def validar_ativo(ticker: str, tipo: str):
    from services.asset_cache_service import validar_ativo
    return validar_ativo(ticker, tipo)


@app.get("/ativos/sugestoes")
async def sugestoes_ativos(termo: str = ""):
    from services.asset_cache_service import buscar_sugestoes
    return buscar_sugestoes(termo)

@app.get("/forcar-snapshot")
async def forcar_snapshot():
    from services.analytics.snapshot_service import salvar_snapshot_diario
    salvar_snapshot_diario()
    return {"mensagem": "Snapshot forçado com sucesso"}

@app.post("/snapshot")
async def forcar_snapshot_post():
    from services.analytics.snapshot_service import salvar_snapshot_diario
    salvar_snapshot_diario()
    return {"mensagem": "Snapshot forçado"}