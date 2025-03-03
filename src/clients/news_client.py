import httpx
from src.config import config

BASE_URL = "https://newsapi.org/v2/everything"

async def fetch_crypto_news(query: str) -> dict:
    params = {
        "q": query,
        "apiKey": config.NEWS_API_KEY,
        "sortBy": "publishedAt",
        "language": "en",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
