import asyncio
from src.agent_base import BaseCryptoAgent
from src.news_client import fetch_crypto_news

class NewsAgent(BaseCryptoAgent):
    """Агент для анализа новостей через NewsAPI"""

    async def run(self, token_symbol: str):
        news = await fetch_crypto_news(token_symbol)

        report = {
            "agent": self.name,
            "token": token_symbol,
            "top_headlines": news.get("articles", [])[:3],  # Топ 3 новости
        }

        print(f"📰 NewsAgent Report: {report}")
        return report
