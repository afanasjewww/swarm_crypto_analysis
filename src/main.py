import asyncio
from src.orchestrator_agent import OrchestratorAgent


async def main():
    orchestrator = OrchestratorAgent(name="Orchestrator")


    token_info = {
        "symbol": "BTC",
        "token_address": "0x12345",
        "chain_id": "eth",
        "usd_price": 45000,
        "market_cap": 900000000,
        "security_score": 95,
        "volume_24h": 50000000,
        "price_change_24h": -1.2,
        "liquidity_change_24h": -200000,
        "buyers_24h": 1000,
        "logo": "https://example.com/logo.png"
    }

    result = await orchestrator.run(token_info)
    print("✅ Полный анализ завершён:", result)


if __name__ == "__main__":
    asyncio.run(main())
