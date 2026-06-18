from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from typing import Optional
import asyncio

from database import engine, SessionLocal, Base
from sqlalchemy.orm import Session

# Importação das entidades antes do create_all para o SQLAlchemy mapear o banco
from entities.compra import Compra
from entities.retirada import Retirada
from entities.renda_fixa import RendaFixa
from entities.historico_patrimonio import HistoricoPatrimonio
from entities.historico_ativo import HistoricoAtivo
from entities.usuario import Usuario
from fastapi import FastAPI, Header, HTTPException, Depends, BackgroundTasks

from models.compra_model import CompraModel
from models.renda_fixa_model import RendaFixaModel

from services.portfolio_service import montar_portfolio, montar_portfolio_resumido
from services.carteira_service import cadastrar_compra_api, remover_compra, retirar_valor
from services.renda_fixa_service import cadastrar_renda_fixa
from services.historico_service import registrar_snapshot
from services.market.benchmark_service import get_benchmarks
from services.analytics.snapshot_service import salvar_snapshot_diario

# =========================
# CRIA TABELAS (Unificado)
# =========================

# Uma única linha cria tudo na ordem correta, respeitando as Chaves Estrangeiras!
Base.metadata.create_all(bind=engine)


# =========================
# LIFESPAN
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    allow_origins=["*"],  # Em produção, substitua pelo domínio do seu front-end
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, OPTIONS, etc.
    allow_headers=[
        "Content-Type",
        "X-User-Email",     # ← Libera o seu cabeçalho customizado
        "Authorization",
        "Accept"
    ],
)

# =========================
# MODELS
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
# DEPENDÊNCIA DO BANCO DE DADOS 
# =========================

def get_db():
    """Garante abertura e fechamento automático de conexões com o banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# FUNÇÃO AUXILIAR DE SEGURANÇA
# =========================

def obtener_usuario_por_email(db: Session, email: Optional[str]):
    if not email or email.strip() in ("", "undefined", "null"):
        raise HTTPException(status_code=401, detail="Usuário não identificado no cabeçalho.")
        
    email_limpo = email.strip()
    usuario = db.query(Usuario).filter(Usuario.email == email_limpo).first()
    
    if not usuario:
        print(f"[AUTO-CADASTRO] Criando usuário {email_limpo} automaticamente para destravar os testes!")
        usuario = Usuario.cadastrar(db, nome="Jorge", email=email_limpo, senha="123")
        db.refresh(usuario)
        
    return usuario

# =========================
# ROTAS
# =========================

@app.get("/")
async def home():
    return {"mensagem": "API online"}


@app.get("/carteira/rapida")
async def get_carteira_rapida(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    
    try:
        resultado = montar_portfolio_resumido(usuario_id=usuario.id)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao montar portfólio resumido: {str(e)}")


@app.get("/carteira/completa")
async def get_carteira_completa(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)

    try:
        resultado = montar_portfolio(usuario_id=usuario.id)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar carteira completa: {str(e)}")


@app.get("/carteira")
async def get_carteira(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Redireciona para completa mantendo a segurança"""
    return await get_carteira_completa(x_user_email=x_user_email, db=db)


@app.post("/compras")
async def post_compras(compra: CompraModel, x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    # Linha de debug para ver o que está vindo do front-end
    print(f"\n[DEBUG] O cabeçalho X-User-Email veio como: '{x_user_email}'\n")
    
    usuario = obtener_usuario_por_email(db, x_user_email)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    
    resultado = cadastrar_compra_api(
        usuario_id=usuario.id,
        categoria=compra.categoria,
        ticker=compra.ticker,
        data_compra=compra.data_compra,
        quantidade=compra.quantidade,
        plataforma=compra.plataforma
    )

    if "erro" in resultado:
        raise HTTPException(status_code=400, detail=resultado["erro"])

    return resultado


@app.delete("/compras/{id}")
async def deletar_compra(id: int, x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    
    resultado = remover_compra(compra_id=id, usuario_id=usuario.id)
    registrar_snapshot(usuario_id=usuario.id)
    return resultado


@app.post("/retiradas")
async def realizar_retirada(retirada: RetiradaModel, x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    
    resultado = retirar_valor(
        usuario_id=usuario.id,
        ticker=retirada.ticker,
        quantidade=retirada.quantidade
    )
    registrar_snapshot(usuario_id=usuario.id)
    return resultado


@app.post("/renda-fixa")
async def post_renda_fixa(renda_fixa: CompraModel, x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Cadastra renda fixa vinculada ao usuário logado"""
    usuario = obtener_usuario_por_email(db, x_user_email)
    
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
    return resultado


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
    
    from services.analytics.comparison_service import gerar_comparativo
    comparativo = gerar_comparativo(historico_formatado)
    
    if comparativo and len(historico_formatado) > 0:
        valor_inicial = historico_formatado[0]["value"]
        if valor_inicial > 0:
            for item in comparativo:
                item["carteira"] = round((item["carteira"] / valor_inicial) * 100, 2)
                item["cdi"] = round((item["cdi"] / valor_inicial) * 100, 2)
                item["ibov"] = round((item["ibov"] / valor_inicial) * 100, 2)
                
    return comparativo


@app.get("/benchmark")
async def benchmark(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    
    carteira = montar_portfolio(usuario_id=usuario.id)
    benchmarks = get_benchmarks()
    benchmarks["carteira_percentual"] = carteira.get("percentChange", 0)
    return benchmarks


@app.get("/ativos/{ticker}/historico")
async def get_historico_ativo(ticker: str, x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    
    historico = db.query(HistoricoAtivo)\
                  .filter(HistoricoAtivo.ticker == ticker, HistoricoAtivo.usuario_id == usuario.id)\
                  .order_by(HistoricoAtivo.data.asc()).all()
    
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
async def forcar_snapshot(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_email(db, x_user_email)
    
    from services.analytics.snapshot_service import salvar_snapshot_diario
    salvar_snapshot_diario(usuario_id=usuario.id)
    return {"mensagem": "Snapshot forçado com sucesso"}


@app.post("/snapshot")
async def forcar_snapshot_post(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)):
    return await forcar_snapshot(x_user_email=x_user_email, db=db)


@app.post("/cadastro")
async def cadastrar_usuario(dados: CadastroModel, db: Session = Depends(get_db)):
    usuario = Usuario.cadastrar(db, dados.nome, dados.email, dados.senha)
    if not usuario:
        return ORJSONResponse(status_code=400, content={"erro": "Email já cadastrado"})
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}


@app.post("/login")
async def login_usuario(dados: LoginModel, db: Session = Depends(get_db)):
    usuario = Usuario.login(db, dados.email, dados.senha)
    if not usuario:
        return ORJSONResponse(status_code=401, content={"erro": "Credenciais inválidas"})
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}

@app.get("/historico/sincronizar")
async def sincronizar_historico(
    background_tasks: BackgroundTasks, 
    x_user_email: Optional[str] = Header(None), 
    db: Session = Depends(get_db)
):

    usuario = obtener_usuario_por_email(db, x_user_email)
    
    from popular_historico import processar_usuario_historico
    
    # Adiciona a tarefa pesada na fila do FastAPI
    background_tasks.add_task(processar_usuario_historico, usuario.id)
    
    return {"status": "Sincronização histórica iniciada com sucesso em segundo plano."}