import httpx
from src.config import config

BASE_URL = "https://deep-index.moralis.io/api/v2.2"

HEADERS = {
    "X-API-Key": config.MORALIS_API_KEY,
    "accept": "application/json"
}


async def search_tokens(query: str) -> dict:
    url = f"{BASE_URL}/tokens/search"
    params = {"query": query}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_token_price(token_address: str, chain: str = "eth") -> dict:
    url = f"{BASE_URL}/erc20/{token_address}/price"
    params = {"chain": chain}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_wallet_balance(wallet_address: str, chain: str = "eth") -> dict:
    url = f"{BASE_URL}/{wallet_address}/balance"
    params = {"chain": chain}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_token_metadata(token_address: str, chain: str = "eth") -> dict:
    url = f"{BASE_URL}/erc20/{token_address}/metadata"
    params = {"chain": chain}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
