# services/market/quotes_service.py

import os
import requests

from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TOKEN_BRAPI")


def buscar_quote(ticker):

    url = (
        "https://brapi.dev/api/quote/"
        f"{ticker}"
        f"?token={TOKEN}"
    )

    try:

        response = requests.get(
            url,
            timeout=15
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if not data.get("results"):
            return None

        return data["results"][0]

    except Exception:

        return None