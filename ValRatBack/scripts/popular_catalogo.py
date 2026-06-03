# scripts/popular_catalogo.py

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from services.assets.asset_catalog_service import cadastrar_ativo_catalogo

# =========================
# CDBs do Usuário
# =========================

cadastrar_ativo_catalogo(
    codigo="CDB_INTER_110",
    nome="CDB Inter 110% CDI",
    tipo="cdb",
    indexador="CDI",
    taxa=110,
    instituicao="Inter"
)

cadastrar_ativo_catalogo(
    codigo="CDB_NUBANK_100",
    nome="CDB Nubank 100% CDI",
    tipo="cdb",
    indexador="CDI",
    taxa=100,
    instituicao="Nubank"
)

cadastrar_ativo_catalogo(
    codigo="CDB_BTG_105",
    nome="CDB BTG 105% CDI",
    tipo="cdb",
    indexador="CDI",
    taxa=105,
    instituicao="BTG"
)

print("✅ Catálogo de CDBs populado com sucesso!")