from database import SessionLocal

from entities.renda_fixa import (
    RendaFixa
)


def cadastrar_renda_fixa(
    dados
):

    db = SessionLocal()

    nova_aplicacao = RendaFixa(

        nome=dados.nome,

        tipo=dados.tipo,

        indexador=dados.indexador,

        taxa=dados.taxa,

        valor_aplicado=dados.valor_aplicado,

        data_aplicacao=dados.data_aplicacao,

        data_vencimento=dados.data_vencimento,

        liquidez=dados.liquidez,

        emissor=dados.emissor,

        plataforma=dados.plataforma
    )

    db.add(nova_aplicacao)

    db.commit()

    db.refresh(nova_aplicacao)

    db.close()

    return {
        "mensagem":
        "Aplicação cadastrada"
    }