from swarm import Agent
from abc import ABC, abstractmethod

class BaseCryptoAgent(Agent, ABC):
    """ Абстрактный класс агента для криптоанализа """

    @abstractmethod
    async def run(self):
        """Метод, который должен реализовать каждый агент"""
        pass
