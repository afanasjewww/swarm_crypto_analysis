import logging
import json
import asyncio
import time
from datetime import datetime, timezone
from src.utils.swarm_handler import SwarmHandler
from src.db.mongo_client import MongoDB
from src.agents.news_agent import NewsAgent

# Configure logging to include timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def __init__(self, token_results: list):
        """OrchestratorAgent aggregates token analyses and news summaries to provide a final investment recommendation."""
        self.token_results = token_results
        self.swarm = SwarmHandler(
            agent_name="InvestmentOrchestrator",
            instructions="You are a cryptocurrency investment advisor. Analyze the given token reports and news summaries, assess risks, and provide a clear final decision: 'BUY', 'HOLD', or 'AVOID'. Justify your reasoning with key insights.",
        )
        self.mongo_db = MongoDB()

    async def evaluate(self):
        """Runs evaluation using Swarm and saves it to MongoDB."""
        try:
            start_time = time.time()
            logger.info("🔍 Fetching news summaries for all tokens...")

            async def fetch_news_summary(token):
                news_agent = NewsAgent(token["symbol"])
                token["news_summary"] = await news_agent.summarize_news()
                if not token["news_summary"]:
                    logger.warning(f"⚠️ No news summary for {token['symbol']}")
                return token

            self.token_results = await asyncio.gather(*(fetch_news_summary(token) for token in self.token_results))

            logger.info("✅ All news summaries retrieved. Generating final investment decision...")

            prompt = self._generate_prompt()
            decision_result = await self.swarm.run(prompt)
            logger.info(f"📊 Final decision received: {decision_result}")

            parsed_decision = self._parse_decision_result(decision_result)
            if not parsed_decision:
                raise ValueError("⚠️ Failed to parse decision_result.")

            await self.mongo_db.save_report(self._prepare_report(parsed_decision))
            total_time = round(time.time() - start_time, 2)
            logger.info(f"✅ Final evaluation completed in {total_time}s")

            return parsed_decision

        except Exception as e:
            logger.error(f"❌ Error in final evaluation: {e}", exc_info=True)
            return "Final evaluation failed."

    def _generate_prompt(self):
        """Генерирует промпт для финального решения."""
        formatted_results = "\n\n".join(
            [
                f"Token: {token['symbol']} ({token['chainId']})\n"
                f"Analysis: {token.get('analysis', 'No analysis available')}\n"
                f"TAAPI Analysis: {token.get('taapi_analysis', 'No TA data available')}\n"
                f"News Summary: {token.get('news_summary', 'No news available')}"
                for token in self.token_results
            ]
        )
        return (
            f"Here are multiple cryptocurrency analysis reports with news summaries:\n\n{formatted_results}\n\n"
            "Based on these insights, provide a final decision for each token: "
            "Should an investor 'BUY', 'HOLD', or 'AVOID' these tokens? "
            "Return your response as a JSON object where each token's symbol is the key "
            "and the value is one of ['BUY', 'HOLD', 'AVOID']. No extra formatting, just raw JSON."
        )

    def _parse_decision_result(self, decision_result):
        """Parses the decision result into a dictionary format."""
        if isinstance(decision_result, dict):
            return decision_result

        if isinstance(decision_result, str):
            try:
                # Удаляем возможные код-блоки Markdown
                decision_result_cleaned = decision_result.strip().replace("```json", "").replace("```", "").strip()
                logger.info(
                    f"🔍 Parsing decision_result: {decision_result_cleaned[:500]}...")  # Логирование первых 500 символов

                # Пробуем распарсить JSON
                parsed_result = json.loads(decision_result_cleaned)
                if isinstance(parsed_result, dict):
                    return parsed_result
                else:
                    logger.error(f"⚠️ Unexpected JSON structure: {parsed_result}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse decision_result: {e}\nRaw response: {decision_result}")

        return {}  # Возвращаем пустой словарь вместо None

    def _prepare_report(self, decision_result):
        """Prepares the final report before saving to MongoDB."""
        report = {
            "date": datetime.now(timezone.utc).isoformat(),
            "tokens": []
        }

        for token in self.token_results:
            token_decision = decision_result.get(token["symbol"], "HOLD")  # Default to HOLD if missing
            token["final_decision"] = token_decision
            report["tokens"].append(token)

        return report
