from database import SessionLocal

from entities.ativo_master import (
    AtivoMaster
)


# =========================
# BUSCAR POR CÓDIGO
# =========================

def buscar_ativo_catalogo(
    codigo: str
):

    db = SessionLocal()

    ativo = (
        db.query(AtivoMaster)
        .filter(
            AtivoMaster.codigo == codigo.upper()
        )
        .first()
    )

    db.close()

    return ativo


# =========================
# BUSCAR POR NOME
# =========================

def buscar_por_nome(
    nome: str
):

    db = SessionLocal()

    ativos = (
        db.query(AtivoMaster)
        .filter(
            AtivoMaster.nome.ilike(
                f"%{nome}%"
            )
        )
        .all()
    )

    db.close()

    return ativos


# =========================
# LISTAR POR TIPO
# =========================

def listar_por_tipo(
    tipo: str
):

    db = SessionLocal()

    ativos = (
        db.query(AtivoMaster)
        .filter(
            AtivoMaster.tipo == tipo
        )
        .all()
    )

    db.close()

    return ativos


# =========================
# CADASTRAR
# =========================

def cadastrar_ativo_catalogo(

    codigo,
    nome,
    tipo,

    instituicao=None,

    indexador=None,

    fonte=None,

    liquidez=None,

    tributacao=None,

    taxa=None,

    percentual_indexador=None,

    vencimento=None
):

    db = SessionLocal()

    existe = (
        db.query(AtivoMaster)
        .filter(
            AtivoMaster.codigo == codigo.upper()
        )
        .first()
    )

    if existe:

        db.close()

        return {
            "erro": "ativo já existe"
        }

    ativo = AtivoMaster(

        codigo=codigo.upper(),

        nome=nome,

        tipo=tipo,

        instituicao=instituicao,

        indexador=indexador,

        fonte=fonte,

        liquidez=liquidez,

        tributacao=tributacao,

        taxa=taxa,

        percentual_indexador=percentual_indexador,

        vencimento=vencimento
    )

    db.add(ativo)

    db.commit()

    db.refresh(ativo)

    db.close()

    return {

        "mensagem": "ativo cadastrado",

        "codigo": ativo.codigo
    }


# =========================
# AUTO COMPLETE
# =========================

def buscar_sugestoes(
    texto: str
):

    db = SessionLocal()

    ativos = (
        db.query(AtivoMaster)
        .filter(
            AtivoMaster.nome.ilike(
                f"%{texto}%"
            )
        )
        .limit(10)
        .all()
    )

    db.close()

    resultado = []

    for ativo in ativos:

        resultado.append({

            "codigo": ativo.codigo,

            "nome": ativo.nome,

            "tipo": ativo.tipo,

            "indexador": ativo.indexador,

            "taxa": ativo.taxa,

            "instituicao": ativo.instituicao
        })

    return resultado