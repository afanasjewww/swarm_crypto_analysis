import requests
import logging
from src.config import config
from src.utils.swarm_handler import SwarmHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class TAAPIAgent:
    def __init__(self, token_symbol: str):
        """Агент получает символ токена и запрашивает технические индикаторы с TAAPI.io."""
        self.token_symbol = token_symbol
        self.taapi_api_key = config.TAAPI_KEY
        self.taapi_base_url = "https://api.taapi.io"

        self.swarm = SwarmHandler(
            agent_name="TAAPIAgent",
            instructions="You are a technical analysis expert. Analyze the given cryptocurrency indicators (SMA, RSI) and provide insights on market trends."
        )

    def fetch_ta_indicators(self) -> dict:
        """Запрос технических индикаторов с TAAPI.io."""
        try:
            logger.info(f"Fetching TA indicators for {self.token_symbol}")

            params = {
                "secret": self.taapi_api_key,
                "exchange": "binance",
                "symbol": self.token_symbol,
                "interval": "1h",
                "optInTimePeriod": 14
            }

            sma_response = requests.get(f"{self.taapi_base_url}/sma", params=params)
            rsi_response = requests.get(f"{self.taapi_base_url}/rsi", params=params)

            sma = sma_response.json().get("value")
            rsi = rsi_response.json().get("value")

            logger.info(f"TA indicators for {self.token_symbol}: SMA={sma}, RSI={rsi}")

            return {"sma": sma, "rsi": rsi}
        except Exception as e:
            logger.error(f"Error fetching TA indicators: {e}")
            return {"error": str(e)}

    async def analyze(self):
        """Анализирует технические индикаторы с помощью Swarm AI."""
        ta_data = self.fetch_ta_indicators()

        prompt = f"""
            Cryptocurrency: {self.token_symbol}
            SMA (Simple Moving Average): {ta_data.get('sma', 'No data')}
            RSI (Relative Strength Index): {ta_data.get('rsi', 'No data')}

            Analyze these indicators and provide a short, actionable market insight.
        """

        return await self.swarm.run(prompt)
