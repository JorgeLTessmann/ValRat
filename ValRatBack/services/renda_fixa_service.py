# services/renda_fixa_service.py

from database import SessionLocal
from entities.renda_fixa import RendaFixa
from entities.transacao import Transacao
from services.cache_service import invalidate_cache


def cadastrar_renda_fixa(renda_fixa_model):
    """
    Cadastra um ativo de renda fixa.
    Valida indexador e taxa antes de salvar.
    """
    
    # =========================
    # VALIDAÇÃO
    # =========================
    if not renda_fixa_model.nome:
        return {"erro": "Nome do produto é obrigatório"}
        
    if not renda_fixa_model.indexador:
        return {"erro": "Indexador é obrigatório (CDI, IPCA, PRE)"}
    
    if renda_fixa_model.taxa is None or renda_fixa_model.taxa <= 0:
        return {"erro": f"Taxa inválida: {renda_fixa_model.taxa}. Use 100 para 100% do CDI, etc."}
    
    if renda_fixa_model.valor_aplicado is None or renda_fixa_model.valor_aplicado <= 0:
        return {"erro": "Valor aplicado é obrigatório"}
    # =========================
    # CADASTRO
    # =========================
    db = SessionLocal()
    
    nova_renda_fixa = RendaFixa(
        nome=renda_fixa_model.nome,
        tipo=renda_fixa_model.tipo,
        indexador=renda_fixa_model.indexador,
        taxa=renda_fixa_model.taxa,
        valor_aplicado=renda_fixa_model.valor_aplicado,
        data_aplicacao=renda_fixa_model.data_aplicacao,
        data_vencimento=renda_fixa_model.data_vencimento,
        liquidez=renda_fixa_model.liquidez,
        emissor=renda_fixa_model.emissor,
        plataforma=renda_fixa_model.plataforma
    )
    
    db.add(nova_renda_fixa)
    db.flush()
    
    # Cria transação associada
    transacao = Transacao(
        tipo="compra",
        ticker=renda_fixa_model.nome,
        quantidade=1,
        preco=renda_fixa_model.valor_aplicado,
        valor=renda_fixa_model.valor_aplicado,
        status="success"
    )

    if renda_fixa_model.taxa is None or renda_fixa_model.taxa <= 0:
        return {"erro": "Taxa inválida. Para CDB, use 100 para 100% do CDI, etc."}

    db.add(transacao)
    
    db.commit()
    db.refresh(nova_renda_fixa)
    db.close()
    
    # Invalida cache do portfolio
    invalidate_cache("portfolio_completo")
    
    return {
        "mensagem": "Renda fixa cadastrada com sucesso",
        "id": nova_renda_fixa.id
    }