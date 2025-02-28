import httpx
from src.config import config

BASE_URL = "https://api.taapi.io"

async def fetch_technical_indicators(symbol: str) -> dict:
    url = f"{BASE_URL}/bulk"
    params = {
        "secret": config.TAAPI_KEY,
        "exchange": "binance",
        "symbol": symbol.upper() + "/USDT",
        "interval": "1d",
        "indicators": [
            {"indicator": "rsi"},
            {"indicator": "macd"},
            {"indicator": "sma"},
        ],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=params)
        response.raise_for_status()
        return response.json()
