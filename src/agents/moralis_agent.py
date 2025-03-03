from textwrap import dedent
from src.config import config
import logging
from src.utils.swarm_handler import SwarmHandler

logger = logging.getLogger(__name__)

class MoralisAgent:
    def __init__(self, token_info: dict):
        """Agent receives token data and processes it using Swarm."""
        self.token_info = token_info
        self.swarm = SwarmHandler(
            agent_name="CryptoAnalysisAgent",
            instructions="You are a cryptocurrency analyst. Analyze the given token data and provide a short but accurate summary, highlighting key risks and trends.",
        )

    async def analyze(self):
        """Runs token analysis through Swarm asynchronously."""
        try:
            prompt = self._generate_prompt()
            logger.info(f"Sending prompt to agent: {prompt}")
            result = await self.swarm.run(prompt)

            if not result:
                logger.warning(f"Empty analysis result for {self.token_info.get('symbol')}")
                return "Analysis not available."

            return result

        except Exception as e:
            logger.error(f"Error analyzing token {self.token_info.get('symbol')}: {e}", exc_info=True)
            return "Analysis error, data unavailable."

    def _generate_prompt(self):
        """Generates a well-formatted English-language prompt based on token data."""
        return dedent(f"""
            Token: {self.token_info.get('name')} ({self.token_info.get('symbol')})
            Price: {self.token_info.get('usdPrice')} USD
            Market Cap: {self.token_info.get('marketCap')} USD
            24h Price Change: {self.token_info.get('usdPricePercentChange', {}).get('oneDay', 'No data')}%
            24h Trading Volume: {self.token_info.get('volumeUsd', {}).get('oneDay', 'No data')} USD
            Security Score: {self.token_info.get('securityScore', 'No data')}/100

            Analyze this token and provide a summary of its reliability and future prospects.
            Highlight any risks or trends that should be considered.
        """).strip()
