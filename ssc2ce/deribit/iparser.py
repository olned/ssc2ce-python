from abc import ABC, abstractmethod


class IDeribitParser(ABC):
    @abstractmethod
    async def handle_message(self, message: str) -> None:
        pass
