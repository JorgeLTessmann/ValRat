# services/carteira_service.py

import logging
from datetime import datetime
from database import SessionLocal
from entities.compra import Compra
from entities.transacao import Transacao
from services.assets.asset_catalog_service import buscar_ativo_catalogo
from services.price_service import buscar_preco
from utils.date_utils import normalizar_data_compra
from services.cache_service import invalidate_cache

logger = logging.getLogger(__name__)


def cadastrar_compra_api(
    usuario_id: int,
    categoria: str,
    ticker: str,
    data_compra,
    quantidade: float,
    plataforma: str,
    tipo_renda_fixa=None,
    valor_investido=None,
    taxa=None,
    indexador=None,
    data_vencimento=None
):
    db = SessionLocal()
    ticker = ticker.strip().upper()
    data_normalizada = normalizar_data_compra(data_compra)

    # =========================
    # Contexto: Renda Fixa
    # =========================
    if categoria.lower() in ["fixa", "renda fixa"]:
        logger.info(f"📥 Cadastrando Renda Fixa para o usuário {usuario_id}: {ticker}")
        
        valor_investido = float(valor_investido or 0.0)
        qtd = float(quantidade or 1.0)

        nova_compra = Compra(
            usuario_id=usuario_id,
            ticker=ticker,
            nome=ticker,
            tipo="fixa",
            categoria="fixa",
            tipo_renda_fixa=tipo_renda_fixa,
            plataforma=plataforma,
            quantidade=qtd,
            quantidade_original=qtd,
            quantidade_restante=qtd,
            preco_compra=1.0 if valor_investido == 0 else (valor_investido / qtd),
            valor_investido=valor_investido,
            valor_atual=valor_investido,
            taxa=taxa,
            indexador=indexador,
            data_vencimento=data_vencimento,
            data_compra=data_normalizada
        )
        db.add(nova_compra)
        db.flush()

        transacao = Transacao(
            usuario_id=usuario_id,
            tipo="compra",
            ticker=ticker,
            quantidade=qtd,
            preco=nova_compra.preco_compra,
            valor=valor_investido,
            status="success"
        )
        db.add(transacao)
        db.commit()
        db.close()

        invalidate_cache(f"portfolio_completo_{usuario_id}")
        return {"mensagem": "Renda fixa cadastrada com sucesso", "id": nova_compra.id}

    # =========================
    # Contexto: Renda Variável ou Cripto
    # =========================
    logger.info(f"📥 Cadastrando {categoria} para o usuário {usuario_id}: {ticker}")

    catalogo = buscar_ativo_catalogo(ticker)
    nome = catalogo.nome if catalogo else ticker
    tipo_busca = "cripto" if categoria == "cripto" else "acao"

    preco_compra = buscar_preco(tipo_busca, ticker, data_normalizada)
    
    if preco_compra is None:
        logger.error(f"❌ Preço não encontrado para {ticker}")
        db.close()
        return {"erro": f"Não foi possível encontrar o preço de {ticker} na data {data_compra}."}
    
    if valor_investido is None:
        valor_investido = quantidade * preco_compra

    nova_compra = Compra(
        usuario_id=usuario_id,
        ticker=ticker,
        nome=nome,
        tipo=categoria,
        categoria=categoria,
        plataforma=plataforma,
        quantidade=quantidade,
        quantidade_original=quantidade,
        quantidade_restante=quantidade,
        preco_compra=preco_compra,
        valor_investido=valor_investido,
        valor_atual=valor_investido,
        taxa=taxa,
        indexador=indexador,
        data_vencimento=data_vencimento,
        data_compra=data_normalizada
    )
    db.add(nova_compra)
    db.flush()

    transacao = Transacao(
        usuario_id=usuario_id,
        tipo="compra",
        ticker=ticker,
        quantidade=quantidade,
        preco=preco_compra,
        valor=valor_investido,
        status="success"
    )
    db.add(transacao)
    db.commit()
    db.refresh(nova_compra)
    db.close()

    invalidate_cache(f"portfolio_completo_{usuario_id}")
    return {"mensagem": "Compra cadastrada com sucesso", "id": nova_compra.id, "preco_compra": preco_compra}


def remover_compra(compra_id: int, usuario_id: int):
    db = SessionLocal()
    compra = db.query(Compra).filter(Compra.id == compra_id, Compra.usuario_id == usuario_id).first()
    
    if not compra:
        db.close()
        return {"erro": "Compra não encontrada ou acesso não autorizado"}
    
    db.delete(compra)
    db.commit()
    db.close()
    
    invalidate_cache(f"portfolio_completo_{usuario_id}")
    return {"mensagem": "Compra removida com sucesso"}


def retirar_valor(usuario_id: int, ticker: str, quantidade: float):
    db = SessionLocal()
    ticker = ticker.upper()

    compras = db.query(Compra).filter(
        Compra.usuario_id == usuario_id,
        Compra.ticker == ticker,
        Compra.quantidade_restante > 0
    ).order_by(Compra.data_compra.asc()).all()

    if not compras:
        db.close()
        return {"erro": "Ativo não encontrado na carteira do usuário"}

    total_disponivel = sum(c.quantidade_restante for c in compras)

    if quantidade > total_disponivel:
        db.close()
        return {"erro": "Quantidade maior que disponível"}

    tipo_ativo = compras[0].categoria
    tipo_busca = "cripto" if tipo_ativo == "cripto" else "acao"
    preco_atual = buscar_preco(tipo_busca, ticker, None)
    
    if preco_atual is None:
        db.close()
        return {"erro": "Não foi possível obter o preço atual do ativo"}

    valor_venda = quantidade * preco_atual
    quantidade_a_retirar = quantidade

    for compra in compras:
        if quantidade_a_retirar <= 0:
            break
        retirar = min(quantidade_a_retirar, compra.quantidade_restante)
        compra.quantidade_restante -= retirar
        quantidade_a_retirar -= retirar

    transacao = Transacao(
        usuario_id=usuario_id,
        tipo="venda",
        ticker=ticker,
        quantidade=quantidade,
        preco=preco_atual,
        valor=valor_venda,
        status="success"
    )
    db.add(transacao)
    db.commit()
    db.close()

    invalidate_cache(f"portfolio_completo_{usuario_id}")
    return {"mensagem": "Retirada realizada com sucesso"}


def buscar_compras_por_ticker(ticker: str, usuario_id: int):
    db = SessionLocal()
    compras = db.query(Compra).filter(
        Compra.ticker == ticker.upper(), 
        Compra.usuario_id == usuario_id
    ).order_by(Compra.data_compra.desc()).all()
    db.close()
    
    return [{
        "id": c.id,
        "data_compra": c.data_compra,
        "quantidade": c.quantidade_restante,
        "preco_compra": c.preco_compra,
        "valor_investido": c.valor_investido,
        "valor_atual": c.valor_atual
    } for c in compras]