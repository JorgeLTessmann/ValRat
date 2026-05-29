from dotenv import load_dotenv
import os


load_dotenv()


TOKEN = os.getenv("TOKEN_BRAPI")

BASE_URL = (
    "https://brapi.dev/api/quote"
)

RANGE = "10y"

INTERVAL = "1d"