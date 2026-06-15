# services/carteira_service.py

import logging
from datetime import datetime
from database import SessionLocal
from entities.compra import Compra
from entities.retirada import Retirada
from services.assets.asset_catalog_service import buscar_ativo_catalogo
from services.price_service import buscar_preco
from utils.date_utils import normalizar_data_compra
from entities.transacao import Transacao
from services.cache_service import invalidate_cache

logger = logging.getLogger(__name__)


def cadastrar_compra_api(
    usuario_id: int,  # ← Adicionado parâmetro para isolamento
    categoria,
    ticker,
    data_compra,
    quantidade,
    plataforma,
    tipo_renda_fixa=None,
    valor_investido=None,
    taxa=None,
    indexador=None,
    data_vencimento=None
):
    # =========================
    # RENDA FIXA
    # =========================
    if categoria == "fixa":
        logger.info(f"📥 Iniciando cadastro de renda fixa para o usuário {usuario_id}: {ticker} - R${valor_investido}")
        db = SessionLocal()
        data_normalizada = normalizar_data_compra(data_compra)
        nome = ticker
        preco_compra = 1.0
        qtd = 1
        if valor_investido is None:
            valor_investido = 0.0

        nova_compra = Compra(
            usuario_id=usuario_id,  # ← Vincula a compra ao usuário
            ticker=ticker.upper(),
            nome=nome,
            tipo="fixa",
            categoria="fixa",
            tipo_renda_fixa=tipo_renda_fixa,
            plataforma=plataforma,
            quantidade=qtd,
            quantidade_original=qtd,
            quantidade_restante=qtd,
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
        logger.info(f"✅ Renda fixa salva no BD com ID: {nova_compra.id}")

        transacao = Transacao(
            usuario_id=usuario_id,  # ← Vincula a transação ao usuário
            tipo="compra",
            ticker=ticker.upper(),
            quantidade=qtd,
            preco=preco_compra,
            valor=valor_investido,
            status="success"
        )
        db.add(transacao)

        db.commit()
        db.refresh(nova_compra)
        logger.info(f"✅ Transação commitada para {ticker}")
        db.close()

        # Invalida apenas o cache deste usuário específico
        invalidate_cache(f"portfolio_completo_{usuario_id}")

        return {
            "mensagem": "Compra cadastrada com sucesso",
            "id": nova_compra.id
        }

    # =========================
    # RENDA VARIÁVEL OU CRIPTO
    # =========================
    logger.info(f"📥 Iniciando cadastro de {categoria} para o usuário {usuario_id}: {ticker} - {quantidade} un")
    db = SessionLocal()

    ticker = ticker.strip().upper()
    data_normalizada = normalizar_data_compra(data_compra)

    catalogo = buscar_ativo_catalogo(ticker)
    nome = catalogo.nome if catalogo else ticker

    tipo_busca = "cripto" if categoria == "cripto" else "acao"

    preco_compra = buscar_preco(tipo_busca, ticker, data_normalizada)
    logger.info(f"Preço encontrado: {preco_compra}")
    
    if preco_compra is None:
        logger.error(f"❌ Preço não encontrado para {ticker}")
        db.close()
        return {
            "erro": f"Não foi possível encontrar o preço de {ticker} na data {data_compra}. "
                    f"Verifique se a data está correta ou se o ativo existia nessa data."
        }
    
    if valor_investido is None:
        valor_investido = quantidade * preco_compra

    nova_compra = Compra(
        usuario_id=usuario_id,  # ← Vincula a compra ao usuário
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
    logger.info(f"✅ Compra salva no BD com ID: {nova_compra.id}")

    transacao = Transacao(
        usuario_id=usuario_id,  # ← Vincula a transação ao usuário
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
    logger.info(f"✅ Transação commitada para {ticker}")
    db.close()

    invalidate_cache(f"portfolio_completo_{usuario_id}")
    logger.info(f"✅ Cache do usuário {usuario_id} invalidado")

    return {
        "mensagem": "Compra cadastrada com sucesso",
        "id": nova_compra.id,
        "preco_compra": preco_compra,
        "data_utilizada": data_normalizada
    }


def remover_compra(compra_id: int, usuario_id: int):
    """Remove uma compra pelo ID, validando se pertence ao usuário correto"""
    db = SessionLocal()
    
    # CRÍTICO: Filtra pelo ID da compra E pelo ID do usuário proprietário
    compra = db.query(Compra).filter(Compra.id == compra_id, Compra.usuario_id == usuario_id).first()
    
    if not compra:
        db.close()
        return {"erro": "Compra não encontrada ou acesso não autorizado"}
    
    db.delete(compra)
    db.commit()
    db.close()
    
    invalidate_cache(f"portfolio_completo_{usuario_id}")
    
    return {"mensagem": "Compra removida com sucesso"}


def retirar_valor(usuario_id: int, ticker, quantidade):
    """Realiza retirada de um ativo garantindo o isolamento da conta"""
    db = SessionLocal()

    # CRÍTICO: Busca apenas as compras que pertencem ao usuário conectado
    compras = (
        db.query(Compra)
        .filter(
            Compra.usuario_id == usuario_id,
            Compra.ticker == ticker,
            Compra.quantidade_restante > 0
        )
        .order_by(Compra.data_compra.desc())
        .all()
    )

    if not compras:
        db.close()
        return {"erro": "Ativo não encontrado na carteira do usuário"}

    total_disponivel = sum(c.quantidade_restante for c in compras)

    if quantidade > total_disponivel:
        db.close()
        return {"erro": "Quantidade maior que disponível"}

    from services.price_service import buscar_preco
    tipo_ativo = compras[0].categoria if compras else "acao"
    tipo_busca = "cripto" if tipo_ativo == "cripto" else "acao"
    preco_atual = buscar_preco(tipo_busca, ticker, None)
    
    if preco_atual is None:
        db.close()
        return {"erro": "Não foi possível obter o preço atual do ativo"}

    valor_venda = quantidade * preco_atual

    # Corrigida variável 'quantité' com caractere especial para 'quantidade' para evitar NameError
    for compra in compras:
        proporcao = compra.quantidade_restante / total_disponivel
        retirar = int(quantidade * proporcao)
        retirar = min(retirar, compra.quantidade_restante)
        compra.quantidade_restante -= retirar
        quantidade -= retirar

    for compra in compras:
        if quantidade <= 0:
            break
        if compra.quantidade_restante > 0:
            retirar = min(quantidade, compra.quantidade_restante)
            compra.quantidade_restante -= retirar
            quantidade -= retirar

    transacao = Transacao(
        usuario_id=usuario_id,  # ← Vincula o histórico de venda ao usuário
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
    """Busca todas as compras de um ticker específico de um usuário determinado"""
    db = SessionLocal()
    
    # CRÍTICO: Filtrando pelo ticker e pelo usuario_id
    compras = (
        db.query(Compra)
        .filter(Compra.ticker == ticker.upper(), Compra.usuario_id == usuario_id)
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