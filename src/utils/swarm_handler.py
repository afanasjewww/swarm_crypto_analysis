import asyncio
import logging
from swarm import Swarm, Agent

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SwarmHandler:
    def __init__(self, agent_name: str, instructions: str, model_override=None):
        """Initializes SwarmHandler with an optional model override."""
        self.client = Swarm()
        self.agent = Agent(name=agent_name, instructions=instructions)
        self.model_override = model_override

    async def run(self, prompt: str, context_variables=None):
        """Executes the agent with a given prompt, context variables, and model override."""
        try:
            if context_variables is None:
                context_variables = {}

            logger.info(f"Executing Swarm agent: {self.agent.name}")

            response = await asyncio.to_thread(
                lambda: self.client.run(
                    agent=self.agent,
                    messages=[{"role": "user", "content": prompt}],
                    context_variables=context_variables,
                    model_override=self.model_override,
                    max_turns=5
                )
            )

            last_message = response.messages[-1]["content"]
            logger.info(f"Swarm agent response: {last_message[:500]}...")  # Ограничение логов
            return last_message
        except Exception as e:
            logger.error(f"Swarm execution error for {self.agent.name}: {e}", exc_info=True)
            return "Analysis error, data unavailable."



# import asyncio
# import logging
# from swarm import Swarm, Agent
#
# logging.basicConfig(
#     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)
#
# class SwarmHandler:
#     def __init__(self, agent_name: str, instructions: str, model_override=None):
#         """Initializes SwarmHandler with an optional model override."""
#         self.client = Swarm()
#         self.agent = Agent(name=agent_name, instructions=instructions)
#         self.model_override = model_override  # Allow model customization
#
#     async def run(self, prompt: str, context_variables=None):
#         """Executes the agent with a given prompt, context variables, and model override."""
#         try:
#             if context_variables is None:
#                 context_variables = {}
#
#             logger.info(f"Executing Swarm agent: {self.agent.name}")
#
#             response = await asyncio.to_thread(
#                 self.client.run,
#                 agent=self.agent,
#                 messages=[{"role": "user", "content": prompt}],
#                 context_variables=context_variables,
#                 model_override=self.model_override,
#                 max_turns=3
#             )
#
#             return response.messages[-1]["content"]
#         except Exception as e:
#             logger.error(f"Swarm execution error for {self.agent.name}: {e}", exc_info=True)
#             return "Analysis error, data unavailable."
