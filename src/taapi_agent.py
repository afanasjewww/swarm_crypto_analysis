import asyncio
from src.agent_base import BaseCryptoAgent
from src.taapi_client import fetch_technical_indicators

class TAAPIAgent(BaseCryptoAgent):
    """Агент для анализа технических индикаторов через TAAPI.io API"""

    async def run(self, token_symbol: str):
        indicators = await fetch_technical_indicators(token_symbol)

        report = {
            "agent": self.name,
            "token": token_symbol,
            "rsi": indicators.get("rsi", "Unknown"),
            "macd": indicators.get("macd", "Unknown"),
            "sma": indicators.get("sma", "Unknown"),
        }

        print(f"📊 TAAPIAgent Report: {report}")
        return report
