import asyncio
from src.agent_base import BaseCryptoAgent
from src.moralis_client import fetch_token_price, fetch_token_metadata

class MoralisAgent(BaseCryptoAgent):
    """Агент, анализирующий данные из Moralis API"""

    token_address: str

    async def run(self):
        price_data = await fetch_token_price(self.token_address)
        metadata = await fetch_token_metadata(self.token_address)

        report = {
            "agent": self.name,
            "token": self.token_address,
            "usd_price": price_data.get("usdPrice", "Unknown"),
            "native_price": price_data.get("nativePrice", {}).get("value", "Unknown"),
            "market_cap": metadata.get("marketCap", "Unknown"),
            "volume_24h": metadata.get("volume24h", "Unknown"),
            "price_change_24h": metadata.get("priceChange24h", "Unknown"),
            "holders_count": metadata.get("holdersCount", "Unknown"),
            "liquidity": metadata.get("liquidity", "Unknown"),
        }

        print(f"📊 MoralisAgent Report: {report}")
        return report
