import logging
import json
from datetime import datetime, timezone
from src.utils.swarm_handler import SwarmHandler
from src.db.mongo_client import MongoDB

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    def __init__(self, token_results: list):
        """OrchestratorAgent aggregates token analyses and provides a final investment recommendation."""
        self.token_results = token_results
        self.swarm = SwarmHandler(
            agent_name="InvestmentOrchestrator",
            instructions="You are a cryptocurrency investment advisor. Analyze the given token reports, assess risks, and provide a clear final decision: 'BUY', 'HOLD', or 'AVOID'. Justify your reasoning with key insights.",
        )
        self.mongo_db = MongoDB()

    async def evaluate(self):
        """Runs the final evaluation using Swarm and saves it to MongoDB."""
        try:
            prompt = self._generate_prompt()
            decision_result = await self.swarm.run(prompt)

            logger.info(f"Final decision received: {decision_result}")

            # Ensure the decision result is parsed correctly
            parsed_decision = self._parse_decision_result(decision_result)
            if not parsed_decision:
                raise ValueError("Failed to parse decision_result, using default HOLD decision.")

            await self.mongo_db.save_report(self._prepare_report(parsed_decision))
            return parsed_decision

        except Exception as e:
            logger.error(f"Error in final evaluation: {e}", exc_info=True)
            return "Final evaluation failed."

    def _generate_prompt(self):
        """Generates a prompt for the final investment decision."""
        formatted_results = "\n\n".join(
            [f"Token: {token['symbol']} ({token['chainId']})\nAnalysis: {token['analysis']}" for token in
             self.token_results]
        )
        return (
            f"Here are multiple cryptocurrency analysis reports:\n\n{formatted_results}\n\n"
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
                # Clean the response by removing markdown code blocks
                decision_result = decision_result.strip().replace("```json", "").replace("```", "").strip()

                # Attempt to parse as JSON
                parsed_result = json.loads(decision_result)
                if isinstance(parsed_result, dict):
                    return parsed_result
                else:
                    logger.error(f"Unexpected JSON structure: {parsed_result}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse decision_result: {e}\nRaw response: {decision_result}")

        return {}  # Return an empty dict to prevent crashes

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
