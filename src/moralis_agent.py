import logging
from swarm import Swarm, Agent
import asyncio

logger = logging.getLogger(__name__)

class MoralisAgent:
    def __init__(self, token_info: dict):
        """Agent receives token data and processes it using Swarm."""
        self.token_info = token_info
        self.client = Swarm()  # Creating a Swarm client
        self.agent = Agent(
            name="CryptoAnalysisAgent",
            instructions="You are a cryptocurrency analyst. Analyze the given token data and provide a short but accurate summary, highlighting key risks and trends.",
        )

    async def analyze(self):
        """Runs token analysis through Swarm."""
        try:
            prompt = self._generate_prompt()
            logger.info(f"Sending prompt to agent: {prompt}")

            # Running analysis in a separate thread
            response = await asyncio.to_thread(self.client.run, self.agent, [{"role": "user", "content": prompt}])
            return response.messages[-1]["content"]  # Returning the last agent response

        except Exception as e:
            logger.error(f"Error analyzing token {self.token_info.get('symbol')}: {e}", exc_info=True)
            return "Analysis error, data unavailable."

    def _generate_prompt(self):
        """Generates an English-language prompt based on token data."""
        return (
            f"Token: {self.token_info.get('name')} ({self.token_info.get('symbol')})\n"
            f"Price: {self.token_info.get('usdPrice')} USD\n"
            f"Market Cap: {self.token_info.get('marketCap')} USD\n"
            f"24h Price Change: {self.token_info.get('usdPricePercentChange', {}).get('oneDay', 'No data')}%\n"
            f"24h Trading Volume: {self.token_info.get('volumeUsd', {}).get('oneDay', 'No data')} USD\n"
            f"Security Score: {self.token_info.get('securityScore', 'No data')}/100\n\n"
            f"Analyze this token and provide a summary of its reliability and future prospects. "
            f"Highlight any risks or trends that should be considered."
        )
