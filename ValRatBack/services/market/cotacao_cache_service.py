# services/market/cotacao_cache_service.py

import logging
from datetime import date, datetime
from database import SessionLocal
from entities.cotacao_historica import CotacaoHistorica
from services.price_service import buscar_preco

logger = logging.getLogger(__name__)


def buscar_preco_com_cache(tipo: str, ticker: str, data_str: str = None):
    if not data_str:
        return buscar_preco(tipo, ticker, None)

    try:
        data_busca = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        return buscar_preco(tipo, ticker, data_str)

    if data_busca >= date.today():
        return buscar_preco(tipo, ticker, data_str)

    db = SessionLocal()
    try:
        cache_existente = db.query(CotacaoHistorica).filter(
            CotacaoHistorica.ticker == ticker,
            CotacaoHistorica.tipo == tipo,
            CotacaoHistorica.data == data_str
        ).first()

        if cache_existente:
            return cache_existente.preco

        preco = buscar_preco(tipo, ticker, data_str)

        if preco is not None:
            try:
                novo_cache = CotacaoHistorica(
                    ticker=ticker,
                    tipo=tipo,
                    data=data_str,
                    preco=float(preco)
                )
                db.add(novo_cache)
                db.commit()
            except Exception as e:
                logger.info(f"Cache de cotação não gravado (provável corrida): {ticker} {tipo} {data_str} -- {e}")
                db.rollback()

        return preco

    except Exception as e:
        logger.warning(f"⚠️ Erro ao consultar cache de cotação ({ticker}, {tipo}, {data_str}): {e}")
        db.rollback()
        return buscar_preco(tipo, ticker, data_str)
    finally:
        db.close()