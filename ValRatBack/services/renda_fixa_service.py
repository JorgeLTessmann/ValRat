from datetime import date
from database import SessionLocal
from entities.compra import Compra
from services.cache_service import invalidate_cache


def cadastrar_renda_fixa(
    nome_aplicacao: str,
    valor_aplicado: float,
    data_aplicacao: date,
    data_vencimento: date,
    tipo_ativo: str,
    indexador: str,
    taxa_contratada: float,
    tem_carencia: bool = False,
    data_carencia: date = None,
    plataforma: str = None
):
    """
    Cadastra um novo ativo de renda fixa no banco de dados.
    """
    db = SessionLocal()

    # Validações básicas
    if valor_aplicado <= 0:
        db.close()
        return {"erro": "Valor aplicado deve ser maior que zero"}

    if data_aplicacao >= data_vencimento:
        db.close()
        return {"erro": "Data de vencimento deve ser posterior à data de aplicação"}

    if tem_carencia and data_carencia is None:
        db.close()
        return {"erro": "Data de carência é obrigatória quando há carência"}

    if tem_carencia and data_carencia >= data_vencimento:
        db.close()
        return {"erro": "Data de carência deve ser anterior ao vencimento"}

    # Cria o registro com os nomes de campos CORRETOS
    nova_compra = Compra(
        nome_aplicacao=nome_aplicacao,
        valor_investido=valor_aplicado,  
        data_compra=data_aplicacao,      
        data_vencimento=data_vencimento,
        tem_carencia=tem_carencia,
        data_carencia=data_carencia,
        tipo_renda_fixa=tipo_ativo,      
        indexador=indexador,
        taxa_contratada=taxa_contratada,
        plataforma=plataforma,
        categoria="Renda Fixa"           
    )

    db.add(nova_compra)
    db.commit()
    db.refresh(nova_compra)
    db.close()

    # Invalida cache do portfólio
    invalidate_cache("portfolio_completo")

    return {
        "mensagem": "Renda fixa cadastrada com sucesso",
        "id": nova_compra.id
    }