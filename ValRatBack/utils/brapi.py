import requests
import os

from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv(
    "TOKEN_BRAPI"
)



def buscar_preco_atual(ticker):

    url = (
        f"https://brapi.dev/api/quote/"
        f"{ticker}"
        f"?token={TOKEN}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return None


    data = response.json()


    if not data["results"]:
        return None


    ativo = data["results"][0]

    return ativo[
        "regularMarketPrice"
    ]