# services/renda_fixa_service.py

from datetime import date
from database import SessionLocal
from entities.compra import Compra
from services.cache_service import invalidate_cache


def cadastrar_renda_fixa(
    usuario_id: int,  # ← Adicionado para vinculação correta da conta
    nome_aplicacao: str,
    valor_applied: float,  # Mantendo o mapeamento interno original da sua função
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
    Cadastra um novo ativo de renda fixa no banco de dados vinculado a um usuário.
    """
    db = SessionLocal()

    # Validações básicas
    if valor_applied <= 0:
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

    # Cria o registro atrelando o usuario_id enviado pela API
    nova_compra = Compra(
        usuario_id=usuario_id,  # ← CRÍTICO: Isola o ativo para este usuário
        nome_aplicacao=nome_aplicacao,
        valor_investido=valor_applied,  
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

    # Invalida apenas o cache do portfólio deste usuário específico
    invalidate_cache(f"portfolio_completo_{usuario_id}")

    return {
        "mensagem": "Renda fixa cadastrada com sucesso",
        "id": nova_compra.id
    }