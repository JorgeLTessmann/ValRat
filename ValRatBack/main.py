# main.py

import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger("main")

from database import engine, SessionLocal, Base

from entities.compra import Compra
from entities.retirada import Retirada
from entities.renda_fixa import RendaFixa
from entities.historico_patrimonio import HistoricoPatrimonio
from entities.historico_ativo import HistoricoAtivo
from entities.usuario import Usuario

from models.compra_model import CompraModel
from models.renda_fixa_model import RendaFixaModel

from services.portfolio_service import montar_portfolio, montar_portfolio_resumido
from services.carteira_service import cadastrar_compra_api, remover_compra, retirar_valor
from services.renda_fixa_service import cadastrar_renda_fixa
from services.market.indicadores_service import get_cdi_atual as buscar_taxa_cdi
from services.analytics.snapshot_service import salvar_snapshot_diario
from services.asset_validator_service import validar_tipo_ativo, buscar_sugestoes_ticker

Base.metadata.create_all(bind=engine)

# =========================
# LIFESPAN & SCHEDULER
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from scheduler import iniciar_scheduler
        iniciar_scheduler()
        logger.info("📅 Módulo de rotinas agendadas (Scheduler) acoplado com sucesso.")
    except Exception as e:
        logger.error(f"⚠️ Falha ao inicializar o Scheduler de mercado: {e}")
    yield

# =========================
# CONFIGURAÇÃO DO APP
# =========================
app = FastAPI(
    title="ValRat API",
    lifespan=lifespan,
    default_response_class=ORJSONResponse
)

# =========================
# CORS MIDDLEWARE
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://val-rat.vercel.app"
    ], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# =========================
# PYDANTIC DTOs
# =========================
class RetiradaModel(BaseModel):
    ticker: str
    quantidade: float

class CadastroModel(BaseModel):
    nome: str
    email: str
    senha: str

class LoginModel(BaseModel):
    email: str
    senha: str

# =========================
# CONTROLE DE CONEXÕES (Session venv)
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# AUTH & AUTO-CADASTRO AUXILIAR
# =========================
def obtener_usuario_por_email(db: Session, email: Optional[str]):
    if not email or email.strip() in ("", "undefined", "null"):
        raise HTTPException(status_code=401, detail="Usuário não identificado no cabeçalho (X-User-Email).")
        
    email_limpo = email.strip()
    usuario = db.query(Usuario).filter(Usuario.email == email_limpo).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return usuario

# =========================================================================
# FUNÇÃO AUXILIAR PARA EVITAR QUE ERROS DE IMPORT CIRCULAR QUEBREM A COMPRA
# =========================================================================
def safe_recalcular_historico(usuario_id: int, data_referencia: str):
    """Executa o recálculo do histórico de forma segura prevenindo loops de importação."""
    try:
        from services.analytics.snapshot_service import recalcular_historico_a_partir_de
        recalcular_historico_a_partir_de(usuario_id, data_referencia)
    except ImportError as ie:
        logger.error(f"⚠️ Erro de importação ao tentar recalcular histórico (provável import circular): {ie}")
    except Exception as e:
        logger.error(f"❌ Erro genérico ao rodar recalcular_historico_a_partir_de: {e}")

# =========================
# ROTAS ENDPOINTS
# =========================

@app.get("/")
async def home():
    return {"status": "online", "projeto": "ValRat Back-end"}


@app.get("/carteira/rapida")
async def get_carteira_rapida(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    try:
        return montar_portfolio_resumido(usuario_id=usuario.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no cálculo resumido: {str(e)}")


@app.get("/carteira/completa")
async def get_carteira_completa(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    try:
        return montar_portfolio(usuario_id=usuario.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento consolidado: {str(e)}")


@app.get("/carteira")
async def get_carteira(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    return await get_carteira_completa(x_user_email=x_user_email, db=db)


@app.post("/compras")
async def post_compras(
    compra: CompraModel,
    background_tasks: BackgroundTasks,
    x_user_email: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    usuario = obtener_usuario_por_email(db, x_user_email)
    try:
        resultado = cadastrar_compra_api(
            usuario_id=usuario.id,
            categoria=compra.categoria,
            ticker=compra.ticker,
            data_compra=compra.data_compra,
            quantidade=compra.quantidade,
            plataforma=compra.plataforma
        )
        if resultado and "erro" in resultado:
            raise HTTPException(status_code=400, detail=resultado["erro"])

        # Dispara o recálculo via BackgroundTask isolada e segura
        background_tasks.add_task(safe_recalcular_historico, usuario.id, str(compra.data_compra))

        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Falha no processamento de ordem de compra: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Erro interno de processamento: {str(e)}")


@app.delete("/compras/{id}")
async def deletar_compra(id: int, x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    resultado = remover_compra(compra_id=id, usuario_id=usuario.id)
    salvar_snapshot_diario(usuario_id=usuario.id)
    return resultado


@app.post("/retiradas")
async def realizar_retirada(retirada: RetiradaModel, x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    resultado = retirar_valor(usuario_id=usuario.id, ticker=retirada.ticker, quantidade=retirada.quantidade)
    salvar_snapshot_diario(usuario_id=usuario.id)
    return resultado


@app.post("/renda-fixa")
async def post_renda_fixa(
    renda_fixa: CompraModel,
    background_tasks: BackgroundTasks,
    x_user_email: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    usuario = obtener_usuario_por_email(db, x_user_email)
    try:
        resultado = cadastrar_renda_fixa(
            usuario_id=usuario.id,
            nome_aplicacao=renda_fixa.nome_aplicacao,
            valor_applied=renda_fixa.valor_investido,
            data_aplicacao=renda_fixa.data_compra,
            data_vencimento=renda_fixa.data_vencimento,
            tipo_ativo=renda_fixa.tipo_renda_fixa,
            indexador=renda_fixa.indexador,
            taxa_contratada=renda_fixa.taxa_contratada,
            tem_carencia=renda_fixa.tem_carencia,
            data_carencia=renda_fixa.data_carencia,
            plataforma=renda_fixa.plataforma
        )

        if resultado and "erro" in resultado:
            raise HTTPException(status_code=400, detail=resultado["erro"])

        # Dispara o recálculo de forma assíncrona e protegida
        background_tasks.add_task(safe_recalcular_historico, usuario.id, str(renda_fixa.data_compra))

        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Falha no cadastro de renda fixa: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Erro interno de processamento: {str(e)}")


@app.get("/historico")
async def get_historico(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)

    historico = db.query(HistoricoPatrimonio)\
                  .filter(HistoricoPatrimonio.usuario_id == usuario.id)\
                  .order_by(HistoricoPatrimonio.data.asc()).all()

    historico_formatado = []
    for item in historico:
        historico_formatado.append({
            "date": item.data.strftime("%Y-%m-%d") if hasattr(item.data, "strftime") else str(item.data).split(" ")[0],
            "value": round(item.patrimonio, 2) if item.patrimonio is not None else 0.0
        })

    from services.analytics.snapshot_service import calcular_snapshot_atual
    hoje_str = datetime.now().strftime("%Y-%m-%d")

    try:
        dados_ao_vivo = calcular_snapshot_atual(usuario.id)
        ponto_hoje = {"date": hoje_str, "value": round(dados_ao_vivo["patrimonio"], 2)}

        if historico_formatado and historico_formatado[-1]["date"] == hoje_str:
            historico_formatado[-1] = ponto_hoje
        else:
            historico_formatado.append(ponto_hoje)
    except Exception as e:
        logger.warning(f"⚠️ Falha ao calcular ponto ao vivo do histórico: {e}")

    if not historico_formatado:
        return []

    try:
        from services.analytics.comparison_service import gerar_comparativo
        return gerar_comparativo(historico_formatado)
    except Exception as e:
        logger.error(f"❌ Falha ao gerar comparativo: {e}")
        return historico_formatado

@app.get("/benchmark")
async def benchmark(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    carteira = montar_portfolio(usuario_id=usuario.id)
    
    cdi_valor = buscar_taxa_cdi() or 10.50
    return {
        "cdi": round(cdi_valor, 2),
        "ibov": 0.0,
        "carteira_percentual": carteira.get("percentChange", 0)
    }


@app.get("/ativos/{ticker}/historico")
async def get_historico_ativo(ticker: str, x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    historico = db.query(HistoricoAtivo)\
                  .filter(HistoricoAtivo.ticker == ticker, HistoricoAtivo.usuario_id == usuario.id)\
                  .order_by(HistoricoAtivo.data.asc()).all()
    
    return [{
        "ticker": item.ticker,
        "nome": item.nome,
        "tipo": item.tipo,
        "quantidade": item.quantidade,
        "preco": item.preco,
        "valor_total": item.valor_total,
        "lucro": item.lucro,
        "variacao": item.variacao,
        "data": item.data
    } for item in historico]


@app.get("/ativos/validar")
async def validar_ativo(ticker: str, tipo: str):
    return validar_tipo_ativo(tipo)


@app.get("/ativos/sugestoes")
async def sugestoes_ativos(termo: str = "", tipo: str = "acao"):
    return buscar_sugestoes_ticker(tipo=tipo, termo=termo)


@app.get("/forcar-snapshot")
async def forcar_snapshot(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    salvar_snapshot_diario(usuario_id=usuario.id)
    return {"mensagem": "Snapshot processado via solicitação manual."}


@app.post("/snapshot")
async def forcar_snapshot_post(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    return await forcar_snapshot(x_user_email=x_user_email, db=db)


@app.post("/cadastro")
async def cadastrar_usuario(dados: CadastroModel, db: Session = Depends(get_db)):
    usuario = Usuario.cadastrar(db, dados.nome, dados.email, dados.senha)
    if not usuario:
        return ORJSONResponse(status_code=400, content={"erro": "Email já cadastrado no sistema"})
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}


@app.post("/login")
async def login_usuario(dados: LoginModel, db: Session = Depends(get_db)):
    usuario = Usuario.login(db, dados.email, dados.senha)
    if not usuario:
        return ORJSONResponse(status_code=401, content={"erro": "Credenciais incorretas"})
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}


@app.post("/historico/recalcular-total", status_code=202)
async def recalcular_historico(
    background_tasks: BackgroundTasks, 
    x_user_email: Optional[str] = Header(None), 
    db: Session = Depends(get_db)
):
    usuario = obtener_usuario_por_email(db, x_user_email)
    
    try:
        from services.analytics.snapshot_service import recalcular_historico_total_do_zero
        background_tasks.add_task(recalcular_historico_total_do_zero, usuario.id)
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar recálculo total: {e}")
    
    return {"status": "recalculo_total_iniciado"}


@app.get("/historico/sincronizar", status_code=202)
async def sincronizar_historico_auto(
    background_tasks: BackgroundTasks, 
    x_user_email: Optional[str] = Header(None), 
    db: Session = Depends(get_db)
):
    """
    Rota acionada automaticamente pelo DashboardHeader ao carregar a página.
    Verifica e sincroniza pontos faltantes de forma assíncrona.
    """
    usuario = obtener_usuario_por_email(db, x_user_email)
    
    try:
        from services.analytics.snapshot_service import recalcular_historico_incremental
        background_tasks.add_task(recalcular_historico_incremental, usuario.id)
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar sincronização incremental: {e}")
    
    return {"status": "sync_started"}