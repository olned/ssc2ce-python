from abc import ABC, abstractmethod


class IDeribitController(ABC):
    @abstractmethod
    async def handle_method_message(self, message: dict) -> None:
        pass

    @abstractmethod
    async def handle_error(self, message: dict) -> None:
        pass

    @abstractmethod
    async def handle_response(self, request_id: int, data: dict):
        pass
