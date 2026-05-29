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

from services.assets.asset_catalog_service import (
    cadastrar_ativo_catalogo
)


# =========================
# CDBS REAIS (exemplos)
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


# =========================
# LCI (ISENTA)
# =========================

cadastrar_ativo_catalogo(
    codigo="LCI_XP_92",
    nome="LCI XP 92% CDI",
    tipo="lci",
    indexador="CDI",
    taxa=92,
    instituicao="XP"
)


# =========================
# LCA (ISENTA)
# =========================

cadastrar_ativo_catalogo(
    codigo="LCA_BTG_93",
    nome="LCA BTG 93% CDI",
    tipo="lca",
    indexador="CDI",
    taxa=93,
    instituicao="BTG"
)


# =========================
# TESOURO DIRETO
# =========================

cadastrar_ativo_catalogo(
    codigo="TESOURO_IPCA_2035",
    nome="Tesouro IPCA+ 2035",
    tipo="tesouro",
    indexador="IPCA",
    taxa=6.45
)

cadastrar_ativo_catalogo(
    codigo="TESOURO_SELIC",
    nome="Tesouro Selic",
    tipo="tesouro",
    indexador="SELIC",
    taxa=0.10
)


print("✅ Catálogo populado com sucesso!")