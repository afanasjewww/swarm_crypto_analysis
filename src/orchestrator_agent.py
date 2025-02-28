import asyncio
from src.agent_base import BaseCryptoAgent
from src.moralis_agent import MoralisAgent
from src.taapi_agent import TAAPIAgent
from src.news_agent import NewsAgent

class OrchestratorAgent(BaseCryptoAgent):
    """Агент-оркестратор, который собирает данные и делает анализ"""

    async def run(self, token_info: dict):
        print(f"🚀 OrchestratorAgent запущен для {token_info['symbol']} ({token_info['token_address']})...")

        # Запуск агентов с передачей данных
        moralis_agent = MoralisAgent(name="MoralisAgent", token_info=token_info)
        taapi_agent = TAAPIAgent(name="TAAPIAgent", symbol=token_info["symbol"])
        news_agent = NewsAgent(name="NewsAgent", symbol=token_info["symbol"])

        moralis_result = await moralis_agent.run()
        taapi_result = await taapi_agent.run()
        news_result = await news_agent.run()

        # Анализ данных
        usd_price = float(moralis_result.get("usd_price", 0))
        rsi = float(taapi_result.get("rsi", 50))

        # Простая логика принятия решения (можно усложнить)
        action = "BUY" if usd_price < 1 and rsi < 30 else "HOLD"

        final_report = {
            "orchestrator": self.name,
            "moralis_analysis": moralis_result,
            "taapi_analysis": taapi_result,
            "news_analysis": news_result,
            "recommended_action": action,
        }

        print(f"📊 OrchestratorAgent Final Report: {final_report}")
        return final_report
