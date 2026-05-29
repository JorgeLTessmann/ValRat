# services/brapi_service.py

import requests
import os

from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TOKEN_BRAPI")


def buscar_ativo(ticker):

    url = (
        f"https://brapi.dev/api/quote/"
        f"{ticker}"
        f"?token={TOKEN}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    if not data.get("results"):
        return None

    return data["results"][0]


def buscar_historico_ibov():

    url = (
        "https://brapi.dev/api/quote/"
        "^BVSP"
        f"?token={TOKEN}"
    )

    response = requests.get(
        url,
        timeout=20
    )

    if response.status_code != 200:
        return None

    data = response.json()

    if not data.get("results"):
        return None

    return data["results"][0]