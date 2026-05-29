from datetime import datetime
from database import SessionLocal
from entities.compra import Compra
from entities.retirada import Retirada
from services.assets.asset_catalog_service import buscar_ativo_catalogo
from services.price_service import buscar_preco
from utils.date_utils import normalizar_data_compra


def cadastrar_compra_api(
    tipo,
    ticker,
    data_compra,
    quantidade,
    plataforma,
    valor_investido=None,
    taxa=None,
    indexador=None,
    data_vencimento=None
):
    """
    Cadastra uma compra via API.
    Busca automaticamente o preço histórico da data informada.
    """
    db = SessionLocal()

    ticker = ticker.strip().upper()
    data_normalizada = normalizar_data_compra(data_compra)

    # Busca no catálogo
    catalogo = buscar_ativo_catalogo(ticker)
    nome = catalogo.nome if catalogo else ticker

    # =========================
    # RENDA VARIÁVEL
    # =========================
    if tipo in ["acao", "etf", "fii"]:
        
        # Busca o preço histórico na data da compra
        preco_compra = buscar_preco(tipo, ticker, data_normalizada)
        
        if preco_compra is None:
            db.close()
            return {
                "erro": f"Não foi possível encontrar o preço de {ticker} na data {data_compra}. "
                        f"Verifique se a data está correta ou se o ativo existia nessa data."
            }
        
        # Se valor_investido não foi enviado, calcula
        if valor_investido is None:
            valor_investido = quantidade * preco_compra

    # =========================
    # RENDA FIXA E FUNDOS
    # =========================
    else:
        preco_compra = 1
        quantidade = 1
        
        if valor_investido is None:
            valor_investido = 0

    nova_compra = Compra(
        ticker=ticker,
        nome=nome,
        tipo=tipo,
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
    db.commit()
    db.refresh(nova_compra)
    db.close()

    return {
        "mensagem": "Compra cadastrada com sucesso",
        "id": nova_compra.id,
        "preco_compra": preco_compra,
        "data_utilizada": data_normalizada
    }


def remover_compra(compra_id: int):
    """
    Remove uma compra pelo ID
    """
    db = SessionLocal()
    
    compra = db.query(Compra).filter(Compra.id == compra_id).first()
    
    if not compra:
        db.close()
        return {"erro": "Compra não encontrada"}
    
    db.delete(compra)
    db.commit()
    db.close()
    
    return {"mensagem": "Compra removida com sucesso"}


def retirar_valor(ticker, quantidade):
    """
    Realiza retirada de um ativo (alíquota proporcional)
    """
    db = SessionLocal()

    compras = (
        db.query(Compra)
        .filter(
            Compra.ticker == ticker,
            Compra.quantidade_restante > 0
        )
        .order_by(Compra.data_compra.desc())
        .all()
    )

    if not compras:
        db.close()
        return {"erro": "Ativo não encontrado"}

    total_disponivel = sum(c.quantidade_restante for c in compras)

    if quantidade > total_disponivel:
        db.close()
        return {"erro": "Quantidade maior que disponível"}

    # Retirada proporcional
    for compra in compras:
        proporcao = compra.quantidade_restante / total_disponivel
        retirar = int(quantidade * proporcao)
        retirar = min(retirar, compra.quantidade_restante)
        compra.quantidade_restante -= retirar
        quantidade -= retirar

    # Ajuste de arredondamento
    for compra in compras:
        if quantidade <= 0:
            break
        if compra.quantidade_restante > 0:
            retirar = min(quantidade, compra.quantidade_restante)
            compra.quantidade_restante -= retirar
            quantidade -= retirar

    db.commit()
    db.close()

    return {"mensagem": "Retirada realizada com sucesso"}


def buscar_compras_por_ticker(ticker: str):
    """
    Busca todas as compras de um ticker específico
    """
    db = SessionLocal()
    
    compras = (
        db.query(Compra)
        .filter(Compra.ticker == ticker.upper())
        .order_by(Compra.data_compra.desc())
        .all()
    )
    
    db.close()
    
    return [
        {
            "id": c.id,
            "data_compra": c.data_compra,
            "quantidade": c.quantidade_restante,
            "preco_compra": c.preco_compra,
            "valor_investido": c.valor_investido,
            "valor_atual": c.valor_atual
        }
        for c in compras
    ]